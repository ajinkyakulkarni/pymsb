"""This module contains the interpreter that executes a list of Instructions created
by the Parser class."""

import tkinter as tk

import pymsb.language.abstractsyntaxtrees as ast
import pymsb.language.errors as errors
from pymsb.language.modules import *
from pymsb.language.parser import Parser


# TODO: address the following differences between MS Small Basic and Py_MSB:
# Storage of decimals/floats + precision level + what precision is based on (string length, actual bits)
# Setting invalid cursor locations; in MSB, this crashes the program

# FIXME: you can't run interpret_code twice with the same interpreter instance

# TODO: check if we're having blank/comment lines screwing up our line numbers between parser, interpreter
from pymsb.language.process import Process, ProcessBlock


class Interpreter:

    def __init__(self):
        self.parser = Parser()
        self.environment = Environment()
        self.current_statement_index = 0
        self.statements = []
        self.processes = []
        self.current_executing_process = None

        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        self.msb_objects = {
            "TextWindow": TextWindow(self, self.tk_root),
            "GraphicsWindow": GraphicsWindow(self, self.tk_root)
        }

    def interpret_code(self, code):
        # tk.Tk.mainloop blocks everything else, thankfully the code to run alongside is simple
        # noinspection PyAttributeOutsideInit
        self.statements = self.parser.parse(code + "\nTextWindow.Pause()")

        self.scan_code()

        self.processes.append(Process(0, self.statements))
        self.tk_root.after(1, self.execute_running_processes)
        self.tk_root.mainloop()

    def execute_running_processes(self):
        if not self.processes:
            return

        for p in self.processes:
            if p.state == Process.NORMAL:
                self.execute_next_instruction(p)
            if p.state == Process.WAITING:
                p.check_blocking()

        self.processes[:] = [p for p in self.processes if p.state != Process.FINISHED]

        self.tk_root.after(1, self.execute_running_processes)

    def execute_next_instruction(self, process):
        if process.line_number == len(process.statements):
            return

        self.current_executing_process = process
        statement = process.statements[process.line_number]

        try:
            if isinstance(statement, ast.Assignment):
                self.assign(statement.var, statement.val, statement.line_number)
            elif isinstance(statement, ast.MsbObjectFunctionCall):
                self.execute_function_call(statement.msb_object,
                                           statement.msb_object_function,
                                           statement.parameter_asts)
            elif isinstance(statement, ast.SubStatement):
                while not isinstance(process.statements[process.line_number], ast.EndSubStatement):
                    process.line_number += 1
            elif isinstance(statement, ast.SubroutineCall):
                process.sub_return_locations.append(process.line_number)
                process.line_number = self.environment.get_sub_location(statement.name)
            elif isinstance(statement, ast.EndSubStatement):
                process.line_number = process.sub_return_locations.pop()
            else:
                raise NotImplementedError(repr(statement))
        except ProcessBlock as e:
            self.processes.append(e.new_process)
            self.current_executing_process.set_blocking_process(e.new_process)
            return

        process.line_number += 1

    def exit(self):
        self.tk_root.destroy()

    def scan_code(self):
        line_num = 0

        while line_num < len(self.statements):
            stmt_ast = self.statements[line_num]

            # Subroutine stuff
            if isinstance(stmt_ast, ast.SubStatement):
                # Save this location, then skip until EndSub
                self.environment.bind_sub(stmt_ast.sub_name, line_num)
                while True:
                    line_num += 1
                    if line_num == len(self.statements):
                        raise errors.PyMsbSyntaxError(line_num, 0, "Expected EndSub here")
                    if isinstance(self.statements[line_num], ast.SubStatement):
                        raise errors.PyMsbSyntaxError(line_num, 0,
                                                      "A subroutine cannot be defined inside of another subroutine.")
                    if isinstance(self.statements[line_num], ast.EndSubStatement):
                        break

            elif isinstance(stmt_ast, ast.SubroutineCall):
                # A glorified GOTO TODO: implement GOTO as well
                pass

            line_num += 1

    def assign(self, destination_ast, value_ast, line_number=None):

        if isinstance(destination_ast, ast.UserVariable):
            if isinstance(value_ast, ast.UserVariable):
                if self.environment.is_subroutine(value_ast.variable_name):
                    raise errors.PyMsbSyntaxError(
                        line_number, 0,
                        "Subroutine '{0}' can only be assigned to an event.".format(value_ast.variable_name))
            self.environment.bind(destination_ast.variable_name, self.evaluate_expression_ast(value_ast))

        if isinstance(destination_ast, ast.UserVariableArrayAccess):
            return  # TODO: implement array support

        if isinstance(destination_ast, ast.MsbObjectField):
            self.assign_msb_object_field(destination_ast.msb_object,
                                         destination_ast.msb_object_field_name,
                                         self.evaluate_expression_ast(value_ast))

    def evaluate_expression_ast(self, val_ast):
        if isinstance(val_ast, ast.LiteralValue):
            return val_ast.value  # always a string
        if isinstance(val_ast, ast.UserVariable):
            return self.environment.get_variable(val_ast.variable_name)
        if isinstance(val_ast, ast.UserVariableArrayAccess):
            try:
                arr = self.to_dict(self.environment.get_variable(val_ast.variable_name))
                index = self.evaluate_expression_ast(val_ast.index_expr)
                return arr.get(index, "")
            except errors.PyMsbMalformedArrayError:
                return ""
        if isinstance(val_ast, ast.MsbObjectField):
            return self.evaluate_object_field(val_ast.msb_object, val_ast.msb_object_field_name)
        if isinstance(val_ast, ast.Operation):
            return self.apply_operation(val_ast.operator, val_ast.left, val_ast.right)
        if isinstance(val_ast, ast.MsbObjectFunctionCall):
            return self.execute_function_call(val_ast.msb_object,
                                              val_ast.msb_object_function,
                                              val_ast.parameter_asts)

        raise NotImplementedError(val_ast)

    def execute_function_call(self, obj_name, fn_name, arg_asts):
        arg_vals = [self.evaluate_expression_ast(arg_ast) for arg_ast in arg_asts]
        fn = getattr(self.msb_objects[utilities.capitalize(obj_name)], utilities.capitalize(fn_name))
        return fn.__call__(*arg_vals)

    def evaluate_object_field(self, obj_name, field_name):
        return getattr(self.msb_objects[obj_name], field_name)

    def assign_msb_object_field(self, obj_name, field_name, arg_value):
        return setattr(self.msb_objects[obj_name], field_name, arg_value)

    def apply_operation(self, op, left, right):
        def convert(x):
            try:
                return int(x)
            except ValueError:
                # Check if it's a "normal" base-10 number otherwise return the string if +, return 0 if not +
                try:
                    return float(x)  # FIXME: implement better checks so we don't accept the fancy floats like inf
                except ValueError:
                    if op == "+":
                        return x
                    return 0

        left = convert(self.evaluate_expression_ast(left))
        right = convert(self.evaluate_expression_ast(right))
        if op == "+":
            try:
                return left + right
            except TypeError:
                return str(left) + str(right)
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right

    def to_dict(self, dict_str):
        return {}


class Environment:
    def __init__(self):
        self.variable_bindings = {}
        self.label_bindings = {}

    def bind(self, var, val):
        self.variable_bindings[var.lower()] = val

    def get_variable(self, var):
        return self.variable_bindings.setdefault(var.lower(), "")

    def get_sub_location(self, sub_name):
        return self.label_bindings[sub_name.lower()]

    def is_array(self, var):
        return False  # TODO: implement Environment.is_array

    def bind_sub(self, sub_name, line_number):
        if sub_name.lower() in self.label_bindings:
            raise errors.PyMsbSyntaxError(
                line_number, 0, "Another Subroutine exists with the same name '{0}'".format(sub_name))
        self.label_bindings[sub_name.lower()] = line_number

    def is_subroutine(self, name):
        return name.lower() in self.label_bindings


if __name__ == "__main__":
    code3 = """
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    GraphicsWindow.Show()
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    'TextWindow.Clear()
    GraphicsWindow.Width = GraphicsWindow.Width * 2
    GraphicsWindow.Height = GraphicsWindow.Height * 2
    TextWindow.Top = TextWindow.Top + 200
    GraphicsWindow.Left = TextWindow.Left
    GraphicsWindow.Top = TextWindow.Top - GraphicsWindow.Height - 50
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    TextWindow.CursorTop = 0
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    TextWindow.Writeline("bam")
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    """

    sub_test = """
    TextWindow.WriteLine("Beginning")
    Sub helloworld
      TextWindow.WriteLine("Hello world!")
      sayGoodbye()
    EndSub
    TextWindow.WriteLine("Nice to meet you!")
    helloworld()
    TextWindow.WriteLine("cool!")
    sub saygoodbYE
      TextWindow.WriteLine("Goodbye world!")
    endsub
    TextWindow.WriteLine("What's your name?")
    TextWindow.WriteLine("Oh hello, " + TextWindow.Read() + "!  It's great to have input working!")
    TextWindow.Write("How old are you? ")
    age = TextWindow.readnumber()
    Textwindow.writELINe("So you'll be " + (age + 1) + " years old a year from now, congratulations.")
    TextWindow.Pause()
    TextWindow.Writeline("after a pause.")
    TextWindow.Pause()
    TextWindow.Writeline("this is after another pause.")
    """

    interpreter = Interpreter()
    interpreter.interpret_code(sub_test)
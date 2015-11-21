"""This module contains the interpreter that executes a list of Instructions created
by the Parser class."""
from ast import literal_eval

import tkinter as tk
import threading
import time

import pymsb.language.abstractsyntaxtrees as ast
import pymsb.language.errors as errors
from pymsb.language.modules import *
from pymsb.language.parser import Parser


# TODO: address the following differences between MS Small Basic and Py_MSB:
# Storage of decimals/floats + precision level + what precision is based on (string length, actual bits)
# Setting invalid cursor locations; in MSB, this crashes the program

# TODO: check if we're having blank/comment lines screwing up our line numbers between parser, interpreter


class Interpreter:
    def __init__(self):
        self.parser = Parser()
        self.environment = Environment()
        self.current_statement_index = 0
        self.statements = []
        self.sub_return_locations = []

    def __init_tk(self):
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        self.msb_objects = {
            "TextWindow": TextWindow(self, self.tk_root),
            "GraphicsWindow": GraphicsWindow(self, self.tk_root)
        }

        self.threads = []

    def run(self, code):
        self.__init_tk()

        self.statements = self.parser.parse(code + "\nTextWindow.Write(\"For now, use the close button to exit\")")
        self.scan_code()

        self.tk_root.after(1, self.start_main_thread)
        self.tk_root.mainloop()
        self.exit()

    def scan_code(self):
        line_num = 0

        while line_num < len(self.statements):
            stmt_ast = self.statements[line_num]

            # Subroutines - save starting line numbers for subroutines, then skip until EndSub
            if isinstance(stmt_ast, ast.SubStatement):
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

            # Labels - save line numbers for labels
            elif isinstance(stmt_ast, ast.LabelDefinition):
                self.environment.bind_label(stmt_ast.label_name, line_num)

            line_num += 1

    def start_main_thread(self):
        p = InterpreterThread(self, 0)
        self.threads.append(p)
        p.start()

    def exit(self):
        # TODO: add the logic regarding when to exit, when not to exit, and add TextWindow.PauseIfVisible() (I think?)
        # TODO: make this able to close all running interpreter threads
        self.tk_root.quit()

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
            # Check if this is a field or an event
            if utilities.msb_event_exists(destination_ast.msb_object,
                                          destination_ast.msb_object_field_name):
                # Must be assigning to a subroutine
                sub_name = value_ast.variable_name
                if self.environment.is_subroutine(sub_name):
                    self.assign_msb_event(destination_ast.msb_object,
                                          destination_ast.msb_object_field_name,
                                          sub_name)
            else:
                self.assign_msb_object_field(destination_ast.msb_object,
                                             destination_ast.msb_object_field_name,
                                             self.evaluate_expression_ast(value_ast))

    def evaluate_comparison_ast(self, val_ast):
        # Important - returns "True" or "False" if this is actually a comparison
        # Otherwise, evaluates as an expression and returns the string result (e.g. "10" or "concatstr")
        if isinstance(val_ast, ast.Comparison):
            return self.evaluate_comparison(val_ast.comparator, val_ast.left, val_ast.right)
        return self.evaluate_expression_ast(val_ast)

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
            return self.evaluate_operation(val_ast.operator, val_ast.left, val_ast.right)
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
        return getattr(self.msb_objects[utilities.capitalize(obj_name)], utilities.capitalize(field_name))

    def assign_msb_object_field(self, obj_name, field_name, arg_value):
        setattr(self.msb_objects[utilities.capitalize(obj_name)], utilities.capitalize(field_name), arg_value)

    def assign_msb_event(self, obj_name, event_name, sub_name):
        # TODO: implement the event things
        setattr(self.msb_objects[utilities.capitalize(obj_name)], utilities.capitalize(event_name), sub_name)

    def convert_string_value(self, x, force_numeric):
        try:
            return int(x)
        except (ValueError, OverflowError):
            # TODO: Check if it's a "normal" base-10 number otherwise return the string if +, return 0 if not +
            try:
                # FIXME: implement better checks so we don't accept the fancy floats like "inf"
                return float(x)
            except ValueError:
                if force_numeric:
                    return 0
                return x

    def evaluate_comparison(self, comp, left, right):
        # returns "True" or "False"
        # possible comp values <=, >=, <, >, <>, =

        left = self.evaluate_comparison_ast(left)
        right = self.evaluate_comparison_ast(right)
        if comp == "=":
            return str(left == right)
        if comp == "<>":
            return str(left != right)

        # At this point, anything that is non-numerical is treated like 0
        left = self.convert_string_value(left, True)
        right = self.convert_string_value(right, True)

        return str(((comp == "<" and left < right) or
                    (comp == "<=" and left <= right) or
                    (comp == ">" and left > right) or
                    (comp == ">=" and left >= right)))

    def evaluate_operation(self, op, left, right):
        left = self.evaluate_expression_ast(left)
        if isinstance(left, str):
            left = self.convert_string_value(left, op != "+")
        right = self.evaluate_expression_ast(right)
        if isinstance(right, str):
            right = self.convert_string_value(right, op != "+")

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


class Environment:
    def __init__(self):
        self.variable_bindings = {}
        self.sub_location_bindings = {}
        self.label_bindings = {}

    def bind(self, var, val):
        self.variable_bindings[var.lower()] = val

    def get_variable(self, var):
        return self.variable_bindings.setdefault(var.lower(), "")

    def get_sub_location(self, sub_name):
        return self.sub_location_bindings[sub_name.lower()]

    def get_label_location(self, label_name):
        return self.label_bindings[label_name.lower()]

    def is_subroutine(self, name):
        return name.lower() in self.sub_location_bindings

    def is_label(self, name):
        return name.lower() in self.label_bindings

    def is_array(self, var):
        return False  # TODO: implement Environment.is_array

    def bind_sub(self, sub_name, line_number):
        if sub_name.lower() in self.sub_location_bindings:
            raise errors.PyMsbSyntaxError(
                line_number, 0, "Another Subroutine exists with the same name '{0}'".format(sub_name))
        self.sub_location_bindings[sub_name.lower()] = line_number

    def bind_label(self, label_name, line_number):
        if label_name.lower() in self.label_bindings:
            raise errors.PyMsbSyntaxError(
                line_number, 0, "Another Label exists with the same name '{0}'".format(label_name))
        self.label_bindings[label_name.lower()] = line_number


class InterpreterThread(threading.Thread):
    def __init__(self, interpreter, line_number):
        super().__init__()
        self.interpreter = interpreter
        self.environment = interpreter.environment
        self.statements = interpreter.statements

        self.line_number = line_number
        self.sub_return_locations = [len(self.statements)]  # for handling subroutine calls

        self.daemon = True  # auto-exit when interpreter exits and main thread ends

    def run(self):
        while self.line_number is not None and 0 <= self.line_number < len(self.statements):
            self.execute_next_instruction()

    def execute_next_instruction(self):
        statement = self.statements[self.line_number]
        time.sleep(0.1)  # TODO: remove this, it's just an artificial slow-down

        if isinstance(statement, ast.Assignment):
            self.interpreter.assign(statement.var, statement.val, statement.line_number)

        elif isinstance(statement, ast.MsbObjectFunctionCall):
            self.interpreter.execute_function_call(statement.msb_object,
                                                   statement.msb_object_function,
                                                   statement.parameter_asts)

        elif isinstance(statement, ast.SubStatement):
            while not isinstance(self.statements[self.line_number], ast.EndSubStatement):
                self.line_number += 1

        elif isinstance(statement, ast.SubroutineCall):
            self.sub_return_locations.append(self.line_number)
            self.line_number = self.environment.get_sub_location(statement.name)

        elif isinstance(statement, ast.EndSubStatement):
            # first value in (last out) is line number out of range, so if we get to it,
            # it means we started this thread inside this sub call, so we are done this thread
            self.line_number = self.sub_return_locations.pop()

        elif isinstance(statement, ast.IfStatement):
            # If we have just reached an If, then check each branch of this if/elseif/else block until we
            # find a valid If/ElseIf branch or we reach Else/EndIf
            if statement.keyword == "If":
                while statement.keyword != "EndIf":
                    if statement.condition_expr is not None:
                        cond_val = self.interpreter.evaluate_comparison_ast(statement.condition_expr).lower() == "true"
                    else:
                        cond_val = True
                    if cond_val:
                        break  # let the interpreter continue on to the next line
                    else:
                        # Check the next branch
                        target = statement.jump_target
                        while self.statements[self.line_number] != target:
                            self.line_number += 1
                        statement = self.statements[self.line_number]
            else:
                # We have just finished an If/ElseIf block and have reached an ElseIf/Else block
                # Skip until reaching the EndIf
                while statement.keyword != "EndIf":
                    target = statement.jump_target
                    if target is None:
                        raise errors.PyMsbRuntimeError("Fatal error: " + repr(statement) + " has no jump target")
                    while self.statements[self.line_number] != target:
                        self.line_number += 1
                    statement = self.statements[self.line_number]

        elif isinstance(statement, ast.EndIfStatement):
            pass

        else:
            raise NotImplementedError(repr(statement))

        self.line_number += 1
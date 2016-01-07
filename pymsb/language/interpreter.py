import os
import tkinter as tk
import threading

import pymsb.language.abstractsyntaxtrees as ast
import pymsb.language.errors as errors
import pymsb.language.modules as modules
from pymsb.language.parser import Parser
from pymsb.language.arrayparser import ArrayParser

# TODO: address the following differences between MS Small Basic and Py_MSB:
# Storage of decimals/floats + precision level + what precision is based on (string length, actual bits)
# Setting invalid cursor locations; in MSB, this crashes the program
# When a number is represented with or without a decimal point

# TODO: check if we're having blank/comment lines screwing up our line numbers between parser, interpreter


class Interpreter:
    """This class is used to execute Microsoft Small Basic code."""
    def __init__(self):
        self.parser = Parser()
        self.environment = Environment()
        self.current_statement_index = 0
        self.statements = []
        self.sub_return_locations = []
        self.array_parser = ArrayParser()

        self.__program_path = None
        self.prog_args = []
        self.__subroutine_body_locations = {}

    def execute_code(self, code, args=None, program_path=None):
        """
        Executes the given Microsoft Small Basic code, given as a string.

        :param code: The string containing Microsoft Small Basic code.
        :param args: A list of arguments to the Microsoft Small Basic program.
        """
        self.__init_tk()

        if args is None:
            self.prog_args = []
        else:
            self.prog_args = args

        self.statements = self.parser.parse(code)
        if self.statements:
            self.__scan_statements()
            if program_path:
                self.__program_path = os.path.join(os.path.dirname(program_path), '')  # .join to ensure trailing slash
            else:
                self.__program_path = ""
            self.__tk_root.after(1, self.__start_main_thread)
            self.__tk_root.mainloop()
        self._exit()

    def execute_file(self, file_path, args=None):
        """
        Executes the given Microsoft Small Basic source code file.

        :param file_path: The string path to a Microsoft Small Basic source code file.
        :param args: A list of arguments to the Microsoft Small Basic program.
        """
        with open(file_path) as code_file:
            code = code_file.read()
            self.execute_code(code, args, code_file.name)

    @property
    def program_path(self):
        """Returns the path of the directory containing the currently executing script, or the empty string if there is
        no currently executing script or the script is being executed from a string."""
        return self.__program_path

    def __init_tk(self):
        self.__tk_root = tk.Tk()
        self.__tk_root.withdraw()
        self.msb_objects = {
            "Clock": modules.Clock(self),
            "Math": modules.Math(self),
            "TextWindow": modules.TextWindow(self, self.__tk_root),
            "GraphicsWindow": modules.GraphicsWindow(self, self.__tk_root),
            "Text": modules.Text(self),
            "Stack": modules.Stack(self),
            "Network": modules.Network(self),
            "File": modules.FileModule(self),
            "Desktop": modules.Desktop(self, self.__tk_root),
            "Array": modules.Array(self),
            "Program": modules.Program(self),
            "Timer": modules.Timer(self),
            "Mouse": modules.Mouse(self),
        }

        self.__threads = []

    def __scan_statements(self):
        # Save the line numbers for each subroutine body
        self.__subroutine_body_locations.clear()
        for line_number, statement in enumerate(self.statements):
            if isinstance(statement, ast.SubStatement):
                self.__subroutine_body_locations[statement.sub_name.lower()] = line_number + 1

    def __start_main_thread(self):
        p = InterpreterThread(self, 0)
        self.__threads.append(p)
        p.start()
        self.__tk_root.after(1, self.__check_threads_finished)

    def _call_subroutine_in_new_thread(self, sub_name):
        line_number = self.__subroutine_body_locations[sub_name.lower()]
        p = InterpreterThread(self, line_number)
        self.__threads.append(p)
        p.start()

    def __check_threads_finished(self):
        for thread in self.__threads[:]:
            if not thread.is_alive():
                self.__threads.remove(thread)
        if not self.__threads:
            if not (self.msb_objects["GraphicsWindow"].is_visible() or self.msb_objects["TextWindow"].is_visible()):
                self._exit()
        else:
            self.__tk_root.after(100, self.__check_threads_finished)

    def _exit(self, status=None):
        # TODO: make this able to close all running interpreter threads
        self.__tk_root.quit()
        self.__program_path = ""

    def _assign(self, destination_ast, value_ast, line_number=None):

        if isinstance(destination_ast, ast.UserVariable):
            # Assigning to variable as an array using one or more indices
            if destination_ast.array_indices:
                array_string = self.environment.get_variable(destination_ast.variable_name)
                index_values = [str(self._evaluate_expression_ast(index_ast)) for index_ast in destination_ast.array_indices]
                value = str(self._evaluate_expression_ast(value_ast))

                # TODO: raise error when trying to assign to a subroutine name or subroutine call.

                new_array_string = self.array_parser.set_value(array_string, index_values, value)
                self.environment.bind(destination_ast.variable_name, new_array_string)

            # Just overwriting variable
            else:
                self.environment.bind(destination_ast.variable_name, self._evaluate_expression_ast(value_ast))

        if isinstance(destination_ast, ast.MsbObjectField):
            msb_object = self.msb_objects[modules.utilities.capitalize(destination_ast.msb_object)]
            member_name = modules.utilities.capitalize(destination_ast.msb_object_field_name)

            # Determine if this is a function or an event
            info = modules.utilities.get_msb_builtin_info(destination_ast.msb_object, member_name)
            if info.type == "event":
                msb_object.set_event_sub(member_name, value_ast.variable_name)
            else:
                value = str(self._evaluate_expression_ast(value_ast))
                setattr(msb_object,
                        member_name,
                        value)

    def _increment_value(self, var_ast):
        # Increments the variable that has the given name by 1.  If not defined, this defines var_name to be 1.
        if isinstance(var_ast, ast.UserVariable):
            val = self._evaluate_operation("+", var_ast, ast.LiteralValue(1))
            self.environment.bind(var_ast.variable_name, val)
        else:
            raise errors.PyMsbRuntimeError(
                "Internal error - tried to increment non-UserVariable in Interpreter.increment_value")

    def _evaluate_comparison_ast(self, val_ast):
        # Important - returns "True" or "False" if this is actually a comparison
        # Otherwise, evaluates as an expression and returns the string result (e.g. "10" or "concatstr" or even "true")
        if isinstance(val_ast, ast.Comparison):
            return self._evaluate_comparison(val_ast.comparator, val_ast.left, val_ast.right)
        return self._evaluate_expression_ast(val_ast)

    def _evaluate_expression_ast(self, val_ast):
        if isinstance(val_ast, ast.LiteralValue):
            return val_ast.value  # always a string

        if isinstance(val_ast, ast.UserVariable):
            value = self.environment.get_variable(val_ast.variable_name)

            # If accessing variable as an array
            if val_ast.array_indices:
                index_values = [str(self._evaluate_expression_ast(i)) for i in val_ast.array_indices]
                return self.array_parser.get_value(value, index_values)

            # Just accessing variable
            return value

        if isinstance(val_ast, ast.MsbObjectField):
            return self._evaluate_object_field(val_ast.msb_object, val_ast.msb_object_field_name)

        if isinstance(val_ast, ast.Operation):
            return self._evaluate_operation(val_ast.operator, val_ast.left, val_ast.right)

        if isinstance(val_ast, ast.MsbObjectFunctionCall):
            return self._execute_function_call(val_ast.msb_object,
                                              val_ast.msb_object_function,
                                              val_ast.parameter_asts)

        raise NotImplementedError(val_ast)

    def _execute_function_call(self, obj_name, fn_name, arg_asts):
        arg_vals = [str(self._evaluate_expression_ast(arg_ast)) for arg_ast in arg_asts]
        fn = getattr(self.msb_objects[modules.utilities.capitalize(obj_name)], modules.utilities.capitalize(fn_name))
        return fn.__call__(*arg_vals)

    def _evaluate_object_field(self, obj_name, field_name):
        return getattr(self.msb_objects[modules.utilities.capitalize(obj_name)], modules.utilities.capitalize(field_name))

    def _evaluate_comparison(self, comp, left, right):
        # returns "True" or "False" - VERY IMPORTANT NOTE: returns the strings and not boolean values.
        # possible comp values are strings "<=", ">=", "<", ">", "<>", "="
        # left, right are asts

        left = self._evaluate_comparison_ast(left)
        right = self._evaluate_comparison_ast(right)
        if comp == "=":
            return str(left == right)
        if comp == "<>":
            return str(left != right)
        if comp.lower() == "and":
            return str(str(left).lower() == "true" and str(right).lower() == "true")
        if comp.lower() == "or":
            return str(str(left).lower() == "true" or str(right).lower() == "true")

        # At this point, anything that is non-numerical is treated like 0
        left = modules.utilities.numericize(left, True)
        right = modules.utilities.numericize(right, True)

        return str(((comp == "<" and left < right) or
                    (comp == "<=" and left <= right) or
                    (comp == ">" and left > right) or
                    (comp == ">=" and left >= right)))

    # FIXME: fix this so ("x is " + "00") returns "x is 00" and not "x is 0"
    def _evaluate_operation(self, op, left, right):
        # op is "+", "-", "*" or "/"
        # left, right are expression asts
        left = self._evaluate_expression_ast(left)
        if isinstance(left, str):
            left = modules.utilities.numericize(left, op != "+")
        right = self._evaluate_expression_ast(right)
        if isinstance(right, str):
            right = modules.utilities.numericize(right, op != "+")

        if op == "+":
            try:
                return str(left + right)
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

    def bind(self, var, val):
        self.variable_bindings[var.lower()] = val

    def get_variable(self, var):
        return self.variable_bindings.setdefault(var.lower(), "")


# noinspection PyProtectedMember
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
        # time.sleep(0.1)  # TODO: remove this, it's just an artificial slow-down

        if isinstance(statement, ast.Assignment):
            self.interpreter._assign(statement.var, statement.val, statement.line_number)

        elif isinstance(statement, ast.MsbObjectFunctionCall):
            self.interpreter._execute_function_call(statement.msb_object,
                                                   statement.msb_object_function,
                                                   statement.parameter_asts)

        elif isinstance(statement, ast.SubStatement):
            while not isinstance(self.statements[self.line_number], ast.EndSubStatement):
                self.line_number += 1

        elif isinstance(statement, ast.SubroutineCall):
            # Save the current line number, temporarily jump to the body of the called subroutine.
            self.sub_return_locations.append(self.line_number)
            self.line_number = self.statements.index(statement.jump_target)

        elif isinstance(statement, ast.EndSubStatement):
            # Return to where we were before calling the subroutine.
            # The first value in sub_return_locations is past the end of the program, so
            # if we call a subroutine as, say, part of Timer.Tick, the subroutine ending will terminate that
            # particular thread.
            self.line_number = self.sub_return_locations.pop()

        elif isinstance(statement, ast.IfStatement):
            # If we have just reached an If, then check each branch of this if/elseif/else block until we
            # find a valid If/ElseIf branch or we reach Else/EndIf
            if statement.keyword == "If":
                while statement.keyword != "EndIf":
                    if statement.condition_expr is not None:
                        cond_val = self.interpreter._evaluate_comparison_ast(statement.condition_expr).lower() == "true"
                    else:
                        cond_val = True
                    if cond_val:
                        break  # let the interpreter continue on to the next line
                    else:
                        # Check the next branch
                        while self.statements[self.line_number] != statement.jump_target:
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

        elif isinstance(statement, ast.ForStatement):
            # When we reach ForStatement, set the loop variable to the lower expression.
            # Do a one-time check if loop variable is greater than the upper expression.
            # Then advance; the matching EndForStatement handles the rest of the loop logic.
            self.interpreter._assign(statement.var_ast, statement.lower_expr)
            if self.interpreter._evaluate_comparison(">", statement.var_ast, statement.upper_expr) == "True":
                print("var: " + repr(statement.var_ast) + " is greater than " + repr(statement.upper_expr))
                self.line_number = self.statements.index(statement.jump_target)

        elif isinstance(statement, ast.EndForStatement):
            # When we reach EndForStatement, we always increment the variable.
            # If loop variable is greater than upper expression, advance to next line.  We always reevaluate upper expr.
            # Otherwise, increment loop variable and go to line immediately after the corresponding ForStatement
            for_ast = statement.jump_target
            self.interpreter._increment_value(for_ast.var_ast)
            if self.interpreter._evaluate_comparison(">", for_ast.var_ast, for_ast.upper_expr) == "True":
                pass
            else:
                self.line_number = self.statements.index(for_ast)  # line number gets incremented again after

        elif isinstance(statement, ast.WhileStatement):
            # If the expression evaluates to "true", continue execution, otherwise skip past EndWhile
            if self.interpreter._evaluate_comparison_ast(statement.condition_expr).lower() == "true":
                pass
            else:
                self.line_number = self.statements.index(statement.jump_target)

        elif isinstance(statement, ast.EndWhileStatement):
            # Jump back to the While
            self.line_number = self.statements.index(statement.jump_target)-1

        elif isinstance(statement, ast.LabelDefinition): pass  # all labels were parsed earlier

        elif isinstance(statement, ast.GotoStatement):
            self.line_number = self.statements.index(statement.jump_target)

        else:
            raise NotImplementedError(repr(statement))

        self.line_number += 1

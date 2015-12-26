from pymsb.language import errors
from pymsb.language.modules import utilities

# TODO: look over all of these and see if I want line_number and if I should change these asts up

class Statement:
    """ An AST representing a standalone instruction that can be executed."""
    def __init__(self, line_number):
        self.line_number = line_number

    @property
    def jump_target(self):
        # noinspection PyBroadException
        try:
            return self.__jump_target
        except:
            return None

    @jump_target.setter
    def jump_target(self, x):
        # noinspection PyAttributeOutsideInit
        self.__jump_target = x


class Assignment(Statement):
    """ An AST representing an assignment to a named variable or MsbObjectField on the left-hand side,
    using the value obtained by evaluating the right-hand side.
    """
    def __init__(self, line_number, var, val):
        super().__init__(line_number)
        self.var = var
        self.val = val

        if isinstance(var, MsbObjectField):
            # Check for read-only status
            if var.read_only:
                raise errors.PyMsbSyntaxError(
                    "The property '{0}' in '{1}' is read-only and cannot be assigned a value."
                    .format(var.msb_object_field_name, var.msb_object))

    def __repr__(self):
        return "Assignment{{{0} = {1}}}".format(self.var, self.val)


class UserVariable:
    """ An AST representing a reference to a user-defined variable. """

    def __init__(self, variable_name):
        super().__init__()
        self.variable_name = variable_name

    def __repr__(self):
        return "UserVariable<{0}>".format(self.variable_name)


class LiteralValue:
    """ An AST representing a literal value in Microsoft Small Basic (e.g. "Hello world!" or 10).

    Note that internally, all Microsoft Small Basic values are just strings.
    """

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return "Literal<{0}>".format(self.value)


class UserVariableArrayAccess:
    """ An AST representing an array indexing access operation """
    def __init__(self, variable_name, index_expr):
        super().__init__()
        self.variable_name = variable_name
        self.index_expr = index_expr

    def __repr__(self):
        return "ArrayAccess<{0}[{1}]>".format(self.variable_name, repr(self.index_expr))


class MsbObjectField:
    """ An AST representing a reference to a built-in Microsoft Small Basic object field.
    """
    # TODO: implement the read-only check
    def __init__(self, msb_object, msb_object_field_name, read_only=False):
        super().__init__()
        self.msb_object = msb_object
        self.msb_object_field_name = msb_object_field_name
        self.read_only = read_only

    def __repr__(self):
        return "MsbObjectField<{0}.{1}>".format(self.msb_object, self.msb_object_field_name)


class MsbObjectFunctionCall(Statement):
    """ An AST representing a call to a built-in function in Microsoft Small Basic.
    """

    def __init__(self, line_number, msb_object, msb_object_function, parameter_asts):
        super().__init__(line_number)
        self.msb_object = msb_object
        self.msb_object_function = msb_object_function
        self.parameter_asts = parameter_asts

        # Check for existence of function and correct number of arguments
        num_args = utilities.get_msb_method_args(msb_object, msb_object_function)
        if num_args is None:
            raise errors.PyMsbRuntimeError("{0} not in {1}".format(msb_object_function,
                                                                   msb_object))
        if num_args != len(parameter_asts):
            raise errors.PyMsbRuntimeError(
                "Operation '{0}.{1}' is supplied {2} arguments, but takes {3} arguments."
                .format(msb_object, msb_object_function, len(parameter_asts), num_args))

    def __repr__(self):
        s = ",".join(map(repr, self.parameter_asts))
        return "MsbObjectFunctionCall<{0}.{1}({2})>".format(self.msb_object,
                                                            self.msb_object_function,
                                                            s)


class LabelDefinition(Statement):
    """ An AST representing a label definition line """

    def __init__(self, line_number, label_name):
        super().__init__(line_number)
        self.line_number = line_number
        self.label_name = label_name


class GotoStatement(Statement):
    """ An AST representing a Goto statement """

    def __init__(self, line_number, label_name):
        super().__init__(line_number)
        self.line_number = line_number
        self.label_name = label_name


class SubroutineCall(Statement):
    """ An AST representing a call to a Microsoft Small Basic subroutine (syntactic sugar for goto).
    """

    def __init__(self, line_number, name):
        super().__init__(line_number)
        self.name = name


class Operation:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return "(" + repr(self.left) + self.operator + repr(self.right) + ")"


class Comparison:
    def __init__(self, comparator, left, right):
        self.comparator = comparator
        self.left = left
        self.right = right

    def __repr__(self):
        return "(" + repr(self.left) + " " + self.comparator + " " + repr(self.right) + ")"


class KeywordStatement(Statement):
    """ An AST representing a keyword expression. """
    def __init__(self, line_number, keyword):
        super().__init__(line_number)
        self.keyword = keyword

    def __repr__(self):
        return "{0}Statement<>".format(self.keyword)


class IfStatement(KeywordStatement):
    """ Represents an if statement (just the if statement, not the body of the statement)
        Keyword must be one of If, ElseIf, Else.  """
    def __init__(self, line_number, if_keyword, condition_expr):
        super().__init__(line_number, if_keyword)
        self.condition_expr = condition_expr

    def __repr__(self):
        return "IfStatement[{0}]{1}".format(self.keyword, self.condition_expr)


class EndIfStatement(KeywordStatement):
    def __init__(self, line_number):
        super().__init__(line_number, "EndIf")


class WhileStatement(KeywordStatement):
    """ Represents a while statement (just the while statement, not the body of the loop) """
    def __init__(self, line_number, condition_expr):
        super().__init__(line_number, "While")
        self.condition_expr = condition_expr

    def __repr__(self):
        return "WhileStatement<{0}>".format(self.condition_expr)


class EndWhileStatement(KeywordStatement):
    def __init__(self, line_number):
        super().__init__(line_number, "EndWhile")


class ForStatement(KeywordStatement):
    """ Represents a for statement (just the for statement, not the body of the loop) """
    def __init__(self, line_number, var_ast, lower_expr, upper_expr):
        super().__init__(line_number, "For")
        self.var_ast = var_ast
        self.lower_expr = lower_expr
        self.upper_expr = upper_expr

    def __repr__(self):
        return "ForStatement<{0}...{1}>".format(self.lower_expr, self.upper_expr)


class EndForStatement(KeywordStatement):
    def __init__(self, line_number):
        super().__init__(line_number, "EndFor")


class SubStatement(KeywordStatement):
    """ An AST representing a Subroutine definition line (just the Sub statement, not the body of the subroutine) """

    def __init__(self, line_number, sub_name):
        super().__init__(line_number, "Sub")
        self.sub_name = sub_name
        self.line_number = line_number

    def __repr__(self):
        return "SubStatement<{0}>".format(self.sub_name)


class EndSubStatement(KeywordStatement):
    def __init__(self, line_number):
        super().__init__(line_number, "EndSub")


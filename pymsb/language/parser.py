from collections import OrderedDict
from pymsb.language import abstractsyntaxtrees as ast
import pymsb.language.errors as errors
import re

# TODO: describe errors that may be raised


class Parser:
    """
    The Parser converts multi-line strings containing Microsoft Small Basic code into ASTs representing instructions for
    the Interpreter.
    """

    def __init__(self):
        self.line_number = -1
        self.token_index = -1
        self.tokens = []
        self.line = ""

    def parse(self, code):
        """
        Consumes a single multiline string containing Microsoft Small Basic code.
        If no syntax errors are detected, this returns a list of ASTs representing instructions for the Interpreter.
        If syntax errors are detected, this outputs to stdout and returns None.

        :param code: A multiline string containing Microsoft Small Basic code.
        :return: A list of abstractsyntaxtrees.Statement instances, or None.
        """
        asts = []

        # This keeps track of what code blocks are "open" right now in the current part of the code
        # noinspection PyAttributeOutsideInit
        self.open_code_block_asts = []

        error_list = []

        lines = code.splitlines()
        for self.line_number, self.line in enumerate(lines):
            try:
                ast = self.__parse_tokens(self.tokenize(self.line))
            except errors.PyMsbSyntaxError as e:
                error_list.append(e)
                continue
            if ast:
                asts.append(ast)

        # If we didn't close our code blocks
        if self.open_code_block_asts:
            # TODO: give detailed output of what we're missing
            message = "Missing the closing for " + repr(self.open_code_block_asts[-1])
            error_list.append(errors.PyMsbExpectedExpressionError(self.line_number, message))

        # Perform checks and processing for labels
        try:
            self.__scan_for_labels_and_subroutines(asts)
        except errors.PyMsbSyntaxError as e:
            error_list.append(e)

        # No issues detected during parsing
        if not error_list:
            return asts

        # If there were errors detected, print in user-friendly format and return None.
        for error in error_list:
            print(lines[error.line_number])
            print(' '*error.line_index + '^')
            print("\t", error, "\n")
        return None

    def tokenize(self, line, include_comments=False):
        """
        Takes a single line of MSB and generates a list of MsbToken instances.

        :param line: A single-line string of MSB code.
        :param include_comments: If true, then comments are included as MsbToken instances of type MsbToken.COMMENT.
        :return: A list of MsbToken instances representing the given line of code.
        """
        self.tokens = []
        line_tokenizing = line.lstrip()
        while line_tokenizing:
            line_index = len(line) - len(line_tokenizing)
            for token_type, regex in MsbToken.regexes.items():
                match = re.match(regex, line_tokenizing, re.IGNORECASE)
                if match:
                    if token_type != MsbToken.COMMENT or include_comments:
                        self.tokens.append(MsbToken(token_type,
                                                    match.group(),
                                                    self.line_number,
                                                    line_index))
                    line_tokenizing = line_tokenizing[match.end():].lstrip()
                    break
            else:
                self.tokens.append(MsbToken.generate_unexpected_token(line_tokenizing, self.line_number, line_index))
                break
        return self.tokens

    def __get_token(self, token_index_offset, *expected_types):
        """
        Attempts to return the MsbToken located at the current index (self.token_index) plus token_index.  If this is
        out of bounds, or the type of the token does not match the expected types, then one of PyMsbExpectedTokenError
        or PyMsbUnexpectedTokenError are raised.

        :param token_index_offset: The number of tokens ahead to read from the current value of self.token_index.
        :param expected_types: If non-empty, then the list of MsbToken types to allow (i.e. not raise an exception for).
                               If empty, then all token types are allowable.
                               If (and only if) None is in expected_types, then None will be returned if no token was
                               found at the given offset from self.token_index rather than PyMsbExpectedTokenError.
        :return: The MsbToken at the given offset from self.token_index, or None if out of bounds and None is in
                 expected_types.
        """
        index = self.token_index + token_index_offset

        # Past end of the line; either silently return None if None is expected or raise PyMsbExpectedTokenError
        if index >= len(self.tokens):
            if None in expected_types:
                return None
            line_index = self.tokens[-1].line_index_end
            raise errors.PyMsbExpectedTokenError(self.line_number, line_index, *expected_types)

        if expected_types and self.tokens[index].token_type not in expected_types:
            raise errors.PyMsbUnexpectedTokenError(self.tokens[index])
        return self.tokens[index]

    def __parse_arg_exprs(self):
        """
        Helper function to parse the arguments in a call to an MSB built-in function, where self.token_index is
        immediately after the open left parenthesis.

        :return: A list of ASTs representing the arguments for an MSB built-in function.
        """
        arg_asts = []
        while True:
            expr_ast = self.__parse_expr(MsbToken.R_PARENS, MsbToken.COMMA, allow_empty=True)
            if expr_ast is None:
                return []
            arg_asts.append(expr_ast)
            next_token = self.__get_token(-1, MsbToken.R_PARENS, MsbToken.COMMA)
            if next_token.token_type == MsbToken.R_PARENS:
                return arg_asts

    def __parse_expr(self, *closing_braces, allow_comparators=False, allow_empty=False):
        """
        Helper function to parse the operands and operators in an expression, starting from self.token_index.
        :param closing_braces: The list of token types that can terminate the current expression.  If None is in
                               closing_braces, then encountering EOL can terminate the current expression.
        :param allow_comparators: If true, then comparators like =, < and "and" can be used in place of operators.
        :param allow_empty: If true, then an empty expression is valid.
        :return: An AST representing this expression.
        """
        # FIXME: "and" and "or" are not supported yet.

        if not closing_braces:
            closing_braces = (None,)

        # Catch the case of empty expression - examples:
        # a =
        # b = 20 * ()
        if not allow_empty:
            if self.token_index < len(self.tokens) and self.tokens[self.token_index].token_type in closing_braces:
                raise errors.PyMsbExpectedExpressionError(self.line_number, self.__get_token(0).line_index)

        # Process into list of alternating operand asts and operator self.tokens, then consider order of precedence
        expr_elements = []
        while True:
            # loop until we get to a closing brace/bracket/blank space (at this level of nesting)
            # Find operand
            t = self.__get_token(0, MsbToken.LITERAL, MsbToken.L_PARENS, MsbToken.SYMBOL, MsbToken.COMMA,
                                 *closing_braces)

            if not t:
                break
            if t.token_type in closing_braces:
                self.token_index += 1
                break

            # Start a nested expression
            if t.token_type == MsbToken.L_PARENS:
                self.token_index += 1
                opd = self.__parse_expr(MsbToken.R_PARENS, allow_comparators=allow_comparators)

            # The literal is the entire operand
            elif t.token_type == MsbToken.LITERAL:
                self.token_index += 1
                # Either no surrounding double quotes, or double quotes on both end
                v = t.value
                if v[0] == "\"":
                    v = v[1:]
                if v[-1] == "\"":
                    v = v[:-1]
                opd = ast.LiteralValue(v)

            # Determine what this symbol represents
            elif t.token_type == MsbToken.SYMBOL:

                # either a built-in object field, or a built-in object function call, or a user variable
                t2 = self.__get_token(1, MsbToken.DOT, MsbToken.OPERATOR, MsbToken.COMPARATOR, MsbToken.EQUALS,
                                      MsbToken.L_PARENS, MsbToken.L_BRACKET, *closing_braces)

                # just a user-defined variable.
                if ((not t2) or
                        (t2.token_type in closing_braces) or
                        (t2.token_type in (MsbToken.OPERATOR, MsbToken.EQUALS, MsbToken.COMPARATOR))):
                    opd = ast.UserVariable(t.value)
                    self.token_index += 1

                # Access to an array index
                elif t2.token_type == MsbToken.L_BRACKET:
                    self.token_index += 2  # pass the symbol and the L_BRACKET
                    array_index_asts = []
                    while True:  # Look for potentially multiple [index] in a row
                        array_index_ast = self.__parse_expr(MsbToken.R_BRACKET)
                        array_index_asts.append(array_index_ast)
                        # After this expression, there is either another index [, an operator, or EOL.
                        if self.token_index >= len(self.tokens):
                            break
                        if self.tokens[self.token_index].token_type != MsbToken.L_BRACKET:
                            break
                        self.token_index += 1

                    opd = ast.UserVariable(t.value, array_index_asts)

                # Is a built-in of some kind.  Check if fn call, or to-in field value access, or invalid
                elif t2.token_type == MsbToken.DOT:
                    field_token = self.__get_token(2, MsbToken.SYMBOL)
                    action_token = self.__get_token(3, MsbToken.L_PARENS, MsbToken.OPERATOR, *closing_braces)

                    # fn call
                    if action_token is not None and action_token.token_type == MsbToken.L_PARENS:
                        self.token_index += 4
                        arg_asts = self.__parse_arg_exprs()
                        opd = ast.MsbObjectFunctionCall(self.line_number, t.value, field_token.value, arg_asts)

                    # built-in field value
                    else:
                        self.token_index += 3
                        opd = ast.MsbObjectField(t.value, field_token.value)

            # noinspection PyUnboundLocalVariable
            expr_elements.append(opd)

            # Find operator (maybe comparator) after the operand, or end of the expression
            if allow_comparators:
                t = self.__get_token(0, MsbToken.OPERATOR, MsbToken.COMPARATOR, MsbToken.EQUALS, MsbToken.COMMA,
                                     *closing_braces)
            else:
                t = self.__get_token(0, MsbToken.OPERATOR, MsbToken.COMMA, *closing_braces)

            if not t:
                break
            self.token_index += 1

            if t.token_type in closing_braces:
                break
            else:
                expr_elements.append(t.value)

        # Process into nested expression asts
        op_precedences = list("*/+-")
        if allow_comparators:
            op_precedences += ["<", "<=", "=", ">=", ">", "<>"]
        for op_finding in op_precedences:
            while op_finding in expr_elements:
                ind2 = expr_elements.index(op_finding)
                left = expr_elements[ind2-1]
                right = expr_elements[ind2+1]
                if op_finding in "*/+-":
                    expr_elements[ind2-1] = ast.Operation(op_finding, left, right)
                else:
                    expr_elements[ind2-1] = ast.Comparison(op_finding, left, right)
                del expr_elements[ind2]
                del expr_elements[ind2]

        if expr_elements:
            return expr_elements[0]
        return None

    def __parse_keyword_statement(self):
        """
        Helper function to parse a statement beginning with If, For, While, etc.

        :return: An AST representing the current statement being parsed.
        """

        def assert_open_code_block(*open_code_block_keywords):
            """
            Raises errors.PyMsbUnexpectedTokenError iff the current open block isn't one of the given types.

            :param open_code_block_keywords: The type(s) of open code blocks that are allowed.
            :raise errors.PyMsbUnexpectedTokenError: If current open code block is not one of the given types.
            """
            if open_block_keyword not in open_code_block_keywords:
                raise errors.PyMsbUnexpectedTokenError(kw_token)
                # raise errors.PyMsbExpectedTokenError(self.line_number, 0, *open_code_block_keywords)

        kw_token = self.__get_token(0)
        open_block_keyword = self.open_code_block_asts[-1].keyword if self.open_code_block_asts else None

        # ==========================================================================================
        # IFS
        if kw_token.token_type in ("If", "ElseIf", "Else"):
            # Check previous token type
            if kw_token.token_type in ("ElseIf", "Else"):
                assert_open_code_block("If", "ElseIf", "Else")

            # Parse conditional expression
            if kw_token.token_type != "Else":
                self.token_index += 1
                conditional_expr = self.__parse_expr("Then", allow_comparators=True)
            else:
                conditional_expr = None

            answer = ast.IfStatement(self.line_number, kw_token.token_type, conditional_expr)

            # Link previous If/ElseIf/Else to this ElseIf/Else
            if kw_token.token_type in ("ElseIf", "Else"):
                self.open_code_block_asts.pop().jump_target = answer

            self.open_code_block_asts.append(answer)
            return answer

        if kw_token.token_type == "EndIf":
            assert_open_code_block("If", "ElseIf", "Else")
            # Link previous If/ElseIf/Else to this ElseIf/Else
            answer = ast.EndIfStatement(self.line_number)
            self.open_code_block_asts.pop().jump_target = answer
            return answer

        # ==========================================================================================
        # FOR
        if kw_token.token_type == "For":
            var = self.__get_token(1, MsbToken.SYMBOL).value
            var_ast = ast.UserVariable(var)  # note, in MSB "For array[0] = 1 to 10" is not valid
            self.__get_token(2, MsbToken.EQUALS)
            self.token_index += 3
            lower_expr = self.__parse_expr("To")  # remember to match capitalization in MsbToken.keywords
            upper_expr = self.__parse_expr()
            answer = ast.ForStatement(self.line_number, var_ast, lower_expr, upper_expr)
            self.open_code_block_asts.append(answer)
            return answer

        if kw_token.token_type == "EndFor":
            # Link the for and endfor asts together
            assert_open_code_block("For")
            answer = ast.EndForStatement(self.line_number)
            for_ast = self.open_code_block_asts.pop()
            for_ast.jump_target = answer
            answer.jump_target = for_ast
            return answer

        # ==========================================================================================
        # WHILE
        if kw_token.token_type == "While":
            self.token_index += 1
            conditional_expr = self.__parse_expr(allow_comparators=True)
            answer = ast.WhileStatement(self.line_number, conditional_expr)
            self.open_code_block_asts.append(answer)
            return answer

        if kw_token.token_type == "EndWhile":
            assert_open_code_block("While")
            answer = ast.EndWhileStatement(self.line_number)
            while_ast = self.open_code_block_asts.pop()
            while_ast.jump_target = answer
            answer.jump_target = while_ast
            return answer

        # ==========================================================================================
        # SUB
        # TODO: make this use something similar to what the ifs are using or at least have the right checks
        # TODO: check if the above TODO has been fulfilled
        if kw_token.token_type == "Sub":
            sub_name = self.__get_token(1, MsbToken.SYMBOL).value
            self.__get_token(2, None)
            answer = ast.SubStatement(self.line_number, sub_name)
            self.open_code_block_asts.append(answer)
            return answer

        if kw_token.token_type == "EndSub":
            self.__get_token(1, None)
            assert_open_code_block("Sub")
            self.open_code_block_asts.pop()
            return ast.EndSubStatement(self.line_number)

        # ==========================================================================================
        # GOTO
        if kw_token.token_type == "Goto":
            label_name = self.__get_token(1, MsbToken.SYMBOL).value
            self.__get_token(2, None)
            return ast.GotoStatement(self.line_number, label_name)

    def __parse_tokens(self, tokens):
        """
        Parses a tokenized line of Microsoft Small Basic code.

        :param tokens: A list of MsbToken instances that composes a single line of code in Microsoft Small Basic.
        :return: A single AST representing this line of Microsoft Small Basic code.
        """
        if not tokens:
            return None

        self.tokens = tokens
        self.token_index = 0

        # Special handling for keywords
        if self.tokens[0].is_keyword():
            return self.__parse_keyword_statement()

        self.__get_token(0, MsbToken.SYMBOL)

        # Use the second token to find the type of the overall symbol we're operating on
        t = self.__get_token(1, None, MsbToken.DOT, MsbToken.L_BRACKET, MsbToken.EQUALS, MsbToken.COLON,
                             MsbToken.L_PARENS)

        if not t:
            raise errors.PyMsbUnrecognizedStatementError(self.line_number, 0)

        # label_name: (should have nothing after the colon)
        elif t.token_type == MsbToken.COLON:
            self.__get_token(2, None)
            return ast.LabelDefinition(self.line_number, self.tokens[0].value)

        # SYMBOL DOT SYMBOL - a built-in
        elif t.token_type == MsbToken.DOT:
            obj = self.__get_token(0)
            field = self.__get_token(2, MsbToken.SYMBOL)

            # Verify that this is an assignment to a field/event, or is a built-in function call
            self.__get_token(3, MsbToken.L_PARENS, MsbToken.EQUALS)

            # Function call, with variable number of arguments
            if self.tokens[3].token_type == MsbToken.L_PARENS:
                self.token_index = 4
                arg_asts = self.__parse_arg_exprs()
                answer = ast.MsbObjectFunctionCall(self.line_number, obj.value, field.value, arg_asts)

            # Is assignment to a built-in MSB object field.
            else:
                self.token_index = 4
                expr_ast = self.__parse_expr()
                answer = ast.Assignment(self.line_number, ast.MsbObjectField(obj.value, field.value), expr_ast)

            # Should have no more tokens
            self.__get_token(0, None)
            return answer

        # Assignment to a user-defined array value
        elif t.token_type == MsbToken.L_BRACKET:
            self.token_index += 2
            array_index_asts = []
            while True:  # Look for potentially multiple [index] in a row
                array_index_ast = self.__parse_expr(MsbToken.R_BRACKET)
                array_index_asts.append(array_index_ast)
                # After this expression, there is either another index or an equal sign
                l_bracket_or_equals_token = self.__get_token(0, MsbToken.EQUALS, MsbToken.L_BRACKET)
                self.token_index += 1
                if l_bracket_or_equals_token.token_type == MsbToken.EQUALS:
                    break

            array_access_ast = ast.UserVariable(tokens[0].value, array_index_asts)
            val_ast = self.__parse_expr()
            return ast.Assignment(self.line_number, array_access_ast, val_ast)

        # Assignment to a user-defined variable
        elif t.token_type == MsbToken.EQUALS:
            self.token_index += 2
            val_ast = self.__parse_expr()
            return ast.Assignment(self.line_number, ast.UserVariable(self.tokens[0].value), val_ast)

        # Call to user-defined subroutine
        elif t.token_type == MsbToken.L_PARENS:
            self.__get_token(2, MsbToken.R_PARENS)
            self.__get_token(3, None)
            return ast.SubroutineCall(self.line_number, self.tokens[0].value)

        # Because of self.get_token(self.tokens,  parameter restrictions, this line shouldn't be reached.
        raise errors.PyMsbUnrecognizedStatementError(self.line_number, 0)

    def __scan_for_labels_and_subroutines(self, asts):
        """
        Helper function to scan for duplicate/missing labels/subroutines and store their line numbers.
        :param asts: A list of ASTs representing the parsed program.
        :return: None
        """
        label_asts = dict()
        sub_asts = dict()

        # Save label/sub locations
        for line_num, stmt_ast in enumerate(asts):
            if isinstance(stmt_ast, ast.LabelDefinition):
                name = stmt_ast.label_name
                if name in label_asts:
                    raise errors.PyMsbSyntaxError(line_num, 0,
                                                  "Another Label exists with the same name '{0}'.".format(name))
                else:
                    label_asts[name] = stmt_ast

            if isinstance(stmt_ast, ast.SubStatement):
                name = stmt_ast.sub_name
                if name in sub_asts:
                    raise errors.PyMsbSyntaxError(line_num, 0,
                                                  "Another Subroutine exists with the same name '{0}'.".format(name))
                else:
                    sub_asts[name] = stmt_ast

        # Check gotos and sub calls
        for line_num, stmt_ast in enumerate(asts):
            if isinstance(stmt_ast, ast.GotoStatement):
                name = stmt_ast.label_name
                if name not in label_asts:
                    raise errors.PyMsbSyntaxError(line_num, 0,
                                                  "Cannot find label '{0}' used in Goto statement.".format(name))
                else:
                    stmt_ast.jump_target = label_asts[name]

            if isinstance(stmt_ast, ast.SubroutineCall):
                name = stmt_ast.name
                if name not in sub_asts:
                    raise errors.PyMsbSyntaxError(line_num, 0,
                                                  "Subroutine '{0}' is not defined.".format(name))
                else:
                    stmt_ast.jump_target = sub_asts[name]


class MsbToken:  # TODO:
    """
    For internal use in Parser, in the tokenization process that happens before the tokens are parsed into statements.
    :param token_type: One of the static members defined below.
    :param value:
    :param line_number:
    :param line_index:
    """
    COMMENT = "a comment"
    SYMBOL = "a variable or an object"
    LITERAL = "a number or a string"
    L_PARENS = "("
    R_PARENS = ")"
    L_BRACKET = "["
    R_BRACKET = "]"
    DOT = "."
    COMMA = ","
    COLON = ":"
    COMPARATOR = "<=, >=, <, >, <>"
    OPERATOR = "+, -, *, /"
    EQUALS = "="  # Note: EQUALS can be assignment or comparator based on context, but token_type will always be EQUALS.

    keywords = {"If", "ElseIf", "Else", "EndIf", "Then",
                "While", "EndWhile",
                "For", "EndFor", "To",
                "Sub", "EndSub",
                "Goto",
                "Step"}
    # for kw in keywords:
    #    setattr(MsbToken, kw.toupper(), kw)  FIXME: figure out how to set these constants without getting too hacky

    # TODO: decide if OrderedDict will be necessary in the end
    regexes = OrderedDict()

    for kw in keywords:  # Make each keyword a reserved keyword
        regexes[kw] = kw + "(?!\w)"
    regexes[L_PARENS] = "\("
    regexes[R_PARENS] = "\)"
    regexes[L_BRACKET] = "\["
    regexes[R_BRACKET] = "]"
    regexes[SYMBOL] = "[a-zA-Z_]\w*"
    # Notes on literals: strings have no escape codes.  Multiple leading "-" in numeric literals are ok.
    regexes[LITERAL] = ("-*\d+[.]?\d*"
                        "|"
                        "\".*?(\"|$)"  # for some reason, if end of line before closing quote, is ok.
                        "|"
                        "-*\d*[.]?\d+|\".*?\"")  # can have leading dot or trailing dot but not both
    regexes[DOT] = "\."
    regexes[COMMA] = ","
    regexes[COLON] = ":"
    regexes[COMPARATOR] = "<=|>=|<>|<|>"
    regexes[EQUALS] = "="
    regexes[OPERATOR] = "[-#+*/]"
    regexes[COMMENT] = "'.*"

    UNEXPECTED_TOKEN = "unexpected token"

    def __init__(self, token_type, value, line_number, line_index):
        self.token_type = token_type
        self.value = value
        self.line_number = line_number
        self.line_index = line_index
        self.line_index_end = line_index + len(value)

    def __str__(self):
        if self.token_type == self.OPERATOR:
            return "operator<" + self.value + ">"
        return self.token_type + "<" + self.value + ">"

    def __repr__(self):
        return self.__str__()  # TODO: implement __repr__ for MsbToken, determine if

    def is_keyword(self):
        # TODO: decide on capitalization of internal constants
        for k in self.keywords:
            if k.lower() == self.value.lower():
                return True
        return False

    @classmethod
    def generate_unexpected_token(cls, value, line_number, line_index):
        return MsbToken(cls.UNEXPECTED_TOKEN, value, line_number, line_index)

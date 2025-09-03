"""
Numeric expression parser

parser = NumericParser()
parser.eval("2 * 15 / 22")
"""
from typing import List

from pyparsing import (
    Literal,
    Word,
    Combine,
    Group,
    Optional,
    ZeroOrMore,
    Forward,
    nums,
    alphas,
    Regex,
    oneOf,
    QuotedString,
)
import operator


# Most of this code comes from the fourFn.py pyparsing example
# https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py
class NumericStringParser:
    """
    Parse a string containing numeric expression

    The string can contain brace vars, like in :
      {fu bar} + {zu}
    """

    def push_first(self, strg, loc, toks):
        self.expr_stack.append(toks[0])

    def push_u_minus(self, strg, loc, toks):
        if toks and toks[0] == "-":
            self.expr_stack.append("unary -")

    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        brace_var :: '{' .+ '}'
        atom    :: real | fn '(' expr ')' | '(' expr ')' | variable
        term    :: atom [ multop atom ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        fnumber = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
        # Limitation, there is no way to escape a brace
        brace_var = QuotedString(
            quote_char="{",
            end_quote_char="}",
            unquote_results=False,
        )
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expr = Forward()
        atom = (
            (
                Optional(oneOf("- +"))
                + (ident + lpar + expr + rpar | fnumber | brace_var).set_parse_action(
                    self.push_first
                )
            )
            | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
        ).set_parse_action(self.push_u_minus)

        term = atom + ZeroOrMore((multop + atom).set_parse_action(self.push_first))
        expr << term + ZeroOrMore((addop + term).set_parse_action(self.push_first))
        self.bnf = expr

    def parse(self, num_string, parse_all=True):
        self.expr_stack = []
        self.bnf.parseString(num_string, parse_all)
        return self.expr_stack[:]


class NumericStringFloatReducer:
    """
    Reduce a parsed numeric string to a float value

    By doing the math!

    Expects input in the format of NumericStringParser output.

    Eg: transforms ["1.2", "+", "1"] to 2.2

    Does *not* support brace vars (eg: ["1.2" + "{fubar}])
    """

    functions = {
        "abs": abs,
        "trunc": lambda a: int(a),
        "round": round,
    }

    operators = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    @classmethod
    def reduce(cls, stack: List[str]) -> float:
        """

        :param stack: example : ["1.2", "+", "1"]
        :return: the result of the computation
        """
        op = stack.pop()
        if op == "unary -":
            return -cls.reduce(stack)
        if op in "+-*/":
            op2 = cls.reduce(stack)
            op1 = cls.reduce(stack)
            return cls.operators[op](op1, op2)
        elif op in cls.functions:
            return cls.functions[op](cls.reduce(stack))
        elif op.startswith("{"):
            raise SyntaxError  # brace vars
        else:
            return float(op)

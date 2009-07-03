"""
Fortran code printer

The FCodePrinter converts single sympy expressions into single Fortran
expressions, using the functions defined in the Fortran 77 standard where
possible. Some useful pointers to Fortran can be found on wikipedia:

http://en.wikipedia.org/wiki/Fortran

Most of the code below is based on the "Professional Programmer\'s Guide to
Fortran77" by Clive G. Page:

http://www.star.le.ac.uk/~cgp/prof77.html

Fortran is a case-insensitive language. This might cause trouble because sympy
is case sensitive. The implementation below does not care and leaves the
responsibility for generating properly cased Fortran code to the user.
"""


from str import StrPrinter
from sympy.printing.precedence import precedence
from sympy.core import S, Add, I
from sympy.core.numbers import NumberSymbol
from sympy.functions import sin, cos, tan, asin, acos, atan, atan2, sinh, \
    cosh, tanh, sqrt, log, exp, abs, sign, conjugate, Piecewise
from sympy.utilities.iterables import postorder_traversal


implicit_functions = {
    sin: "sin",
    cos: "cos",
    tan: "tan",
    asin: "asin",
    acos: "acos",
    atan: "atan",
    atan2: "atan2",
    sinh: "sinh",
    cosh: "cosh",
    tanh: "tanh",
    sqrt: "sqrt",
    log: "log",
    exp: "exp",
    abs: "abs",
    sign: "sign",
    conjugate: "conjg",
}


class FCodePrinter(StrPrinter):
    """A printer to convert sympy expressions to strings of Fortran code"""
    printmethod = "_fcode_"

    def doprint(self, expr):
        """Returns Fortran code for expr (as a string)"""
        lines = []
        if isinstance(expr, Piecewise):
            # support for top-level Piecewise function
            for i, (e, c) in enumerate(expr.args):
                if i == 0:
                    lines.append("if (%s) then" % self._print(c))
                elif i == len(expr.args)-1 and c == True:
                    lines.append("else")
                else:
                    lines.append("else if (%s) then" % self._print(c))
                if self._settings["assign_to"] is None:
                    lines.append("  %s" % self._print(e))
                else:
                    lines.append("  %s = %s" % (self._settings["assign_to"], self._print(e)))
            lines.append("end if")
        else:
            line = StrPrinter.doprint(self, expr)
            # turn the result into an assignment
            if self._settings["assign_to"] is not None:
                line = "%s = %s" % (self._settings["assign_to"], line)
            lines.append(line)
        # good old fortran line wrapping ;-)
        wrapped_lines = []
        for line in lines:
            hunk = line[:66]
            line = line[66:]
            wrapped_lines.append("      %s" % hunk)
            while len(line) > 0:
                hunk = line[:62]
                line = line[62:]
                wrapped_lines.append("     @    %s" % hunk)
        return "\n".join(wrapped_lines)

    def _print_Add(self, expr):
        # purpose: print complex numbers nicely in Fortran.
        # collect the purely real and purely imaginary parts:
        pure_real = []
        pure_imaginary = []
        mixed = []
        for arg in expr.args:
            if arg.is_real and arg.is_number:
                pure_real.append(arg)
            elif arg.is_imaginary and arg.is_number:
                pure_imaginary.append(arg)
            else:
                mixed.append(arg)
        if len(pure_imaginary) > 0:
            if len(mixed) > 0:
                PREC = precedence(expr)
                term = Add(*mixed)
                t = self._print(term)
                if t.startswith('-'):
                    sign = "-"
                    t = t[1:]
                else:
                    sign = "+"
                if precedence(term) < PREC:
                    t = "(%s)" % t

                return "cmplx(%s,%s) %s %s" % (
                    self._print(Add(*pure_real)),
                    self._print(-I*Add(*pure_imaginary)),
                    sign, t,
                )
            else:
                return "cmplx(%s,%s)" % (
                    self._print(Add(*pure_real)),
                    self._print(-I*Add(*pure_imaginary)),
                )
        else:
            return StrPrinter._print_Add(self, expr)

    def _print_Function(self, expr):
        name = self._settings["user_functions"].get(expr.__class__)
        if name is None:
            name = implicit_functions.get(expr.__class__)
        if name is None:
            name = expr.func.__name__
        return "%s(%s)" % (name, self.stringify(expr.args, ", "))

    _print_Factorial = _print_Function

    def _print_ImaginaryUnit(self, expr):
        # purpose: print complex numbers nicely in Fortran.
        return "cmplx(0,1)"

    def _print_int(self, expr):
        return str(expr)

    def _print_Mul(self, expr):
        # purpose: print complex numbers nicely in Fortran.
        if expr.is_imaginary and expr.is_number:
            return "cmplx(0,%s)" % (
                self._print(-I*expr)
            )
        else:
            return StrPrinter._print_Mul(self, expr)

    def _print_NumberSymbol(self, expr):
        # Standard Fortran has no predefined constants. Therefor NumerSymbols
        # are evaluated.
        return str(expr)

    _print_Catalan = _print_NumberSymbol
    _print_EulerGamma = _print_NumberSymbol
    _print_Exp1 = _print_NumberSymbol
    _print_GoldenRatio = _print_NumberSymbol
    _print_Pi = _print_NumberSymbol

    def _print_Pow(self, expr):
        PREC = precedence(expr)
        if expr.exp is S.NegativeOne:
            return '1.0/%s'%(self.parenthesize(expr.base, PREC))
        elif expr.exp == 0.5:
            return 'sqrt(%s)' % self._print(expr.base)
        else:
            return StrPrinter._print_Pow(self, expr)

    def _print_Rational(self, expr):
        p, q = int(expr.p), int(expr.q)
        return '%d.0/%d.0' % (p, q)


class StrictFCodePrinter(FCodePrinter):
    """A printer to convert sympy expressions to strings of working Fortran code"""

    def emptyPrinter(self, expr):
        raise NotImplementedError("Can not print as Fortran code: %s" % expr)

    # the following can not be simply translated into Fortran.
    _print_Basic = emptyPrinter
    _print_ComplexInfinity = emptyPrinter
    _print_Derivative = emptyPrinter
    _print_dict = emptyPrinter
    _print_Dummy = emptyPrinter
    _print_ExprCondPair = emptyPrinter
    _print_GeometryEntity = emptyPrinter
    _print_Infinity = emptyPrinter
    _print_Integral = emptyPrinter
    _print_Interval = emptyPrinter
    _print_Limit = emptyPrinter
    _print_list = emptyPrinter
    _print_Matrix = emptyPrinter
    _print_DeferredVector = emptyPrinter
    _print_NaN = emptyPrinter
    _print_NegativeInfinity = emptyPrinter
    _print_Normal = emptyPrinter
    _print_Order = emptyPrinter
    _print_PDF = emptyPrinter
    _print_Relational = emptyPrinter
    _print_RootOf = emptyPrinter
    _print_RootsOf = emptyPrinter
    _print_RootSum = emptyPrinter
    _print_Sample = emptyPrinter
    _print_SMatrix = emptyPrinter
    _print_tuple = emptyPrinter
    _print_Uniform = emptyPrinter
    _print_Unit = emptyPrinter
    _print_Wild = emptyPrinter
    _print_WildFunction = emptyPrinter

    def _print_Function(self, expr):
        name = self._settings["user_functions"].get(expr.__class__)
        if name is None:
            name = implicit_functions.get(expr.__class__)
        if name is None:
            raise NotImplementedError("Function not available in Fortran: %s" % expr)
        else:
            return "%s(%s)" % (name, self.stringify(expr.args, ", "))

    _print_Factorial = _print_Function


def fcode(expr, assign_to=None, precision=15, user_functions={}, strict=False, human=True):
    """Converts an expr to a string of Fortran 77 code

       Arguments:
         expr  --  a sympy expression to be converted

       Optional arguments:
         assign_to  --  When given, the argument is used as the name of the
                        variable to which the fortran expression is assigned.
                        (This is helpfull in case of line-wrapping.)
         precision  --  the precission for numbers such as pi [default=15]
         user_functions  --  A dictionary where keys are FuncionClass instances
                             and values are there string representations.
         strict  --  If True, an error is raised if the generated code is not
                     compilable (without making assumptions about the presence
                     of non-standard Fortran functions). [default=False]
         human  --  If True, the result is a single string that may contain
                    some PARAMETER statements for the numer symbols. If
                    False, the same information is returned in a more
                    programmer-friendly data structure.

       >>> from sympy import *
       >>> x, tau = symbols(["x", "tau"])
       >>> fcode((2*tau)**Rational(7,2))
       '      8*sqrt(2)*tau**(7.0/2.0)'
       >>> fcode(sin(x), assign_to="s")
       '      s = sin(x)'
       >>> print fcode(pi)
             parameter (pi = 3.14159265358979)
             pi

    """
    # find all number symbols
    number_symbols = set([])
    for sub in postorder_traversal(expr):
        if isinstance(sub, NumberSymbol):
            number_symbols.add(sub)
    number_symbols = [(str(ns), ns.evalf(precision)) for ns in sorted(number_symbols)]
    # run the printer
    profile = {
        "full_prec": False, # programmers don't care about trailing zeros.
        "assign_to": assign_to,
        "user_functions": user_functions,
    }
    if strict:
        result = StrictFCodePrinter(profile).doprint(expr)
    else:
        result = FCodePrinter(profile).doprint(expr)
    if human:
        result = "".join(
            "      parameter (%s = %s)\n" % (name, value) for name, value in number_symbols
        ) + result
        return result
    else:
        return number_symbols, result


def print_fcode(expr, assign_to=None, precision=15, user_functions={}, strict=False):
    """Prints the Fortran representation of the given expression.

       See fcode for the meaning of the optional arguments.
    """
    print fcode(expr, assign_to, precision, user_functions, strict)


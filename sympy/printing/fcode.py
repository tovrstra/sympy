"""
Fortran code printer

The FCodePrinter converts single sympy expressions into single Fortran
expressions, using the functions defined in the Fortran 77 standard where
possible. Some useful pointers to Fortran can be found on wikipedia:

http://en.wikipedia.org/wiki/Fortran

Most of the code below is based on the "Professional Programmer's Guide to
Fortran77" by Clive G. Page:

http://www.star.le.ac.uk/~cgp/prof77.html

Fortran is a case-insensitive language. This might cause trouble because sympy
is case sensitive. The implementation below does not care and leaves the
responsibility for generating properly cased Fortran code to the user.
"""


from str import StrPrinter
from sympy.printing.precedence import precedence
from sympy.core import S, Add, I
from sympy.functions import sin, cos, tan, asin, acos, atan, atan2, sinh, \
    cosh, tanh, sqrt, log, exp, abs, sign, conjugate


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
    """A printer to convert python expressions to strings of Fortran code"""
    printmethod = "_fcode_"

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
        if len(pure_real) > 0 or len(pure_imaginary) > 0:
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
        name = implicit_functions.get(expr.__class__)
        if name is None:
            name = expr.func.__name__
        return "%s(%s)" % (name, self.stringify(expr.args, ", "))

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
        return str(expr.evalf(self._settings["precision"]))

    _print_Catalan = _print_NumberSymbol
    _print_EulerGamma = _print_NumberSymbol
    _print_Exp1 = _print_NumberSymbol
    _print_GoldenRatio = _print_NumberSymbol
    _print_Pi = _print_NumberSymbol

    def _print_Pow(self, expr):
        PREC = precedence(expr)
        if expr.exp is S.NegativeOne:
            return '1.0/%s'%(self.parenthesize(expr.base, PREC))
        else:
            return StrPrinter._print_Pow(self, expr)

    def _print_Rational(self, expr):
        p, q = int(expr.p), int(expr.q)
        return '%d.0/%d.0' % (p, q)


class StrictFCodePrinter(FCodePrinter):
    """A printer to convert python expressions to strings of Fortran code"""

    def emptyPrinter(self, expr):
        raise NotImplementedError("Can not print as Fortran code: %s" % expr)

    # the following can not be simply translated into Fortran.
    _print_Basic = emptyPrinter
    _print_ComplexInfinity = emptyPrinter
    _print_Derivative = emptyPrinter
    _print_dict = emptyPrinter
    _print_Dummy = emptyPrinter
    _print_ExprCondPair = emptyPrinter
    _print_Factorial = emptyPrinter
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
        name = implicit_functions.get(expr.__class__)
        if name is None:
            raise NotImplementedError("Function not available in Fortran: %s" % expr)
        else:
            return "%s(%s)" % (name, self.stringify(expr.args, ", "))


def fcode(expr, precision=15, strict=False):
    """Converts an expr to a string of Fortran 77 code

       Arguments:
         expr  --  a sympy expression to be converted

       Optional arguments:
         precision  --  the precission for numbers such as pi [default=15]

       >>> from sympy import *
       >>> x, tau = symbols(["x", "tau"])

       >>> fcode((2*tau)**Rational(7,2))
       '8*2**(1.0/2.0)*tau**(7.0/2.0)'
       >>> fcode(sin(x))
       'sin(x)'
       >>> fcode(pi)
       '3.14159265358979'
    """
    profile = {
        "full_prec": False, # programmers don't care about trailing zeros.
        "precision": precision,
    }
    if strict:
        return StrictFCodePrinter(profile).doprint(expr)
    else:
        return FCodePrinter(profile).doprint(expr)


def print_fcode(expr, precision=15):
    """Prints the Fortran representation of the given expression."""
    print fcode(expr, precision)


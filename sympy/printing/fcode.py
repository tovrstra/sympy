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
from sympy.printing.precedence import precedence, PRECEDENCE
from sympy.core.basic import S


class FCodePrinter(StrPrinter):
    """A printer to convert python expressions to strings of Fortran code"""
    printmethod = "_fcode_"

    def _print_Pow(self, expr):
        PREC = precedence(expr)
        if expr.exp is S.NegativeOne:
            return '1.0/%s'%(self.parenthesize(expr.base, PREC))
        else:
            return StrPrinter._print_Pow(self, expr)

    def _print_NumberSymbol(self, expr):
        # Standard Fortran has no predefined constants. Therefor NumerSymbols
        # are evaluated.
        return str(expr.evalf(self._settings["precision"]))

    _print_Catalan = _print_NumberSymbol
    _print_EulerGamma = _print_NumberSymbol
    _print_Exp1 = _print_NumberSymbol
    _print_GoldenRatio = _print_NumberSymbol
    _print_Pi = _print_NumberSymbol

    def _print_Rational(self, expr):
        p, q = int(expr.p), int(expr.q)
        return '%d.0/%d.0' % (p, q)


def fcode(expr, precision=15):
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
    return FCodePrinter(profile).doprint(expr)


def print_fcode(expr, precision=15):
    """Prints the Fortran representation of the given expression."""
    print fcode(expr, precision)


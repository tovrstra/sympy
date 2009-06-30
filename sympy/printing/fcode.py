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

    def _print_Rational(self, expr):
        p, q = int(expr.p), int(expr.q)
        return '%d.0/%d.0' % (p, q)


def fcode(expr):
    """Converts an expr to a string of Fortran 77 code

        >>> from sympy import *
        >>> from sympy.abc import *

        >>> fcode((2*tau)**Rational(7,2))
        '8*2**(1.0/2.0)*tau**(7.0/2.0)'
        >>> fcode(sin(x))
        'sin(x)'
    """
    return FCodePrinter().doprint(expr)


def print_fcode(expr):
    """Prints the Fortran representation of the given expression."""
    print fcode(expr)


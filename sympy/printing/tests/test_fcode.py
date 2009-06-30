from sympy import sin, cos, atan2, gamma, conjugate, Factorial, Integral, \
    symbols, raises
from sympy import Catalan, EulerGamma, E, GoldenRatio, I, pi
from sympy import Function, Rational, Integer

from sympy.printing import fcode


def test_printmethod():
    x = symbols('x')
    class nint(Function):
        def _fcode_(self):
            return "nint(%s)" % fcode(self.args[0])
    assert fcode(nint(x)) == "      nint(x)"

def test_fcode_Pow():
    x, y = symbols('xy')
    assert fcode(x**3) == "      x**3"
    assert fcode(x**(y**3)) == "      x**(y**3)"
    assert fcode(1/(sin(x)*3.5)**(x - y**x)/(x**2 + y)) == \
        "      (3.5*sin(x))**(-x + y**x)/(y + x**2)"

def test_fcode_Rational():
    assert fcode(Rational(3,7)) == "      3.0/7.0"
    assert fcode(Rational(18,9)) == "      2"
    assert fcode(Rational(3,-7)) == "      -3.0/7.0"
    assert fcode(Rational(-3,-7)) == "      3.0/7.0"

def test_fcode_Integer():
    assert fcode(Integer(67)) == "      67"
    assert fcode(Integer(-1)) == "      -1"

def test_fcode_functions():
    x, y = symbols('xy')
    assert fcode(sin(x) ** cos(y)) == "      sin(x)**cos(y)"

def test_fcode_NumberSymbol():
    assert fcode(Catalan) == '      0.915965594177219'
    assert fcode(EulerGamma) == '      0.577215664901533'
    assert fcode(E) == '      2.71828182845905'
    assert fcode(GoldenRatio) == '      1.61803398874989'
    assert fcode(pi) == '      3.14159265358979'
    assert fcode(pi,precision=5) == '      3.1416'

def test_fcode_complex():
    assert fcode(I) == "      cmplx(0,1)"
    x = symbols('x')
    assert fcode(4*I) == "      cmplx(0,4)"
    assert fcode(3+4*I) == "      cmplx(3,4)"
    assert fcode(3+4*I+x) == "      cmplx(3,4) + x"
    assert fcode(I*x) == "      cmplx(0,1)*x"
    assert fcode(3+4*I-x) == "      cmplx(3,4) - x"
    x = symbols('x', imaginary=True)
    assert fcode(5*x) == "      5*x"
    assert fcode(I*x) == "      cmplx(0,1)*x"

def test_implicit():
    x, y = symbols('xy')
    assert fcode(sin(x)) == "      sin(x)"
    assert fcode(atan2(x,y)) == "      atan2(x, y)"
    assert fcode(conjugate(x)) == "      conjg(x)"

def test_strict():
    x = symbols('x')
    g = Function('g')
    assert fcode(gamma(x)) == "      gamma(x)"
    assert fcode(Integral(sin(x))) == "      Integral(sin(x), x)"
    assert fcode(g(x)) == "      g(x)"
    raises(NotImplementedError, 'fcode(gamma(x), strict=True)')
    raises(NotImplementedError, 'fcode(Integral(sin(x)), strict=True)')
    raises(NotImplementedError, 'fcode(g(x), strict=True)')

def test_user_functions():
    x = symbols('x')
    assert fcode(sin(x), user_functions={sin: "zsin"}) == "      zsin(x)"
    assert fcode(sin(x), user_functions={sin: "zsin"}, strict=True) == "      zsin(x)"
    x = symbols('x')
    assert fcode(gamma(x), user_functions={gamma: "mygamma"}) == "      mygamma(x)"
    assert fcode(gamma(x), user_functions={gamma: "mygamma"}, strict=True) == "      mygamma(x)"
    g = Function('g')
    assert fcode(g(x), user_functions={g: "great"}) == "      great(x)"
    assert fcode(g(x), user_functions={g: "great"}, strict=True) == "      great(x)"
    n = symbols('n', integer=True)
    assert fcode(Factorial(n), user_functions={Factorial: "fct"}) == "      fct(n)"
    assert fcode(Factorial(n), user_functions={Factorial: "fct"}, strict=True) == "      fct(n)"

def test_assign_to():
    x = symbols('x')
    assert fcode(sin(x), assign_to="s") == "      s = sin(x)"

def test_line_wrapping():
    x, y = symbols('xy')
    assert fcode(((x+y)**10).expand(), assign_to="var") == \
        "      var = 45*x**8*y**2 + 120*x**7*y**3 + 210*x**6*y**4 + 252*x**5*y**5\n"\
        "     @     + 210*x**4*y**6 + 120*x**3*y**7 + 45*x**2*y**8 + 10*x*y**9 + \n"\
        "     @    10*y*x**9 + x**10 + y**10"


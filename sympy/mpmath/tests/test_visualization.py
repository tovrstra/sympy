"""
Limited tests of the visualization module. Right now it just makes
sure that passing custom Axes works.

"""

from sympy.mpmath import mp, fp

def test_axes():
    try:
        import pylab
    except ImportError:
        print "\nSkipping test (pylab not available)\n"
        return
    from Tkinter import TclError
    try:
        fig = pylab.figure()
    except TclError:
        print "\nSkipping test (Tcl problem)\n"
        return
    axes = fig.add_subplot(111)
    for ctx in [mp, fp]:
        ctx.plot(lambda x: x**2, [0, 3], axes=axes)
        assert axes.get_xlabel() == 'x'
        assert axes.get_ylabel() == 'f(x)'

    fig = pylab.figure()
    axes = fig.add_subplot(111)
    for ctx in [mp, fp]:
        ctx.cplot(lambda z: z, [-2, 2], [-10, 10], axes=axes)
    assert axes.get_xlabel() == 'Re(z)'
    assert axes.get_ylabel() == 'Im(z)'

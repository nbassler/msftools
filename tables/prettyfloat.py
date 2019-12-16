from math import log10
from math import floor
from math import fabs


def pretty(x, min_digits=4, exponent=2):
    """
    A nicer way to print floats than the {:g} format.

    min_digits: the minimum number of significant digits which will be printed.

    exponent: x values which are within 10**exponent or lower are displayed as floats.
              (-1 means all are printed as exponents)
    """

    # avoid zero problems
    if x < 1 and x > -1:
        dd = min_digits
    else:
        _size = floor(log10(fabs(x)))
        dd = min_digits - _size - 1

    # print("dd:", dd, _size, log10(x))
    if dd < 0:
        dd = 0

    if x > 0 and fabs(x) <= float(10**(-exponent)):
        _t = str(min_digits - 1) + 'e'

    elif fabs(x) >= float(10**(exponent + 1)):
        _t = str(min_digits - 1) + 'e'

    else:
        _t = str(dd) + 'f'

    _fmt = "{:." + _t + "}"

    return _fmt.format(x)


# note that funny rounding effects may happen, as 1.2345 may be stored as 1.2344999999999999999999999992519
# which rounds to 1.234
#
# print(pretty(0.00012345))
# print(pretty(0.0012345))
# print(pretty(0.012345))
# print(pretty(0.12345))
# print(pretty(1.2345))
# print(pretty(12.345))
# print(pretty(123.45))
# print(pretty(1234.5))
# print(pretty(12345))
# print(pretty(0))

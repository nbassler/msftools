import numpy as np
from scipy.integrate import quad


def integrand(t, n, x):
    return np.exp(-x*t) / t**n


def expint(n, x):
    return quad(integrand, 1, np.inf, args=(n, x), epsrel=1e-10)[0]


vec_expint = np.vectorize(expint)

base_x = np.array([1.0, 1.5, 2.0, 2.5, 3, 4, 5, 6, 7, 8, 9])

x = np.array([])

for i in np.arange(-2, 2, 1, dtype=np.longdouble):
    x = np.append(x, (10.0**i) * base_x)

x = np.append(x, np.array([100, 150, 200, 500, 1000]))

n = 2

e1 = vec_expint(1, x)
e2 = vec_expint(2, x)

e1_bar = e1 * x * np.exp(x)
e2_bar = e2 * x * np.exp(x)

for i, xx in enumerate(x):
    print("{:8.3g} & {:12.5e} & {:12.5e} & {:12.7f} & {:12.6f}\\\\".format(x[i], e1[i], e2[i], e1_bar[i], e2_bar[i]))

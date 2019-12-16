import numpy as np
# import sys
from scipy.integrate import quad
# from scipy.integrate import romberg
from prettyfloat import pretty


def integrand(t, x):
    return np.exp(-x / np.cos(t))


def sievert_int(x, theta):
    return quad(integrand, 0, theta, args=(x,))[0]
    # return romberg(integrand, 0, theta, args=(x,))


def deg2rad(x):
    return (x / 180.0) * np.pi


# vec_expint = np.vectorize(expint)

# setup steps for thickness (b)
bs = np.array([0.00, 0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80,
               1.00, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00, 3.50,
               4, 5, 6, 8, 10, 12, 15, 20, 25, 35, 50, 60, 75])

# break b into chunks of 7:
# bbs = np.split(b, 4)

# degrees:
# degs = np.array([1, 2.5, 5, 7.5, 10, 12.5, 15, 20, 30, 35, 40, 45, 50, 60, 70, 80, 90])
l_degs = []
l_degs.append(np.array([0, 1, 2.5, 5, 7.5, 10]))
l_degs.append(np.array([12.5, 15, 20, 30, 35, 40]))
l_degs.append(np.array([45, 50, 60, 70, 80, 90]))

# print(expint(2.0, deg2rad(20.0)))
# sys.exit(1)

# print degree header:
for degs in l_degs:

    rads = deg2rad(degs)

    s = np.zeros((len(bs), len(degs)))

    # print the degrees
    print("   $\\theta [^\\circ]\\rightarrow$", end=' & ')
    for j, d in enumerate(degs):
        print("{:6.1f}$^\\circ$".format(d), end='')
        if j >= len(degs) - 1:
            print("\\\\")
        else:
            print(" & ", end='')

    # print the radians
    print("    $b \\downarrow \\theta [rad] \\rightarrow$ ", end=' & ')
    for j, d in enumerate(degs):
        print(pretty(deg2rad(d), min_digits=6), end='')
        if j >= len(degs) - 1:
            print("\\\\")
        else:
            print(" & ", end='')

    print("\\hline\n\\hline")

    for i, b in enumerate(bs):
        print("{:6.2f}".format(b), end=' & ')
        for j, d in enumerate(degs):
            s[i, j] = sievert_int(b, deg2rad(d))
            print(pretty(s[i][j], min_digits=6), end='')
            if j >= len(degs) - 1:
                print("\\\\")
            else:
                print(" & ", end='')
    print("\n\n")

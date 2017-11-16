# -*- coding: utf-8 -*-
import math


def sq(x):
    return float(x * x)


def get_point(pointA, pointB, dA, dB):

    x = pointA[0]
    y = pointA[1]

    a = pointB[0]
    b = pointB[1]

    R = dA
    S = dB

    # print "arm target:", a, b

    d = math.sqrt(sq(math.fabs(a - x)) + sq(math.fabs(b - y)))
    # print "desitens:", d

    if d > (R + S) or d < (math.fabs(R - S)):
        return -1

    if d == 0 and R == S:
        return -1

    try:
        A = (sq(R) - sq(S) + sq(d)) / (2 * d)
        h = math.sqrt(sq(R) - sq(A))

        x2 = x + A * (a - x) / d
        y2 = y + A * (b - y) / d

        # print x2, y2
        x3 = x2 - h * (b - y) / d
        y3 = y2 + h * (a - x) / d

        x4 = x2 + h * (b - y) / d
        y4 = y2 - h * (a - x) / d

    except BaseException:
        return -1

    # print "arm middle point:"
    print (x3, y3), (x4, y4)

    return ((x3, y3), (x4, y4))

def get_center(point_a, point_b, point_c, d1, d2, d3):

    denominator = 1 / (d1 + d2) + 1 / (d1 + d3) + 1 / (d2 + d3)

    x = (point_a[0] / (d1 + d2) + point_b[0] / (d2 + d3) + point_c[0] / (d1 + d3)) / denominator
    y = (point_a[1] / (d1 + d2) + point_a[1] / (d2 + d3) + point_a[1] / (d1 + d3)) / denominator
    return (x, y)

def distance(point_a, point_b):
    return math.sqrt(sq(point_a[0] - point_b[0]) + sq(point_a[1] - point_b[1]))

d_a = float(3.6)
d_b = float(3.6)
d_c = float(3.6)

# arm point
point_a = (0.0, 0.0)

# target point for arm
point_b = (0.0, 5.0)

point_c = (5.0, 0.0)

center = get_center(get_point(point_a, point_b, d_a, d_b)[1],
        get_point(point_b, point_c, d_b, d_c)[0],
        get_point(point_c, point_a, d_c, d_a)[1],
            d_a, d_b, d_c)

print center
print distance(point_a, center)
print distance(point_b, center)
print distance(point_c, center)


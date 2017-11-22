#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import json
import numpy as np
app = Flask(__name__)

x = {1:0, 2:3, 3:6, 4:0, 5:3, 6:6, 7:0, 8:3, 9:3}
y = {1:0, 2:0, 3:0, 4:3, 5:3, 6:3, 7:6, 8:6, 9:6}

position = {1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1), 9: (2, 2)}

position_to_minor = [[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 9]]
totalX = 3
totalY = 3

W = {1: 12}
p = {1: 12}

# def getXY(pointA, pointB, dA, dB):
#     x = 0
#     y = 0
#     if pointA.x == pointB.x:
#         y = pointA.y
#         x = y
#     elif pointA.y == pointB.y:
#         x = pointA.x
#         y = pointB.x
#     else:
#         x = pointA.x
#         y = pointB.y
#
#     return (x, y)

def getDistance(rssi_value, minor):
    return np.power(10.0, (np.array([rssi_value]) / 10 - p[minor]) / W[minor]).tolist()


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


@app.route('/position', methods=['POST', 'GET'])
def hello_world():
    if (request.form['d1'] == '0') or (request.form['d2'] == '0') or (request.form['d3'] == '0'):

        return ('', 500)
    d1 = getDistance(float(request.form['d1']), sess['2'].run(W['2']), sess['2'].run(p0['2']))[0]
    d2 = getDistance(float(request.form['d2']), sess['3'].run(W['3']), sess['3'].run(p0['3']))[0]
    d3 = getDistance(float(request.form['d3']), sess['4'].run(W['4']), sess['4'].run(p0['4']))[0]
    print (d1, d2, d3)

    center = get_center(get_point((0.0, 0.0), (0.0, 5.0), d1, d2)[1],
                        get_point((0.0, 5.0), (5.0, 0.0), d2, d3)[0],
                        get_point((5.0, 0.0), (0.0, 0.0), d3, d1)[1],
                        d1, d2, d3)
    print center
    if center == -1:
        return ('', 500)
    else:
        return (json.dumps({
            'x': str(center[0]),
            'y': str(center[1])
        }), 200, {
            'content-type': 'application/json'
        })


app.run(host='0.0.0.0')

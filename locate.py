#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import json
import math
import numpy as np

app = Flask(__name__)

x = {1: 0, 2: 3, 3: 6, 4: 0, 5: 3, 6: 6, 7: 0, 8: 3, 9: 3}
y = {1: 0, 2: 0, 3: 0, 4: 3, 5: 3, 6: 3, 7: 6, 8: 6, 9: 6}

position = {1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1), 9: (2, 2)}

position_to_minor = [[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 9]]
totalX = 3
totalY = 3

W = {1: -1.48957,
     2: -1.48681,
     3: -1.46657,
     4: -1.46933,
     5: -1.48773,
     6: -1.52914,
     7: -1.48865,
     8: -1.52081,
     9: -1.48037,
     10: -1.51994,
     11: -1.50246,
     12: -1.48589,
     13: -1.48865,
     14: -1.47853,
     15: -1.48681,
     16: -1.51539,
     17: -1.48589,
     18: -1.51442,
     19: -1.47761,
     20: -1.49969,
     21: -1.50246,
     22: -1.54202,
     23: -1.51258,
     24: -1.50522,
     25: -1.49049,
     26: -1.45461,
     27: -1.45093,
     28: -1.43621,
     29: -1.45277,
     30: -1.47669}
p = {1: 5.94826,
     2: 5.93909,
     3: 5.87185,
     4: 5.88102,
     5: 5.94215,
     6: 6.07968,
     7: 5.9452,
     8: 6.05219,
     9: 5.9177,
     10: 6.04912,
     11: 5.99105,
     12: 5.93603,
     13: 5.9452,
     14: 5.91158,
     15: 5.93909,
     16: 6.03382,
     17: 5.93603,
     18: 6.03078,
     19: 5.90853,
     20: 5.98188,
     21: 5.99105,
     22: 6.12247,
     23: 6.02467,
     24: 6.00022,
     25: 5.95132,
     26: 5.83212,
     27: 5.81989,
     28: 5.77099,
     29: 5.82601,
     30: 5.90547}


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
    # if (request.form['d1'] == '0') or (request.form['d2'] == '0') or (request.form['d3'] == '0'):
    #     return ('', 500)
    print(request)
    rssi1 = request.form['rssi1']
    rssi2 = request.form['rssi2']
    rssi3 = request.form['rssi3']
    minor1 = str(request.form['minor1'])
    minor2 = str(request.form['minor2'])
    minor3 = str(request.form['minor3'])
    print rssi1, rssi2, rssi3, minor1
    d1 = getDistance(float(rssi1)/-10, W[minor1], p[minor1])[0]
    d2 = getDistance(float(rssi2)/-10, W[minor2], p[minor2])[0]
    d3 = getDistance(float(rssi3)/-10, W[minor3], p[minor3])[0]
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import json
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import math

def draw_line ():
    im = Image.new("RGBA", (1500, 1000), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    for i in range(len(x_data)):
        if device[i] == '4':
            color = (255, 0, 0)
        elif device[i] == '2':
            color = (0, 255, 0)
        elif device[i] == '3':
            color = (0, 0, 255)
        else:
            pass
        draw.point((x_data[i] * 200 + 3 * np.random.randn(), (y_data[i]) * -10 + 3 * np.random.randn()), fill=color)
    trained_x = [i for i in range(1, 1500)]
    trained_y = np.array((np.log10(np.array(trained_x) / 200.0)
                          * sess[deviceId].run(W[deviceId]) + sess[deviceId].run(p0[deviceId])) * -10).tolist()

    for i in range(len(trained_x)):
        draw.point((trained_x[i], trained_y[i]), fill=color)

    im.show()

def get_tran_data():
    x_data = []
    y_data = []
    for i in range(1,31,1):
        x_data.append([])
        y_data.append([])
    with open('./trandata/rssi') as data_file:
        data = json.load(data_file)
    for minor in data:
        distance = 0
        times = 0
        for item in data[minor]:
            if distance == item['distance'] and times >= 100:
                continue
            if distance != item['distance']:
                times = 0
            distance = item['distance']
            times = times + 1
            y_data[int(minor)-1].append(float(item['distance']))
            x_data[int(minor)-1].append(float(item['rssi'])/-10)

    return (np.array(x_data), np.array(y_data))



def tran() :
    p = tf.Variable(tf.zeros([1]) + 1)
    W = tf.Variable(tf.zeros([1]))

    (x_data, y_data) = get_tran_data()
    # print (x_data, y_data)
    np_x_data = np.array(y_data).astype(np.float32).transpose()
    np_y_data = np.array(x_data).astype(np.float32).transpose()
    def log10(x):
        numerator = tf.log(x)
        denominator = tf.log(tf.constant(10, dtype=numerator.dtype))
        return numerator / denominator

    # 最小化方差



    for i in range(1, 31, 1):
        y = log10(np_x_data[i]) * W + p
        loss = tf.reduce_mean(tf.square(y - np_y_data[i]))
        optimizer = tf.train.GradientDescentOptimizer(0.5)
        train = optimizer.minimize(loss)

        # 初始化变量
        init = tf.global_variables_initializer()

        sess = tf.Session()
        sess.run(init)

        saver = tf.train.Saver()
        # sess.reset()
        # tf.Session.close(sess)


        # # 拟合平面
        for step in xrange(0, 500):
            # if step % 20 == 0:
                # print step, sess.run(W), sess.run(p)
            sess.run(train)

        traned_w = sess.run(W)
        traned_p = sess.run(p)
        print float(str(traned_w[0])), float(str(traned_p[0]))


    save_path = saver.save(sess, "./trandata/model.ckpt")
    return (float(traned_w), float(traned_p[0][0]))


def getDistance(rssi_value, w, p):
    return np.power(10.0, (np.array([rssi_value]) - p) / w).tolist()


tran()

from flask import Flask, request
import json
app = Flask(__name__)

x0 = [0, 5, 0]
y0 = [0, 0, 5]

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

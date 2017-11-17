#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import json
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import PIL.ImageShow as ImageShow
import math

im = Image.new("RGBA", (1500, 1000), (255, 255, 255, 0))

p0 = {
    "2": tf.Variable(tf.zeros([1]) + 10),
    "3": tf.Variable(tf.zeros([1]) + 10),
    "4": tf.Variable(tf.zeros([1]) + 10)
}
W = {
    "2": tf.Variable(tf.zeros([1])),
    "3": tf.Variable(tf.zeros([1])),
    "4": tf.Variable(tf.zeros([1]))
}

# 初始化变量
init = tf.global_variables_initializer()

# 启动图 (graph)
sess = {
    "2": tf.Session(),
    "3": tf.Session(),
    "4": tf.Session()
}
[sess[i].run(init) for i in sess]

saver = tf.train.Saver()

with open('./trandata/data.json') as data_file:
    data = json.load(data_file)
for deviceId in ['2', '3', '4']:

        x_data = []
        y_data = []
        device = []
        for obj in data:
            if str(obj['deviceId']) == deviceId:
                x_data.append(float(obj['distance']))
                y_data.append(float(obj['rssi']))
                device.append(str(obj['deviceId']))

        np_x_data = np.array(x_data).astype(np.float32)
        np_y_data = np.array(y_data).astype(np.float32)


        def log10(x):
            numerator = tf.log(x)
            denominator = tf.log(tf.constant(10, dtype=numerator.dtype))
            return numerator / denominator

        y = W[deviceId] * log10(x_data) + p0[deviceId]

        # 最小化方差
        loss = tf.reduce_mean(tf.square(y - np_y_data))
        optimizer = tf.train.GradientDescentOptimizer(0.5)
        train = optimizer.minimize(loss)

        # 拟合平面
        for step in xrange(0, 200):
            sess[deviceId].run(train)
            print step, sess[deviceId].run(W[deviceId]), sess[deviceId].run(p0[deviceId])

        save_path = saver.save(sess[deviceId], "./trandata/model.ckpt" + deviceId)

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

# im.show()


def getDistance(rssi_value, w, p):
    return np.power(10.0, (np.array([rssi_value]) - p) / w).tolist()


from flask import Flask, request
import json
app = Flask(__name__)

x0 = [0, 5, 0]
y0 = [0, 0, 5]

def getXY(pointA, pointB, dA, dB):
    x = 0
    y = 0
    if pointA.x == pointB.x:
        y = pointA.y
        x = y
    elif pointA.y == pointB.y:
        x = pointA.x
        y = pointB.x
    else:
        x = pointA.x
        y = pointB.y

    return (x, y)


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
    if center == -1 :
        return ('', 500)
    else:
        return (json.dumps({
            'x': str(center[0]),
            'y': str(center[1])
        }), 200, {
            'content-type': 'application/json'
        })


app.run(host='0.0.0.0')
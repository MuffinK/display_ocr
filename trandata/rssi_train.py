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

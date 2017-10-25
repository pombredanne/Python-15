# -*- coding:utf-8 -*-
""" Txt to STL"""
# !/usr/bin/python
# Python:   3.5.2
# Platform: Windows/ARMv7/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  Txt to STL.
# History:  2017/10/25 V1.0 [Heyn]


import stl
import logging
import numpy as np
from stl import mesh

from matplotlib import pyplot
from mpl_toolkits import mplot3d


STL_HORIZONTAL = 0.0
STL_VERTICAL = 1.0

class CoraTXTtoSTL:
    """
        *.txt
        1,0,-1,0,1,1,1,1,-1
        2,1,0,2,0,2,-1,1,-1
        3,2,-1,3,-1,3,-2,2,-2
        4,3,-2,4,-2,4,-3,3,-3
        5,0,-1,0,-2,-1,-2,-1,-1
        6,-1,-2,-1,-3,-2,-3,-2,-2
    """

    def __init__(self, horizontal=STL_HORIZONTAL, vertical=STL_VERTICAL):
        self.zonedata = []
        self.vertical = vertical
        self.horizontal = horizontal
        self.zonerows = self.zonecolumns = 0
        self._npzonedata = self._common_dot = self._meshe = None

    def load(self, filepath):
        """ Load *.txt to memory.
            data = [index, data*8, horizontal, vertical]
        """

        with open(filepath, 'r') as txt:
            for line in txt.readlines():
                data = line.strip('\r\n').strip().split(',')
                if len(data) == 9:
                    data.extend([self.horizontal, self.vertical])
                    self.zonedata.append(list(map(float, data)))
                else:
                    logging.error('Zone data is error ' + line)

        self._npzonedata = np.array(self.zonedata)
        self.zonerows, self.zonecolumns = self._npzonedata.shape
        return self._npzonedata

    def meshobject(self, npdata):
        """ Generate mesh object. """
        meshdata = np.zeros(8*self.zonerows, dtype=mesh.Mesh.dtype)

        self._calc_common_dot()

        for row in range(0, self.zonerows):
            meshdata['vectors'][row*8 + 0] = npdata[row][np.array([[1, 2, 9], [3, 4, 9], [3, 4, 10]])]     #Back  Face V0
            meshdata['vectors'][row*8 + 1] = npdata[row][np.array([[3, 4, 10], [1, 2, 10], [1, 2, 9]])]    #Back  Face V1

            meshdata['vectors'][row*8 + 2] = npdata[row][np.array([[3, 4, 9], [5, 6, 9], [5, 6, 10]])]     #Right Face V0
            meshdata['vectors'][row*8 + 3] = npdata[row][np.array([[5, 6, 10], [3, 4, 10], [3, 4, 9]])]    #Right Face V1

            meshdata['vectors'][row*8 + 4] = npdata[row][np.array([[5, 6, 9], [7, 8, 9], [7, 8, 10]])]     #Front Face V0
            meshdata['vectors'][row*8 + 5] = npdata[row][np.array([[7, 8, 10], [5, 6, 10], [5, 6, 9]])]    #Front Face V1

            meshdata['vectors'][row*8 + 6] = npdata[row][np.array([[7, 8, 9], [1, 2, 9], [1, 2, 10]])]     #Left  Face V0
            meshdata['vectors'][row*8 + 7] = npdata[row][np.array([[1, 2, 10], [7, 8, 10], [7, 8, 9]])]    #Left  Face V1
        return meshdata

    def plot(self, meshdata):
        """Plot"""
        self._meshe = mesh.Mesh(meshdata.copy())
        figure = pyplot.figure()
        axes = mplot3d.Axes3D(figure)
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self._meshe.vectors))
        # Auto scale to the mesh size
        scale = np.concatenate(self._meshe.points).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)
        pyplot.show()

    def save(self, savepath, method='ASCII'):
        """ Save. """
        if method == 'ASCII':
            self._meshe.save(savepath, mode=stl.Mode.ASCII)
        else:
            self._meshe.save(savepath)

    def _calc_common_dot(self):
        """
            @params self._common_dot [row col rowx colx x y] -> dot(x,y) in [row, col] and [rowx, colx]
            ex.
                row [[ 1.  0. -1.  0.  1.  1.  1.  (1. -1.)  0.  1.]
                row  [ 2.  1.  0.  2.  0.  2. -1.  (1. -1.)  0.  1.]]

                self._common_dot = [ 0.  3.  1.  3.  (1. -1.)]
        """

        # """Search common dot (x y)"""
        # """Method 1st"""
        npdata = self._npzonedata.copy()
        for row in range(0, self.zonerows-1):
            matrixrow = npdata[row, 1:9].reshape(4, 2)
            for col, item in enumerate(matrixrow):
                for rowx in range(row+1, self.zonerows):
                    matrixrowx = npdata[rowx, 1:9].reshape(4, 2)
                    for colx, itemx in enumerate(matrixrowx):
                        if np.array_equal(item, itemx):
                            npdot = np.concatenate((np.array([row, col, rowx, colx], dtype='float64'), item))
                            self._common_dot = npdot.copy() if self._common_dot is None else np.concatenate((self._common_dot, npdot))
        else:
            self._common_dot = self._common_dot.reshape(self._common_dot.size//6, 6)
        print(self._common_dot)

        # """Method 2nd (It's faster then 1st)"""

        # npdata = self._npzonedata[:, 1:9].copy()
        # npdata = npdata.reshape(npdata.size//2, 2)
        # for index, item in enumerate(npdata):
        #     result = np.where((npdata[index:, :] == item).all(1))[0]
        #     if result.size >= 2:
        #         x1, x2 = index + result[0], index + result[1]
        #         npdot = np.concatenate((np.array([x1//4, x1%4, x2//4, x2%4], dtype='float64'), npdata[index:, :][result[0]]))
        #         self._common_dot = npdot.copy() if self._common_dot is None else np.concatenate((self._common_dot, npdot))
        # else:
        #     self._common_dot = self._common_dot.reshape(self._common_dot.size//6, 6)
        #     print(self._common_dot)

        # Transform common dot(x, y)
        self._smoothing()

    def _calc_slope(self, kp, mp):
        if kp[0] == mp[0]:
            return False
        if abs((kp[1] - mp[1]) / (kp[0] - mp[0])) == 1:
            return True

        return False

    def find_by_row(self, mat, row):
        return True if np.where((mat == row).all(1))[0].shape[0] == 0 else False

    def _smoothing(self):
        """ Transform
            -----           -----           -----
            | 1 |           | 1 |  \        | 1 |  \
            ---------   =>  -----   -   =>  -   -   -
                | 2 |           | 2 |        \  | 2 |
                -----           -----           -----
              step0     =>    setp1     =>    step2
        """

        print(self._common_dot)
        dotxy = self._common_dot[:, 4:6]

        for _, item in enumerate(self._common_dot):
            x, y = item[4], item[5]     # Common dot(x, y)
            data1 = self._npzonedata[int(item[0]), 1:9].reshape(4, 2)
            data2 = self._npzonedata[int(item[2]), 1:9].reshape(4, 2)

            # Search move dot
            mp1 = mp2 = kp1 = kp2 = np.array([x, y])

            for m, n in zip(data1, data2):
                #step1
                if m[0] == x and m[1] != y and m[1] > y:
                    mp1 = m
                if m[0] != x and m[1] == y:
                    kp1 = m
                #step2
                if n[0] == x and n[1] != y and n[1] < y:
                    mp2 = n
                if n[0] != x and n[1] == y:
                    kp2 = n

            # print(x, y)
            # ****** Condition ******
            # kp1 : slope calcurate dot  mp1 : move to dot
            # 1) kp1 and mp1 are slope must be 1
            # 2) 
            if self._calc_slope(kp1, mp1) and self.find_by_row(dotxy, mp1):
                self._npzonedata[int(item[2]), 1 + int(item[3])*2 + 1] = mp1[1]
            if self._calc_slope(kp2, mp2) and self.find_by_row(dotxy, mp2):
                self._npzonedata[int(item[0]), 1 + int(item[1])*2 + 1] = mp2[1]

TEST = CoraTXTtoSTL()
DATA = TEST.load('D:\\Python\\test.txt')
# TEST.meshobject(DATA)
TEST.plot(TEST.meshobject(DATA))
# TEST.save('D:\\Python\\test_zone.stl')

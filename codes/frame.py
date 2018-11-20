import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageChops
import copy

import tile

class board(object):
    def __init__(self, size = 50, terrainP = [0.2, 0.3, 0.3, 0.2], failP = [0.1, 0.3, 0.7, 0.9], moving = False, targetMoving = False):
        #int size in [2 : inf]: size of board
        #list terrainP with element float p: P(terrain)
        #list failP with element float p: P(false negative | terrain)
        #bool moving: True: hunter have to move between blocks; False: hunter can teleport
        #bool targetMoving: True: target move every failed search; False: stationary target.

        self.rows = size
        self.cols = size
        self.cell = np.empty((self.rows, self.cols), dtype = np.uint8)
        self.sucP = np.empty((self.rows, self.cols), dtype = np.float16)

        self.border = np.zeros((self.rows, self.cols, 4, 4), dtype = np.bool)
        self.dist = np.zeros((self.rows, self.cols, self.rows, self.cols), dtype = np.uint8)
        
        self._target = (self.rows, self.cols)

        self.hunter = (self.rows // 2, self.cols // 2)
        self.search = True
        
        self.prob = np.full((self.rows, self.cols), (1. / (self.rows * self.cols)), dtype = np.float16)

        self.terrainP = []
        self.failP = failP

        self.moving = moving
        self.targetMoving = targetMoving

        self.targetHistory = []
        self.probHistory = []

        self.getTerrainP(terrainP)
        self.buildTerrain()
        self.hideTarget()
        if self.moving:
            self.getDist()
        self.probHistory.append(self.prob.copy())

        self.tile = tile.tile()
        return

    #init functions
    #transform to accumulate p
    def getTerrainP(self, terrainP):
        #list terrainP with element float p: P(terrain)

        sumP = 0
        for p in terrainP:
            self.terrainP.append(sumP)
            sumP = sumP + p
        return

    #init cell
    def buildTerrain(self):
        terrain = np.random.rand(self.rows, self.cols)
        for i in range(len(self.terrainP)):
            self.cell[terrain >= self.terrainP[i]] = i
            self.sucP[terrain >= self.terrainP[i]] = 1 - self.failP[i]
        if self.targetMoving:
            self.getBorder()
        return

    #init _target
    def hideTarget(self):
        pos = int(np.floor(np.random.random() * self.rows * self.cols))
        row, col = divmod(pos, self.cols)
        self._target = (row, col)
        if self.targetMoving:
            self.targetHistory.append(self._target)
        return

    #init border
    def getBorder(self):
        for row in range(self.rows):
            for col in range(self.cols):
                index = 0
                for nRow, nCol in ((row-1, col), (row, col-1), (row, col+1), (row+1, col)):
                    if 0 <= nRow < self.rows and 0 <= nCol < self.cols:
                        self.border[row, col, :, index][self.cell[nRow, nCol]] = True
                    index = index + 1
        return

    #init dist
    def getDist(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.dist[row, col] = self.getBlockDist(row, col)
        return


    #tool functions
    #print the board
    def visualize(self, beacon = 10):
        #int beacon [1 : inf]: interval of beacons; 0: no beacon
        #return
        #PIL.Image image: board image

        normProb = (self.prob / np.max(self.prob))
        image = np.zeros((self.rows*16, self.cols*16, 3), dtype = np.uint8)
        for row in range(self.rows):
            for col in range(self.cols):
                image[row*16 : row*16+16, col*16 : col*16+16] = self.tile(terrain = self.cell[row, col], prob = normProb[row, col], target = ((row, col) == self._target), hunter = ((row, col) == self.hunter), search = self.search, beacon = (beacon and not (row%beacon and col%beacon)))
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        plt.imshow(img)
        plt.show()
        return img

    #generate neighbor of (row, col)
    def getNeighbor(self, row, col):
        #int row in [0 : rows-1]: position x
        #int col in [0 : cols-1]: position y
        #return:
        #list neighbor with element ((row, col), index): this block's neighbor

        candidate = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        neighbor = []
        for nRow, nCol in candidate:
            if -1 < nRow < self.rows and -1 < nCol < self.cols:
                neighbor.append((nRow, nCol))
        return neighbor

    def manhattan(self, x, y):
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    def getBlockDist(self, row = None, col = None):
        if row is None or col is None:
            row, col = self.hunter
        dist = np.empty_like(self.cell, dtype = np.uint8)
        for tRol in range(self.rows):
            for tCol in range(self.cols):
                dist[tRol, tCol] = self.manhattan(x = (row, col), y = (tRol, tCol))
        return dist

    #action functions
    #search (row, col)
    def explore(self, row = None, col = None):
        #int row: position
        #int col: position
        #return:
        #bool res: True: done! False: not found
        #np.ndarray report with shape = (4, ): target moving report

        #teleport
        if row is None or col is None:
            pass
        else:
            self.hunter = (row, col)
        self.search = True

        #search
        if self.hunter == self._target:
            #print('right block')
            if np.random.random() < self.failP[self.cell[self.hunter]]:
                report = self.targetMove()
                return (False, report)
            else:
                return (True, None)
        else:
            report = self.targetMove()
            return (False, report)

    #move to (row, col)
    def move(self, row, col):
        #int row: position
        #int col: position

        self.search = False
        self.hunter = (row, col)
        return

    #target move to neighbor
    def targetMove(self):
        #return:
        #np.ndarray report with shape = (4, ): target moving report
        
        report = np.zeros((4, ), dtype = np.uint8)
        if self.targetMoving:
            candidate = self.getNeighbor(*self._target)
            index = int(np.floor(np.random.random() * len(candidate)))
            report[self.cell[self._target]] = report[self.cell[self._target]] + 1
            report[self.cell[candidate[index]]] = report[self.cell[candidate[index]]] + 1
            self._target = candidate[index]
            self.targetHistory.append(self._target)
        # print(report)
        return report


#use seedBoard generate num boards
def boardFactory(seedBoard, num = 5000, multiple = True):
    if seedBoard is None:
        seedBoard = board(50, moving = moving, targetMoving = targetMoving)

    boardList = []
    for i in range(num):
        b = copy.deepcopy(seedBoard)
        if multiple:
            b.buildTerrain()
        b.hideTarget()
        boardList.append(b)
    return boardList


if __name__ == '__main__':
    b = board(50, moving = True, targetMoving = True)
    b.explore()
    print(b.targetHistory)

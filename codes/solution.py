import numpy as np
import timeit

import frame
import test

class player(object):
    def __init__(self, board, quickRes = False, double = False):
        #frame.board board: game board
        self.b = board
        self.reportHistory = []
        self.quickRes = quickRes
        self.double = double

        self.doubleThreshold = np.ceil(np.log(0.01) / np.log(np.asarray(self.b.failP, dtype = np.float16))).astype(np.uint8) - 1
        self.doubleCount = np.zeros_like(self.b.cell, dtype = np.uint8)

        self.success = False
        self.history = []
        return
    
    #update b.prob after search
    def updateP(self, row, col, quick = False, force = False, temp = False):
        if temp:
            tempProb = np.copy(self.b.prob)
        else:
            tempProb = self.b.prob

        tempProb[row, col] = tempProb[row, col] * self.b.failP[self.b.cell[row, col]]
        sumP = np.sum(tempProb)

        if not force and (self.quickRes or quick) and sumP > 0.5:
            return
        tempProb = self.normalizeP(tempProb, sumP)
        if not temp:
            self.b.prob = tempProb
        return tempProb

    #get next block to search
    def getNext(self, row = None, col = None, rule = 3):
        if rule == 1:
            pos = self.maxProb(row, col)
        elif rule == 2:
            pos = self.maxSucP(row, col)
        elif rule == 3:
            pos = self.maxInfo(row, col)
        else:
            print('E: solution.getNext. wrong rule number.')
        return pos

    #tool functions
    #resize prob so that sum == 1
    def normalizeP(self, tempProb, sumP = None):
        if sumP is None:
            sumP = np.sum(tempProb)
        tempProb = tempProb / sumP
        return tempProb

    #
    def maxProb(self, row = None, col = None):
        if row is None or col is None:
            value = self.b.prob
            pos = np.unravel_index(np.argmax(value), value.shape)
            return pos
        else:
            candidate = self.b.getNeighbor(*self.b.hunter)
            #move to candidate or explore here
            #if move to candidate, which one to move
            return

    def maxSucP(self, row = None, col = None):
        if row is None or col is None:
            value = self.b.prob * self.b.sucP
            pos = np.unravel_index(np.argmax(value), value.shape)
            return pos
        else:
            candidate = self.b.getNeighbor(*self.b.hunter)
            #move to candidate or explore here
            #if move to candidate, which one to move
            return

    def maxInfo(self, row = None, col = None):
        if row is None or col is None:
            tempSucP = self.b.prob * self.b.sucP
            tempSucQ = 1 - tempSucP
            searchInfo = tempSucP * np.log2(tempSucP) + tempSucQ * np.log2(tempSucQ) #there should be negative. use min to find max
            if self.b.targetMoving:
                pass #TODO: value = searchreportInfo
            else:
                value = searchInfo
            pos = np.unravel_index(np.argmin(value), value.shape) #use min instead
            return pos
        else:
            candidate = self.b.getNeighbor(*self.b.hunter)
            #move to candidate or explore here
            #if move to candidate, which one to move
            return

    def solve(self):
        while not self.success:
            pos = self.getNext(rule = 3)

            self.success, report = self.b.explore(*pos)
            self.doubleCount[pos] = self.doubleCount[pos] + 1
            self.history.append((pos, 's'))

            if self.success:
                break

            if self.double and self.b.cell[pos] < self.double and self.doubleCount[pos] >= self.doubleThreshold[self.b.cell[pos]]:
                self.updateP(*pos)
                self.success, report = self.b.explore(*pos)
                self.doubleCount[pos] = self.doubleCount[pos] + 1
                self.history.append((pos, 's'))
                if self.success:
                    break

            self.updateP(*pos)


            #in case of too long loop
            if len(self.history) > 100000:
                break

            # print(self.b.prob)
            # self.b.visualize()
        return

if __name__ == '__main__':
    lenCount = []
    startTime = timeit.default_timer()
    boardSet = []

    while len(lenCount) < 10:
        b = frame.board(size = 50)
        p = player(b, double = 2)
        p.solve()
        lenCount.append(len(p.history))
        print('')
        if len(p.history) > 100000:
            boardSet.append(b)
            continue

    endTime = timeit.default_timer()

    time = endTime - startTime

    print(lenCount)

    test.saveMaze((time, lenCount, boardSet), 'D:/Users/endle/Desktop/520/A3/log/', 'r3')



    # print(p.b.prob[p.b._target])
    # print(np.max(p.b.prob))
    # p.b.visualize()
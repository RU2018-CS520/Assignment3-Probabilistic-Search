import pickle as pkl
import timeit
import copy

import frame
import solution

def saveMaze(mazeList, path, name):
    #list mazeList with element class maze: test set of mazes. acturally, anything is ok
    #str path: saved file path. REMEMBER: end with a slash
    #str name: saved file name
    saveFile = open(path+name, 'wb')
    pkl.dump(mazeList, saveFile)
    saveFile.close()
    return

def loadMaze(path, name):
    #INPUT ARGS:
    #str path: saved file path. REMEMBER: end with a slash
    #str name: saved file name
    #RETURN VAL:
    #list mazeList with element class maze: test set of mazes. acturally, can be anything
    loadFile = open(path+name, 'rb')
    mazeList = pkl.load(loadFile)
    loadFile.close()
    return mazeList

def test(maxIter = 100000, sampleSize = 5, multiple = True, moving = False, targetMoving = False, double = 2, ruleList = [2], name = 'r.pkl'):
    #int maxIter in [1 : inf]: max search times in a board
    #int sampleSize in [1 : inf]: number of test boards
    #bool multiple: True: rebuild terrain; False: onle re-hide target
    #bool targetMoving: True: target will move; False: target is stationary
    #int double in [1 : 4]: cell types that need double check. False: no double check
    #int rule in [1 : 3]: search strategy. #WARN: rule 3 is abandoned

    seed = frame.board(size = 50, moving = moving, targetMoving = targetMoving)

    lenCount = [[], [], [], [], [], []]
    boardSet = [[], [], [], [], [], []]
    startTime = timeit.default_timer()
    
    for i in range(sampleSize): 
        bList = frame.boardFactory(seed, 1, multiple = multiple)
    
        for b in bList:
            for rule in ruleList:
                tempB = copy.deepcopy(b)
                p = solution.player(tempB, double = double, maxIter = maxIter, rule = rule)
                p.solve()
                lenCount[rule].append(len(p.history))
                print('')
                if len(p.searchHistory) > maxIter:
                    boardSet[rule].append(tempB)
                    continue
                tempB.visualize()
    
    endTime = timeit.default_timer()

    time = endTime - startTime

    print(lenCount)

    saveMaze((time, lenCount, boardSet), 'D:/Users/endle/Desktop/520/A3/log/', name)
    return

if __name__ == '__main__':
    test(maxIter = 100000, sampleSize = 5000, multiple = True, moving = True, targetMoving = True, double = True, ruleList = [1, 2, 5], name = 'r2.pkl')
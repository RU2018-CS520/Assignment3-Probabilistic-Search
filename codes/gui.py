import sys
import os
import time
import random
import frame
import solution
import numpy as np
import matplotlib.animation as animation

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QVBoxLayout,
    QSizePolicy, QMessageBox, QPushButton, QWidget, QSlider, QLabel,
    QGridLayout, QGroupBox, QLineEdit, QCheckBox, QRadioButton, QListWidget,
                             QListWidgetItem, QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QRectF
from PIL import Image, ImageChops
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Probabilistic Search (and Destroy)'
        self.width = 1280
        self.height = 960
        self.initUI()
        self.cnt = 0

    def initUI(self):
        grid = QGridLayout()

        self.canvas = Canvas(self, width=12.8, height=9.6)
        grid.addWidget(self.canvas, 0, 0, 10, 10)

        grid.addWidget(self.initConfigGroup(), 0, 11)

        grid.addWidget(self.initAnimationGroup(), 1, 11)

        self.buttonSave = QPushButton('Save animation to file', self)
        self.buttonSave.clicked.connect(self.save)
        self.buttonSave.setEnabled(False)
        grid.addWidget(self.buttonSave, 2, 11)

        self.slider = self.initSlider()
        self.slider.setEnabled(False)
        grid.addWidget(self.slider, 11, 0, 1, 12)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setLayout(grid)
        self.show()


    def initLabel(self, text):
        label = QLabel(self)
        label.setText(text)
        return label

    def initConfigGroup(self):
        groupBox = QGroupBox("Configurations")

        grid = QGridLayout()
        grid.addWidget(self.initLabel("Size:"), 0, 0)

        self.lineEditX = QLineEdit(self)
        self.lineEditX.setText("50")

        grid.addWidget(self.lineEditX, 0, 1)

        self.checkBoxMoving = QCheckBox('Agent can teleport', self)
        self.checkBoxMoving.setChecked(True)
        grid.addWidget(self.checkBoxMoving, 2, 0)

        self.checkBoxTargetMoving = QCheckBox('Target can move', self)
        self.checkBoxTargetMoving.setChecked(True)
        grid.addWidget(self.checkBoxTargetMoving, 2, 1)

        self.checkBoxAnimation = QCheckBox('Animation', self)
        grid.addWidget(self.checkBoxAnimation, 5, 1)

        self.groupBox = QGroupBox('groupBox1')
        self.radio1 = QRadioButton('Rule 1')
        self.radio2 = QRadioButton('Rule 2')
        self.radio3 = QRadioButton('Rule 3')
        self.radio4 = QRadioButton('Rule 4')
        self.radio5 = QRadioButton('Rule 5')
        self.radio1.setChecked(True)
        grid.addWidget(self.radio1, 3, 0)
        grid.addWidget(self.radio2, 3, 1)
        grid.addWidget(self.radio3, 4, 0)
        grid.addWidget(self.radio4, 4, 1)
        grid.addWidget(self.radio5, 5, 0)

        grid.addWidget(self.initLabel("Double check level:"), 6, 0)
        self.comboBox = QComboBox()
        self.comboBox.addItem('False')
        self.comboBox.addItem('1')
        self.comboBox.addItem('2')
        self.comboBox.addItem('3')
        self.comboBox.addItem('4')
        grid.addWidget(self.comboBox, 6, 1)

        self.buttonStart = QPushButton('Generate and Solve', self)
        self.buttonStart.clicked.connect(self.start)
        grid.addWidget(self.buttonStart, 8, 0, 1, 2)

        groupBox.setLayout(grid)
        return groupBox

    def initAnimationGroup(self):
        groupBox2 = QGroupBox("Animation")

        grid2 = QGridLayout()
        self.labelStep = self.initLabel("Current Step: 0")
        grid2.addWidget(self.labelStep, 0, 0)

        self.buttonNext= QPushButton('Next Step', self)
        self.buttonNext.clicked.connect(self.nextStep)
        grid2.addWidget(self.buttonNext, 1, 0)

        self.buttonStartAnimation = QPushButton('Start animation', self)
        self.buttonStartAnimation.clicked.connect(self.animate)
        self.buttonStartAnimation.setEnabled(False)
        grid2.addWidget(self.buttonStartAnimation, 1, 11)

        groupBox2.setLayout(grid2)
        return groupBox2

    def initSlider(self):
        global sliderMax
        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setMaximum(0)
        sliderMax = 0
        slider.setGeometry(0, 900, self.width, 50)
        slider.valueChanged[int].connect(self.changeValue)
        slider.sliderReleased.connect(self.releaseSlider)
        return slider

    def releaseSlider(self):
        value = self.slider.value()
        self.canvas.plotOne(value)

    def changeValue(self, value):
        self.labelStep.setText("Step: " + repr(value))

    def nextStep(self):
        global SliderMax
        global currentStep
        value = self.slider.value()
        currentStep = value
        if value < sliderMax:
            if value == 0:
                self.canvas.initUI()
            self.slider.setValue(value + 1)
            self.canvas.plotOne(value + 1)
            self.labelStep.setText("Step: " + repr(value + 1))

    def animate(self):
        global sliderMax
        global currentStep
        currentStep = 0
        self.slider.setValue(0)
        self.labelStep.setText("Step: 0")
        self.buttonStartAnimation.setEnabled(False)

        self.canvas.start()

        self.buttonStartAnimation.setEnabled(True)

    def start(self):
        global sliderMax
        global currentStep
        currentStep = 0
        self.slider.setValue(0)
        self.labelStep.setText("Step: 0")
        self.buttonStart.setEnabled(False)

        self.buttonStart.setText('Solving, please wait')

        rows = int(self.lineEditX.text())
        cols = int(self.lineEditX.text())
        moving = self.checkBoxMoving.isChecked()
        targetMoving = self.checkBoxTargetMoving.isChecked()
        rule = 1
        if self.radio1.isChecked():
            rule = 1
        elif self.radio2.isChecked():
            rule = 2
        elif self.radio3.isChecked():
            rule = 3
        elif self.radio4.isChecked():
            rule = 4
        elif self.radio5.isChecked():
            rule = 5
        if str(self.comboBox.currentText()) == 'False':
            double = False
        else:
            double = int(self.comboBox.currentText())

        print('Trying to construct a(an) ' + repr(rows) + 'x' + repr(cols) + ' maze. Agent teleporting is ' + repr(moving) + '. Target moving is ' + repr(targetMoving))
        print('Rule ' + repr(rule) + ' double ' + repr(double))
        b = frame.board(size = rows, moving = moving, targetMoving = targetMoving)
        self.p = solution.player(b, double = (False, double)[double != 0], rule = rule)
        print('Construction completed.')
        print('Player is ready, trying to solve.')
        self.p.solve()
        print('Done')
        print(len(self.p.history))
        print(self.p.history)
        print(len(b.targetHistory))
        print(b.targetHistory)
        print(len(b.probHistory))

        self.canvas.setArguement(self.p, b)
        self.canvas.initUI()
        self.slider.setMaximum(len(self.p.history) - 1)
        sliderMax = len(self.p.history) - 1
        if self.checkBoxAnimation.isChecked():
            self.animate()
        self.buttonStartAnimation.setEnabled(True)
        self.buttonStart.setText('Generate and Solve')
        self.buttonStart.setEnabled(True)
        self.slider.setEnabled(True)

    def save(self):
        self.buttonSave.setEnabled(False)
        self.canvas.save()
        self.buttonSave.setEnabled(True)

class Canvas(FigureCanvas):

    def __init__(self, parent = None, width = 12, height = 9, dpi = 100):
        #fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)

        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def setArguement(self, player, board, _beacon = 16):
        global p
        global b
        global beacon
        p = player
        b = board
        beacon = _beacon

    def start(self):
        print('Started plotting')
        global currentStepAgent
        global currentStepTarget
        global p
        global anim
        currentStepAgent = 0
        currentStepTarget = 0
        anim = FuncAnimation(self.fig, self.animate, init_func = self.init, interval = 20, blit = True)
        #self.draw()
        print('Plotting completed')

    def init(self):
        print('Initializing animation')
        global image
        global p
        global b
        prob = np.full((b.rows, b.cols), (1. / (b.rows * b.cols)), dtype = np.float16)
        normProb = (prob / np.max(prob))
        image = np.zeros((b.rows*16, b.cols*16, 3), dtype = np.uint8)
        for row in range(b.rows):
            for col in range(b.cols):
                image[row*16 : row*16+16, col*16 : col*16+16] = b.tile(terrain = b.cell[row, col], prob = normProb[row, col], target = ((row, col) == b.targetHistory[0]), hunter = ((row, col) == p.history[0]), search = b.search, beacon = (beacon and not (row%beacon and col%beacon)))
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        print('Initialization completed')
        return im,

    def plotOne(self, i):
        print('Plotting step ' + repr(i) + ' . Please wait.')
        global currentStep
        global image
        l = 1
        r = i + 1
        if i >= currentStep:
            l = currentStep + 1
        else:
            self.initUI()
        for j in range(l ,r):
            print('Drawing step ' + repr(j))
            [x, y], hint = p.history[j]
            image[x*16 : x*16+16, y*16 : y*16+16] = p.m.tile(covered = p.m.covered[x, y], mine = p.m._mine[x, y], clue = p.m._clue[x, y], hint = p.m.hint[x, y], flag = p.m.flag[x, y], beacon = beacon and not (x%beacon and y%beacon), cheat = cheat, hide = False)
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        self.draw()
        currentStep = i

    def animate(*args):
        global currentStepAgent
        global currentStepTarget
        global p
        global image
        global beacon
        global anim
        print('Drawing step ' + repr(currentStepAgent))
        if currentStepAgent > 0:
            [px, py], hint = p.history[currentStepAgent - 1]
            normProb = (b.probHistory[currentStepTarget] / np.max(b.probHistory[currentStepTarget]))
            image[px*16 : px*16+16, py*16 : py*16+16] = b.tile(terrain = b.cell[px, py], prob = normProb[px, py], target = False, hunter = False, search = b.search, beacon = (beacon and not (px%beacon and py%beacon)))

            if hint == 's':
                print(np.max(b.probHistory[currentStep - 1]))
                print(np.sum(b.probHistory[currentStep - 1]))
                normProbPre = (b.probHistory[currentStepTarget - 1] / np.max(b.probHistory[currentStepTarget - 1]))
                for row in range(b.rows):
                    for col in range(b.cols):
                        image[row*16 : row*16+16, col*16 : col*16+16] = b.tile(terrain = b.cell[row, col], prob = normProbPre[row, col], target = False, hunter = False, search = b.search, beacon = (beacon and not (row%beacon and col%beacon)))

                [ptx, pty] = b.targetHistory[currentStepTarget - 1]
                image[ptx*16 : ptx*16+16, pty*16 : pty*16+16] = b.tile(terrain = b.cell[ptx, pty], prob = normProbPre[ptx, pty], target = False, hunter = False, search = b.search, beacon = (beacon and not (ptx%beacon and pty%beacon)))

        [x, y], hint = p.history[currentStepAgent]
        [tx, ty] = b.targetHistory[currentStepTarget]
        normProb = (b.probHistory[currentStepTarget] / np.max(b.probHistory[currentStepTarget]))
        print(normProb[x, y])
        if [x, y] == [tx, ty]:
            image[x*16 : x*16+16, y*16 : y*16+16] = b.tile(terrain = b.cell[x, y], prob = normProb[x, y], target = True, hunter = True, search = b.search, beacon = (beacon and not (x%beacon and y%beacon)))
        else:
            image[x*16 : x*16+16, y*16 : y*16+16] = b.tile(terrain = b.cell[x, y], prob = normProb[x, y], target = False, hunter = True, search = b.search, beacon = (beacon and not (x%beacon and y%beacon)))
            image[tx*16 : tx*16+16, ty*16 : ty*16+16] = b.tile(terrain = b.cell[tx, ty], prob = normProb[tx, ty], target = True, hunter = False, search = b.search, beacon = (beacon and not (tx%beacon and ty%beacon)))
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        print('Finished')
        currentStepAgent += 1
        if hint == 's' and len(b.targetHistory) > 1:
            currentStepTarget += 1
        if currentStepAgent >= len(p.history):
            print('Stop!')
            anim.event_source.stop()
        return im,

    def initUI(self):
        global image
        global p
        global b
        global beacon
        prob = np.full((b.rows, b.cols), (1. / (b.rows * b.cols)), dtype = np.float16)
        normProb = (prob / np.max(prob))
        image = np.zeros((b.rows*16, b.cols*16, 3), dtype = np.uint8)
        for row in range(b.rows):
            for col in range(b.cols):
                image[row*16 : row*16+16, col*16 : col*16+16] = b.tile(terrain = b.cell[row, col], prob = normProb[row, col], target = ((row, col) == b.targetHistory[0]), hunter = ((row, col) == p.history[0]), search = b.search, beacon = (beacon and not (row%beacon and col%beacon)))
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        self.draw()

    def plotFromFile(self, cnt):
        img = Image.open(filePath + "step" + repr(cnt) + '.png')
        plt.imshow(img)
        self.draw()

    def plotFromHistory(self, p, cnt, beacon = 16, cheat = False):
        print('Drawing step ' + repr(cnt))
        [x, y], hint = p.history[cnt]
        p.m.hint[x, y] = p.m.explore(x, y)
        self.image[x*16 : x*16+16, y*16 : y*16+16] = p.m.tile(covered = p.m.covered[x, y], mine = p.m._mine[x, y], clue = p.m._clue[x, y], hint = p.m.hint[x, y], flag = p.m.flag[x, y], beacon = beacon and not (x%beacon and y%beacon), cheat = cheat, hide = False)
        img = Image.fromarray(self.image)
        img = ImageChops.invert(img)
        plt.imshow(img)
        #plt.pause(0.0001)
        self.draw()
        #plt.draw()
        print('Finished')

    def save(self):
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        global anim
        global currentStep
        currentStep = 0
        anim.save(filePath + 'animation.mp4', writer = writer)

if __name__ == '__main__':
    global filePath
    global fileCnt
    filePath = os.path.dirname(os.path.realpath(__file__))
    filePath = os.path.join(filePath, '../pics/')
    #fileCnt = len([fileName for fileName in os.listdir(filePath) if
    #               os.path.isfile(filePath + fileName)])
    #print(os.listdir(filePath))
    application = QApplication(sys.argv)
    ex = Window()
    sys.exit(application.exec_())
    # test asd

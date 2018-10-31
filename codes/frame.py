import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageChops

import tile

class board(object):
	def __init__(self, size = 50, terrainP = [0.2, 0.3, 0.3, 0.2], failP = [0.1, 0.3, 0.7, 0.9]):
		self.rows = size
		self.cols = size
		self.cell = np.empty((self.rows, self.cols), dtype = np.int8)
		
		self._target = (self.rows, self.cols)

		self.hunter = (self.rows // 2, self.cols // 2)
		self.search = True
		
		self.prob = np.full((self.rows, self.cols), (1. / (self.rows * self.cols)), dtype = np.float16)

		self.terrainP = []
		self.failP = failP

		self.getTerrainP(terrainP)
		self.buildTerrain()
		self.hideTarget()

		self.tile = tile.tile()
		return


	def getTerrainP(self, terrainP):
		sumP = 0
		for p in terrainP:
			self.terrainP.append(sumP)
			sumP = sumP + p
		return

	def buildTerrain(self):
		terrain = np.random.rand(self.rows, self.cols)
		for i in range(len(self.terrainP)):
			self.cell[terrain >= self.terrainP[i]] = i
		return

	def hideTarget(self):
		pos = int(np.floor(np.random.random() * self.rows * self.cols))
		row, col = divmod(pos, self.cols)
		self._target = (row, col)
		return

	def visualize(self, beacon = 10):
		image = np.zeros((self.rows*16, self.cols*16, 3), dtype = np.uint8)
		for row in range(self.rows):
			for col in range(self.cols):
				image[row*16 : row*16+16, col*16 : col*16+16] = self.tile(terrain = self.cell[row, col], prob = self.prob[row, col], target = ((row, col) == self._target), hunter = ((row, col) == self.hunter), search = self.search, beacon = (beacon and not (row%beacon and col%beacon)))
		img = Image.fromarray(image)
		img = ImageChops.invert(img)
		plt.imshow(img)
		plt.show()
		return img

if __name__ == '__main__':
	b = board(32)
	b.prob = np.random.rand(b.rows, b.cols)
	b.visualize()
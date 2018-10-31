import numpy as np

import frame

class player(object):
	def __init__(self, board):
		#frame.board board: game board
		self.b = board
		self.reportHistory

		self.history = []
		return
	
	#update b.prob after search
	def updateP(self, row, col):
		return

	#get next block to search
	def getNext(self, row = None, col = None):
		if row is None or col is None:
			#get next promising block
			return 
		else:
			candidate = self.b.getNeighbor(*self.b.hunter)
			#move to candidate or explore here
			#if move to candidate, which one to move
			return

	def solve(self):
		#loop
			#getNext
			#updateP
		return

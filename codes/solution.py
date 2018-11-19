import numpy as np

import frame

class player(object):
	def __init__(self, board, quickRes = False, double = False, rule = 2, maxIter = 100000):
		#frame.board board: game board
		#bool quickRes: True: faster calculation; False: more precise result
		#int double in [1 : 4]: cell types that need double check. False: no double check
		#int rule in [1 : 3]: search strategy.
		#int maxIter in [1 : inf]: max search times in a board

		self.b = board
		self.quickRes = quickRes
		self.double = double and not self.b.targetMoving
		self.rule = rule
		self.maxIter = maxIter

		#double check related
		self.doubleThreshold = np.ceil(np.log(0.01) / np.log(np.asarray(self.b.failP, dtype = np.float16))).astype(np.uint8) - 1
		self.doubleCount = np.zeros_like(self.b.cell, dtype = np.uint8)

		#report related
		self.reportHistory = []
		self.targetHistory = []
		self.searchHistory = []

		self.success = False
		self.history = []
		return
	

	#update functions
	#update b.prob after search
	def updateP(self, prob, row, col, quick = False, force = False, temp = False):
		#bool force: True: force to normalize prob; False: depand on quick
		#bool temp: True: this is a temp prob, and will not update b.prob; False: update b.prob
		
		#process temp
		if temp:
			tempProb = np.copy(prob)
		else:
			tempProb = prob

		#update
		tempProb[row, col] = tempProb[row, col] * self.b.failP[self.b.cell[row, col]]

		#process quick
		sumP = np.sum(tempProb)
		if not force and (self.quickRes or quick) and sumP > 0.5:
			if not temp:
				self.b.prob = tempProb
			return tempProb
		tempProb = self.normalizeP(tempProb, sumP)
		if not temp:
			self.b.prob = tempProb
		return tempProb

	#update b.prob after report
	def updateR(self, prob, report, quick = False, force = False, temp = False):
		solveFlag, targetMove = self.solveReport(report)
		if solveFlag:
			print('re-update')
			tempProb = self.reUpdateReport(temp = temp)
		else:
			tempProb = self.updateReport(prob, targetMove, quick = quick, force = force, temp = temp)
		return tempProb


	#report functions
	#analysis report history
	def solveReport(self, report):
		#returns:
		#bool solve Flag: True: reportHistory can translate to targetHistory; False: cannot translate
		#tuple targetMove with element (prev, post): target move from prev to post
		
		solveFlag = False
		if self.targetHistory: #translatable
			targetMove = self.solveTarget(report)
		elif self.reportHistory:
			tPrevTer = self.reportHistory[-1] * report #try to translate
			if 1 == np.count_nonzero(tPrevTer): #translatable
				self.backtrackReport(tPrevTer)
				targetMove = self.solveTarget(report)
				solveFlag = True
			elif 2 == np.count_nonzero(tPrevTer): #not translatable
				tReport = tuple(np.where(report > 0)[0])
				if len(tReport) == 1:
					tReport = (tReport[0], tReport[0])
				targetMove = (tReport, tReport[: : -1])
			else: #something wrong, target teleported
				print('E: solution.solveReport. wrong report')
				print(report)
				exit()
		else: #the first report
			tReport = tuple(np.where(report > 0)[0])
			if len(tReport) == 1:
				tReport = (tReport[0], tReport[0])
			targetMove = (tReport, tReport[: : -1])

		self.reportHistory.append(report)
		return (solveFlag, targetMove)

	#update temp report
	def updateReport(self, prob, targetMove, quick = False, force = False, temp = False):
		tempProb = np.zeros_like(prob, dtype = np.float16)
		#for each possible move
		for prev, post in targetMove:
			#for each possible prev block
			for row in range(self.b.rows):
				for col in range(self.b.cols):
					if self.b.cell[row, col] == prev:
						#update each possible post block
						index = tuple(np.where(self.b.border[row, col, post, :])[0])
						factor = len(index)
						if factor:
							nPos = ((row-1, col), (row, col-1), (row, col+1), (row+1, col))
							tempP = prob[row, col] / factor
							for i in index:
								tempProb[nPos[i]] = tempProb[nPos[i]] + tempP

		sumP = np.sum(tempProb)

		if not force and (self.quickRes or quick) and sumP > 0.5:
			if not temp:
				self.b.prob = tempProb
			return tempProb
		tempProb = self.normalizeP(tempProb, sumP)
		if not temp:
			self.b.prob = tempProb
		return tempProb

	#re-update all report
	def reUpdateReport(self, temp = False):
		history = list(map(lambda x: np.where(x)[0][0], self.targetHistory))
		tempProb = np.full((self.b.rows, self.b.cols), (1. / (self.b.rows * self.b.cols)), dtype = np.float16)
		for i in range(len(history) - 1):
			tempProb = self.updateP(tempProb, *self.searchHistory[i], quick = True, temp = temp)
			tempProb = self.updateReport(self.b.prob, ((history[i], history[i+1]), ), quick = True, temp = temp)

		if not temp:
			self.b.prob = tempProb
		return tempProb


	#tool functions
	#resize prob so that sum == 1
	def normalizeP(self, tempProb, sumP = None):
		if sumP is None:
			sumP = np.sum(tempProb)
		if sumP == 0:
			print('E: solution.normalizeP. zero sumP')
			exit()
		tempProb = tempProb / sumP
		return tempProb

	def moveTo(self, row, col):
		while self.b.hunter != (row, col):
			if self.b.hunter[0] < row:
				self.b.move(self.b.hunter[0] + 1, self.b.hunter[1])
				self.history.append((self.b.hunter, 'm'))
			elif self.b.hunter[0] > row:
				self.b.move(self.b.hunter[0] - 1, self.b.hunter[1])
				self.history.append((self.b.hunter, 'm'))
			if self.b.hunter[1] < col:
				self.b.move(self.b.hunter[0], self.b.hunter[1] + 1)
				self.history.append((self.b.hunter, 'm'))
			elif self.b.hunter[1] > col:
				self.b.move(self.b.hunter[0], self.b.hunter[1] - 1)
				self.history.append((self.b.hunter, 'm'))
		return

	def search(self, row, col):
		#move or teleport
		if self.b.moving:
			self.moveTo(row, col)

		#explore
		self.searchHistory.append((row, col))
		self.history.append(((row, col), 's'))
		return self.b.explore(row, col)

	#report tool functions
	#get temp target movement
	def solveTarget(self, report):
		diff = (report - self.targetHistory[-1]) > 0
		tTer = np.where(diff)
		tMove = (np.where(self.targetHistory[-1])[0][0], tTer[0][0])
		self.targetHistory.append(diff)
		return (tMove, )

	#translate reportHistory to targetHistory
	def backtrackReport(self, tPrevTer):
		tTer = tPrevTer > 0
		self.targetHistory.insert(0, tTer)
		reportList = self.reportHistory.copy()
		reportList.reverse()
		for report in reportList:
			tTer = (report - tTer) > 0
			self.targetHistory.insert(0, tTer)
		return


	#rule functions
	#get next block to search
	def getNext(self, row = None, col = None, rule = 3):
		if rule == 1:
			pos = self.maxProb(row, col)
		elif rule == 2:
			pos = self.maxSucP(row, col)
		elif rule == 3:
			pos = self.maxInfo(row, col)
		elif rule == 4:
			pos = self.minCost(row, col)
		else:
			print('E: solution.getNext. wrong rule number.')
			exit()
		return pos

	#rule 1
	def maxProb(self, row = None, col = None):
		value = self.b.prob
		pos = np.unravel_index(np.argmax(value), value.shape)
		return pos

	#rule 2
	def maxSucP(self, row = None, col = None):
		value = self.b.prob * self.b.sucP
		pos = np.unravel_index(np.argmax(value), value.shape)
		return pos

	#rule 3
	def maxInfo(self, row = None, col = None):
		tempSucP = self.b.prob * self.b.sucP
		tempSucQ = 1 - tempSucP
		searchInfo = tempSucP * np.log2(tempSucP) + tempSucQ * np.log2(tempSucQ) #there should be negative. use min to find max
		if self.b.targetMoving:
			pass #TODO: value = searchreportInfo
		else:
			value = searchInfo
		pos = np.unravel_index(np.argmin(value), value.shape) #use min instead
		return pos

	#rule 4
	def minCost(self, row = None, col = None):
		if row is None or col is None:
			pass

	#solver
	def solve(self):
		while not self.success:
			pos = self.getNext(*self.b.hunter, rule = self.rule)

			#explore
			self.success, report = self.search(*pos)
			self.doubleCount[pos] = self.doubleCount[pos] + 1
			

			if self.success:
				break

			#double check
			if self.double and self.b.cell[pos] < self.double and self.doubleCount[pos] >= self.doubleThreshold[self.b.cell[pos]]:
				self.updateP(self.b.prob, *pos)
				if self.b.targetMoving:
					self.updateR(self.b.prob, report)
				self.success, report = self.search(*pos)
				self.doubleCount[pos] = self.doubleCount[pos] + 1
				if self.success:
					break

			#update
			self.updateP(self.b.prob, *pos)
			if self.b.targetMoving:
				self.updateR(self.b.prob, report)


			#in case of too long loop
			if len(self.searchHistory) > self.maxIter:
				break

			# self.b.visualize()
		return

def foo(x):
	return np.where(x)[0][0]

if __name__ == '__main__':
	b = frame.board(size = 4, moving = True, targetMoving = False)
	p = player(b, double = 2, rule = 2)
	p.solve()
	print(p.history)
	temp = list(map(foo, p.targetHistory))
	print(temp)
	print(len(p.targetHistory))
	print(len(p.history))

	p.b.visualize()
# frame.py
functions of map
## class board()
landscape map
### member variables:
basic
```
int rows in [1 : inf]: board hight 
int cols in [1 : inf]: board width
tuple _target of (row, col): target is in (row, col)
tuple hunter of (row, col): hunter is in (row, col)
list terrainP with element of float p: accumulated probability p of a cell being this terrain or a "better" terrain
list failP with element of float p: P(fail to find in this terrain | target in this cell)
bool moving: 
	True: hunter have to move to search
	False: hunter can teleport
bool targetMoving:
	True: target will move when hunter performs searching
	False: target is stationary
bool search: 
	True: hunter is searching
	False: hunter is moving
```
board related
```
np.ndarray cell with shape = (rows, cols) dtype = np.uint8: block terrain
	0: flat(F)
	1: hilly(H)
	2: forest(J for jungle)
	3: cave(C)
np.ndarray sucP with shape = (rows, cols) dtype = np.float16: P(successfully find in this cell | target is in this cell)
np.ndarray border with shape = (rows, cols, 4, 4) dtype = np.bool: (row, col, terrain, index): 
	True: the index neigbor of (row, col) is terrain type
	False: is not
np.ndarray dist with shape = (rows, cols, rows, cols) dtype = np.uin8: (row, col, nRow, nCol): dist((row, col), (nRow, nCol))
```
knowledge base:
```
np.ndarray prob with shape = (rows, cols) dtype = np.float16: P(target is in this cell | observation untill now)
```
visualization related:
```
list targetHistory of element (row, col): target moving history
class tile.tile tile: visualization tool
```

### member functions
initialization
```
getTerrainP(): translate to accumulated probability
	in:
		list terrainP of element float p: p of being this terrain
buildTerrain(): initialize blocks
hideTarget(): initialize _target
getBorder(): initialize border
getDist(): initialize dist
```
tool functions
```
visualize(): print map
	in:
		int beacon [1 : inf]: interval of beacons; 0: no beacon
	out:
		PIL.Image image: board image
getNeighbor(): get neighbor of (row, col)
	in:
		int row:
		int col:
	out:
		list neighbor of element (nRow, nCol): (nRow, nCol) is valid neighbor
manhattan(): get distance from x to y
	in:
		tuple x of (row, col):
		tuple y of (row, col):
	out:
		int dist: manhattan distance from x to y
getBlockDist(): get distance from (row, col)
	in:
		int row:
		int col:
```
actions
```
explore(): search (row, col)
	in:
		int row:
		int col:
	out:
		bool res: 
			True: done! 
			False: not found
		np.ndarray report with shape = (4, ): target moving report
move(): move to (row, col)
	in:
		int row:
		int col:
targetMove(): target move to its neighbor
	out:
		np.ndarray report with shape = (4, ): target moving report
```

## boardFactory()
generate seedBoard-like boards
```
in:
	class frame.board seedBoard: provide baisc member variables
	int num in [1 : inf]: number of boards to be generated
	bool multiple:
		True: rebuild terrain and re-hide target
		False: just re-hide target
out:
	list boardList of element class frame.board b: generated boards
```

# solution.py
## class player()
player view
### member variables
basic
```
class frame.board b: terrain map
bool quickRes:
	True: less frequently to normalize prob, faster
	False: normalize prob every time, more precise
int double in [1 : 4]: cell types that need a double check. takes more steps but much fewer unsolvable boards
	False: no double check
int rule in [1 : 5]: search strategy
int maxIter in [1 : inf]: max search times in a board, boards exceed will be treated as unsolvable ones
bool success:
	True: done
	False: target have not been found
```
double check related:
```
np.ndarray doubleThreshold with shape = (rows, cols) dtype = np.uint8: if a cell searched more than this times, it should be double check
np.ndarray doubleCount with shape = (rows, cols) dtype = np.uint8: counter of search times for each block
```
report related
```
list reportHistory of element np.ndarray report: report list
list targetHistory of element np.ndarray target: terrain of target was in
list searchHistory of element tuple (row, col): searched block, used to re-update prob
```
visualization related
```
list history of element tuple (row, col, action): all actions have been performed
```

### member functions
update functions
```
updateP(): update prob after searching (row, col)
	in:
		np.ndarray prob:
		int row:
		int col:
		bool quick:
			True: skip normalization if sum(prob) > 0.5
			False: depand on quickRes
		bool force: override on quick
			True: force to normalization
			False: depand on quickRes
		bool temp:
			True:  this is a temp prob, and will not update b.prob
			False: update b.prob
	out:
		np.ndarray prob: updated prob
updateR(): update prob after receiving report
	in:
		np.ndarray prob:
		np.ndarray reprot:
		bool quick:
		bool force:
		bool temp:
	out:
		np.ndarray prob:
```
report related functions
```
solveReport(): translate report to possible moves
	in:
		np.ndarray report:
	out:
		bool solve Flag: 
			True: reportHistory can translate to targetHistory; 
			False: cannot translate
		tuple targetMove with element (prev, post): target move from prev to post
updateReport(): use targetMove to update prob
	in:
		np.ndarray prob:
		tuple targetMove:
		bool quick:
		bool force:
		bool temp:
	out:
		np.ndarray prob:
reUpdateReport(): use targetHistory and searchHistory to update prob
	in:
		bool temp:
	out:
		np.ndarray prob:
```
tool functions
```
normalizeP(): resize prob so that sum(prob) = 1
	in:
		np.ndarray tempProb:
		float sumP: sum(tempProb)
	out:
		np.ndarray prob:
moveTo(): hunter move to (row, col) step by step
	in:
		int row:
		int col:
search(): hunter move to (row, col) and explore it
	in:
		int row:
		int col:
	out:
		bool res:
		np.ndarray report:
solveTarget(): get temp target movement by using targetHistory
	in:
		np.ndarray report:
	out:
		tuple targetMove:
backtrackReprot(): translate reportHistory to targetHistory
	in:
		np.ndarray tPrevTer: first found common report
```
rule functions
```
getNext(): choose next block to search
	in:
		int row:
		int col:
		int rule in [1 : 5]:
	out:
		tuple pos: next block to search
maxProb(): rule 1
	in:
		int row:
		int col:
	out:
		tuple pos:
maxSucP(): rule 2
	in:
		int row:
		int col:
	out:
		tuple pos:
maxInfo(): choose the block which provides the largest mutual information, equivalent to rule 2
	in:
		int row:
		int col:
	out:
		tuple pos:
minMove(): dicount value by exponential of dist, for moving and not targetMoving
	in:
		int row:
		int col:
	out:
		tuple pos:
minCost(): minimize the expectation of steps for a given board, for moving and targetMoving
	in:
		int row:
		int col:
	out:
		tuple pos:
```
solver
```
solve(): use update and rule functions to solve a given board
```
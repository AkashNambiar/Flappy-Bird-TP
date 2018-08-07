
from tkinter import *
import random
import time

class Animal(object):
	def __init__(self, data, size, border):
		self.x = data.width//5
		self.y = data.height//2
		self.size = size
		self.speed = 5
		self.goingDown = True
		self.border = border
		self.smartJump = False
		self.jumpDistance = 50

		self.velocity = []
		for i in range(15, 0, -2):
			self.velocity.append(-i)
		self.velocityIndex = 0
		self.jumping = False

	def jump(self, data):
		if data.gameOver: return
		self.jumping = True
		self.velocityIndex = 0
		self.speed = 5

	def jumpAction(self):
		if self.jumping:
			self.y += self.velocity[self.velocityIndex]
			self.velocityIndex += 1
			if self.velocityIndex >= len(self.velocity):
				self.jumping = False
				self.velocityIndex = 0

	def obstacleCollision(self, obstacle, data):
		if data.invisibleObstacle: return
		top = obstacle.top
		bottom = obstacle.bottom
		halfSizeObstacle = (top.x2 - top.x1)/2
		obstacleCX = halfSizeObstacle + (top.x2 - top.x1)/2 + top.x1
		collidedTop = abs(obstacleCX - self.x) < self.size//2 + halfSizeObstacle and top.y2 > self.y - self.size//2
		collidedBottom = abs(obstacleCX - self.x) < self.size//2 + halfSizeObstacle and bottom.y1 < self.y - self.size//2
		return collidedTop or collidedBottom

	def itemCollision(self, item):
		dx = self.x - item.x
		dy = self.y - item.y
		return (dx**2 + dy**2)**0.5 < self.size + item.size

	def smartJumpAction(self, data):
		for obstacle in data.obstacles:
			if obstacle.passed == False:
				self.y = obstacle.getCenterY()
				break
		#nextObstacle = 
		#distanceToCenter = abs(nextObstacle.getCenter() - self.y)
		
		#self.smartJumpAction(data.obstacles[1])

	def onTimerFired(self, data):
		if data.animal.smartJump: 
			self.smartJumpAction(data)
			return
		self.jumpAction()
		self.y += self.speed
		self.speed = self.speed**1.03
		if self.y > data.height - self.size//2 - self.border: 
			self.y = data.height - self.size//2 -self.border
			self.speed = 5
		if self.y < self.size//2 + self.border: 
			self.y = self.size//2 + self.border

	def draw(self, canvas, data):
		x, y, size = self.x, self.y, self.size
		canvas.create_oval(x - size//2, y - size//2, x + size//2, y + size//2, width = 0)
		canvas.create_image(x, y, anchor = CENTER, image = data.animalImage)

class Obstacle(object):
	def __init__(self, data, x, y, endHeight, gap = 150, obstacleWidth = 25):
		self.top = ObstaclePart(x ,y, obstacleWidth, endHeight)
		self.bottom = ObstaclePart(x ,y + endHeight + gap, obstacleWidth, data.height)
		self.passed = False

	def __repr__(self):
		return "%s" % self.passed

	def draw(self, canvas, data):
		obstacleT, obstacleB = data.topObstacle, data.bottomObstacle
		if data.invisibleObstacle:
			obstacleT, obstacleB = data.topObstacleClear, data.bottomObstacleClear

		self.top.draw(canvas, data, obstacleT, SE)
		self.bottom.draw(canvas, data, obstacleB, NW)

	def getCenterX(self):
		return (self.top.x1 + self.top.x2)/2

	def getCenterY(self):
		return (self.top.y2 + self.bottom.y1)/2

	def onTimerFired(self, data):
		self.top.onTimerFired(data, self)
		self.bottom.onTimerFired(data, self)

		if data.animal.x > self.getCenterX() + data.topObstacle.width() and self.passed == False:
			data.score += 1
			self.passed = True

		if self.top.x2 < 0: 
			return "Off Screen"
		if data.animal.obstacleCollision(self, data):
			return "Bird Hit"

class ObstaclePart(object):
	def __init__(self, x, y, obstacleWidth, obstacleHeight):
		self.x1 = x
		self.y1 = y
		self.x2 = x + obstacleWidth
		self.y2 = y + obstacleHeight

	def getCenterX(self):
		return (self.x2 + self.x1)/2

	def draw(self, canvas, data, obstacleType, anchor):
		canvas.create_rectangle(self.x1 , self.y1, self.x2, self.y2, width = 0)
		x, y = self.x2, self.y2
		if anchor == NW: x, y = self.x1, self.y1
		
		canvas.create_image(x, y, anchor = anchor, image = obstacleType)

	def onTimerFired(self, data, entireObstacle):
		if data.gameOver: data.itemMove = 0
		self.x1 -= data.itemMove
		self.x2 -= data.itemMove

class GameItem(object):
	def __init__(self, x, y, size):
		self.x = x
		self.y = y
		self.size = size

	def draw(self, canvas, data):
		canvas.create_image(self.x, self.y, anchor = CENTER, image = data.coin)

	def onTimerFired(self, data):
		self.x -= data.itemMove
		if data.animal.itemCollision(self):
			return "Collected"

def init(data):
	animalImageFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/bunny1.gif"
	data.animalImage = PhotoImage(file = animalImageFile)

	topObstacleFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstacletop.gif"
	data.topObstacle = PhotoImage(file = topObstacleFile)

	bottomObstacleFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstaclebottom.gif"
	data.bottomObstacle = PhotoImage(file = bottomObstacleFile)

	topObstacleClearFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstacletopClear.gif"
	data.topObstacleClear = PhotoImage(file = topObstacleClearFile)

	bottomObstacleClearFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstaclebottomClear.gif"
	data.bottomObstacleClear = PhotoImage(file = bottomObstacleClearFile)

	backgroundFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/background.gif"
	data.background = PhotoImage(file = backgroundFile)

	groundFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/ground.gif"
	data.ground = PhotoImage(file = groundFile)

	groundFlippedFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/groundFlip.gif"
	data.groundFlipped = PhotoImage(file = groundFlippedFile)

	restartFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/restart.gif"
	data.restart = PhotoImage(file = restartFile)

	coinFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/coin.gif"
	data.coin = PhotoImage(file = coinFile, format="gif -index 4")

	data.animal = Animal(data, 40, data.ground.height())

	data.obstacles = []
	data.obstaclesImages = []

	data.gameItems = []

	data.timer = 0
	data.timerDelay = 30

	data.obstacleDistance = 300
	data.itemMove = 5

	data.score = 0

	data.gameOver = False
	data.arcadeMode = True

	data.invisibleObstacle = False
	data.timeInvisbleCounter = 0
	data.timeInvisble = 3 * (1000 / data.timerDelay)

	newObstacle(data)

def mousePressed(event, data):
	pass

def keyPressed(event, data):
	key = event.keysym
	if key == "Up":
		data.animal.jump(data)
	elif key == "r":
		init(data)
	elif key == "a":
		data.animal.smartJump = True

def timerFired(data):
	if data.gameOver: 
		data.animal.onTimerFired(data)
	else:
		data.animal.onTimerFired(data)
	
	data.timer += 1

	if data.invisibleObstacle:
		data.timeInvisbleCounter += 1

		if data.timeInvisbleCounter > data.timeInvisble:
			data.timeInvisbleCounter = 0
			data.invisibleObstacle = False

	if data.obstacles[len(data.obstacles) - 1].top.x1 < data.width - data.obstacleDistance:
		newObstacle(data)

	for obstacle in data.obstacles:
		gameState = obstacle.onTimerFired(data)
		if gameState == "Off Screen":
			index = data.obstacles.index(obstacle)
			data.obstacles.remove(obstacle)
			break
		elif gameState == "Bird Hit":
			data.gameOver = True	

	for gameItem in data.gameItems:
		if gameItem.onTimerFired(data) == "Collected":
			data.gameItems.remove(gameItem)
			data.invisibleObstacle = True
			data.t = time.time()

def redrawAll(canvas, data):
	drawBackground(canvas, data)
	
	for obstacle in data.obstacles:
		obstacle.draw(canvas, data)
	
	for gameItem in data.gameItems:
		gameItem.draw(canvas, data)
	
	drawBorders(canvas, data)
	
	data.animal.draw(canvas, data)
	
	if data.gameOver:
		drawRestart(canvas, data)

def newObstacle(data):
	if data.gameOver: return
	data.obstacles.append(Obstacle(data, data.width, 0, random.randint(100, data.height - 200)))

	newGameItem(data, data.width + data.obstacleDistance/2)

def newGameItem(data, x):
	if data.gameOver: return
	data.gameItems.append(GameItem(x, random.randint(100, data.height - 100), data.coin.height()/4))

def drawBorders(canvas, data, thickness = 30):
	#canvas.create_image(0, 0, anchor = NW, image = data.groundFlipped)
	canvas.create_image(0, data.height - thickness, anchor = NW, image = data.ground)
	#canvas.create_rectangle(0, 0, data.width, thickness, width = 0)
	canvas.create_rectangle(0, data.height - thickness, data.width, data.height, width = 0)

def drawBackground(canvas, data):
	canvas.create_image(0, 0, anchor = NW, image = data.background)

def drawRestart(canvas, data):
	canvas.create_image(data.width//2, data.height//2, anchor = CENTER, image = data.restart)



def run(width=300, height=300):
	def redrawAllWrapper(canvas, data):
		canvas.delete(ALL)
		canvas.create_rectangle(0, 0, data.width, data.height,
								fill='white', width=0)
		redrawAll(canvas, data)
		canvas.update()

	def mousePressedWrapper(event, canvas, data):
		mousePressed(event, data)
		redrawAllWrapper(canvas, data)

	def keyPressedWrapper(event, canvas, data):
		keyPressed(event, data)
		redrawAllWrapper(canvas, data)

	def timerFiredWrapper(canvas, data):
		timerFired(data)
		redrawAllWrapper(canvas, data)
		# pause, then call timerFired again
		canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
	# Set up data and call init
	class Struct(object): pass
	data = Struct()
	data.width = width
	data.height = height
	data.timerDelay = 100 # milliseconds
	root = Tk()
	init(data)
	# create the root and the canvas
	canvas = Canvas(root, width=data.width, height=data.height)
	canvas.configure(bd=0, highlightthickness=0)
	canvas.pack()
	# set up events
	root.bind("<Button-1>", lambda event:
							mousePressedWrapper(event, canvas, data))
	root.bind("<Key>", lambda event:
							keyPressedWrapper(event, canvas, data))
	timerFiredWrapper(canvas, data)
	# and launch the app
	root.mainloop()  # blocks until window is closed

run(600, 600)


from tkinter import *
import random

class Animal(object):
	def __init__(self, data, size, border):
		self.x = data.width//5
		self.y = data.height//2
		self.size = size
		self.speed = 5
		self.goingDown = True
		self.border = border

	def jump(self, data, dy = 50):
		if data.gameOver: return
		self.y -= dy
		self.speed = 5

	def jumpAction(self):
		pass

	def collisionCheck(self, obstacle):
		top = obstacle.top
		bottom = obstacle.bottom
		halfSizeObstacle = (top.x2 - top.x1)/2
		obstacleCX = halfSizeObstacle + (top.x2 - top.x1)/2 + top.x1
		collidedTop = abs(obstacleCX - self.x) < self.size//2 + halfSizeObstacle and top.y2 > self.y - self.size//2
		collidedBottom = abs(obstacleCX - self.x) < self.size//2 + halfSizeObstacle and bottom.y1 < self.y - self.size//2
		return collidedTop or collidedBottom

	def onTimerFired(self, data):
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

	def draw(self, canvas, data):
		self.top.draw(canvas, data, data.topObstacle, SE)
		self.bottom.draw(canvas, data, data.bottomObstacle, NW)

	def onTimerFired(self, data):
		self.top.onTimerFired(data)
		self.bottom.onTimerFired(data)
		if self.top.x2 < 0: 
			return "Off Screen"
		if data.animal.collisionCheck(self):
			return "Bird Hit"

class ObstaclePart(object):
	def __init__(self, x, y, obstacleWidth, obstacleHeight):
		self.x1 = x
		self.y1 = y
		self.x2 = x + obstacleWidth
		self.y2 = y + obstacleHeight

	def draw(self, canvas, data, obstacleType, anchor):
		canvas.create_rectangle(self.x1 , self.y1, self.x2, self.y2, width = 0)
		x, y = self.x2, self.y2
		if anchor == NW: x, y = self.x1, self.y1
		canvas.create_image(x, y, anchor = anchor, image = obstacleType)

	def onTimerFired(self, data):
		dx = 5
		if data.gameOver: dx = 0
		self.x1 -= dx
		self.x2 -= dx

def init(data):
	animalImageFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/bunny1.gif"
	data.animalImage = PhotoImage(file = animalImageFile)

	topObstacleFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstacletop.gif"
	data.topObstacle = PhotoImage(file = topObstacleFile)

	bottomObstacleFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/obstaclebottom.gif"
	data.bottomObstacle = PhotoImage(file = bottomObstacleFile)

	backgroundFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/background.gif"
	data.background = PhotoImage(file = backgroundFile)

	groundFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/ground.gif"
	data.ground = PhotoImage(file = groundFile)

	groundFlippedFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/groundFlip.gif"
	data.groundFlipped = PhotoImage(file = groundFlippedFile)

	restartFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/restart.gif"
	data.restart = PhotoImage(file = restartFile)

	data.animal = Animal(data, 40, data.ground.height())
	data.obstacles = []
	data.obstaclesImages = []
	data.timer = 0
	data.timerDelay = 40
	data.obstacleGen = data.timerDelay
	data.gameOver = False
	data.score = 0

def mousePressed(event, data):
	pass

def keyPressed(event, data):
	key = event.keysym
	if key == "Up":
		data.animal.jump(data)
	elif key == "r":
		init(data)

def timerFired(data):
	if data.gameOver: 
		data.animal.onTimerFired(data)
	else:
		data.animal.onTimerFired(data)
	
	data.timer += 1

	if data.timer % data.obstacleGen == 0: 
		newObstacle(data)

	for obstacle in data.obstacles:
		gameState = obstacle.onTimerFired(data)
		if gameState == "Off Screen":
			data.obstacles.remove(obstacle)
			break
		elif gameState == "Bird Hit":
			data.gameOver = True	

def redrawAll(canvas, data):
	drawBackground(canvas, data)
	for obstacle in data.obstacles:
		obstacle.draw(canvas, data)
	drawBorders(canvas, data)
	data.animal.draw(canvas, data)
	if data.gameOver:
		drawRestart(canvas, data)

def newObstacle(data, dx = 50):
	if data.gameOver: return
	data.obstacles.append(Obstacle(data, data.width, 0, random.randint(100, data.height - 200)))

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
    print("bye!")

run(600, 600)

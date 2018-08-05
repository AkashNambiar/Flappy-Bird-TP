
from tkinter import *
import random

class Bird(object):
	def __init__(self, data, size):
		self.x = data.width//5
		self.y = data.height//2
		self.size = size
		self.speed = 10
		self.goingDown = True

	def jump(self, dy = 50):
		self.y -= dy
		self.speed = 10

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
		self.speed = self.speed**1.05
		if self.y > data.height - self.size//2: self.y = data.height - self.size//2
		if self.y < self.size//2: self.y = self.size//2

	def draw(self, canvas):
		x, y, size = self.x, self.y, self.size
		canvas.create_oval(x - size//2, y - size//2, x + size//2, y + size//2)

class Obstacle(object):
	def __init__(self, data, x, y, endHeight, gap = 150, obstacleWidth = 25):
		self.top = ObstaclePart(x ,y, obstacleWidth, endHeight)
		self.bottom = ObstaclePart(x ,y + endHeight + gap, obstacleWidth, data.height)

	def draw(self, canvas):
		self.top.draw(canvas)
		self.bottom.draw(canvas)

	def onTimerFired(self, data):
		self.top.onTimerFired(data)
		self.bottom.onTimerFired(data)
		if self.top.x2 < 0: 
			return "Off Screen"
		if data.bird.collisionCheck(self):
			return "Bird Hit"

class ObstaclePart(object):
	def __init__(self, x, y, obstacleWidth, obstacleHeight):
		self.x1 = x
		self.y1 = y
		self.x2 = x + obstacleWidth
		self.y2 = y + obstacleHeight

	def draw(self, canvas):
		canvas.create_rectangle(self.x1 , self.y1, self.x2, self.y2, fill = "black")

	def onTimerFired(self, data):
		self.x1 -= 5
		self.x2 -= 5

def init(data):
	data.bird = Bird(data, 40)
	data.obstacles = []
	data.timer = 0
	data.timerDelay = 40
	data.obstacleGen = data.timerDelay
	data.gameOver = False

def mousePressed(event, data):
	pass

def keyPressed(event, data):
	key = event.keysym
	if key == "Up":
		data.bird.jump()

def timerFired(data):
	if data.gameOver: return
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
	data.bird.onTimerFired(data)

def redrawAll(canvas, data):
	for obstacle in data.obstacles:
		obstacle.draw(canvas)
	data.bird.draw(canvas)
	drawBorders(canvas, data)

def newObstacle(data):
	data.obstacles.append(Obstacle(data, data.width, 0, random.randint(100, 200)))

def drawBorders(canvas, data, thickness = 30):
	canvas.create_rectangle(0, 0, data.width, thickness, fill = "black")
	canvas.create_rectangle(0, data.height - thickness, data.width, data.height, fill = "black")

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
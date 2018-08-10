
from tkinter import *
import random
import time

#################################################
#################################################

class Animal(object):
	def __init__(self, data, size, border):
		self.x = data.width//5
		self.y = data.height//2
		self.size = size
		
		self.speed = 5
		self.fallVelocity = 1

		self.border = border
		self.smartJump = False
		self.jumpDistance = 50

		self.velocity = []
		for i in range(20, 0, -3):
			self.velocity.append(-i)
		self.velocityIndex = 0
		self.jumping = False

		self.possibleMoves = ["Jump", "Wait"]

		self.foundMove = [False, None, None]

		self.jumpMoves = 0
		self.t = 0
		self.a = 0
		self.f = False

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

	def obstacleCollision(self, obstacle, data, x, y):
		if data.invisibleObstacle: return
		top = obstacle.top
		bottom = obstacle.bottom
		size = data.animalImage.width()//2
		
		collidedTop = abs(top.x1 - x) < size and top.y2 > y - size
		collidedBottom = abs(bottom.x1 - x) < size and bottom.y1 < y + size
		return collidedTop or collidedBottom

	def itemCollision(self, item):
		dx = self.x - item.x
		dy = self.y - item.y
		return (dx**2 + dy**2)**0.5 < self.size + item.image.width()//2

	#################################################

	def smartJumpAction(self, data):
		if data.gameOver: return
		if self.t != 0: 
			self.t -= 1
			if self.jumpMoves != 0:
				self.y += self.velocity[0]
				self.jumpMoves -= 1
				self.speed = self.fallVelocity
			self.f = True
			return
		elif self.t == - 4 and self.f:
			self.y += self.velocity[0]

		for obstacle in data.obstacles:
			if not obstacle.passed:
		 		x, y = obstacle.getCenterX(), (obstacle.top.y2 + obstacle.bottom.y1)/2
		 		if self.y < y:
		 			pass
		 		else:
		 			distanceToY = abs(self.y - y)
		 			jumpHeight = abs(self.velocity[0]) + self.fallVelocity 
		 			numberOfJumps = distanceToY // jumpHeight 
		 			self.jumpMoves = numberOfJumps
		 			self.t = self.jumpMoves
		 			self.a = 0
		 		return
	
	#BackTracking --> ineffecient

	# def jumpMove(self, data, obstacle, startX, startY, moves = []):
	# 	endingPosition = self.executeJumpMoves(data, obstacle, startX, startY, moves)

	# 	for move in self.possibleMoves:
	# 		moves.append(move)
	# 		temp = self.jumpMove(data, obstacle, startX, startY, moves)
	# 		if temp != None:
	# 			return moves
	# 		moves.remove(move)
	# 	return None

	# def possibleJumpMoves(self, data, obstacle, startX, startY, moves):
	# 	for move in moves:
	# 		if move == "Jump":
	# 			startY += sum(self.velocity)
	# 			startX += data.itemMove * len(self.velocity)
	# 		else:
	# 			speed = self.speed
	# 			for i in range(len(self.velocity)):
	# 				startX += data.itemMove
	# 				startY += speed
	# 				speed += self.fallVelocity

	# 				if startY > data.height - self.size//2 - self.border: 
	# 					startY = data.height - self.size//2 -self.border
	# 					speed = self.speed

	# 				if startY < self.size//2 + self.border: 
	# 					startY = self.size//2 + self.border
	# 					speed = self.speed

	# 			if startX > obstacle.getCenterX() + data.topObstacle.width() and self.obstacleCollision(obstacle, data, startX, startY):
	# 				print(moves)
	# 				return moves
	# 	return None							
	#################################################

	def onTimerFired(self, data):
		if data.animal.smartJump: 
			self.smartJumpAction(data)
			
		self.jumpAction()
		self.y += self.speed
		self.speed += self.fallVelocity

		if self.y > data.height - self.size//2 - self.border: 
			self.y = data.height - self.size//2 -self.border
			self.speed = 5

		if self.y < self.size//2: 
			self.y = self.size//2
			self.speed = 5

	def draw(self, canvas, data):
		x, y, size = self.x, self.y, self.size
		canvas.create_oval(x - size//2, y - size//2, x + size//2, y + size//2, width = 0)
		canvas.create_image(x, y, anchor = CENTER, image = data.animalImages[data.animalImageIndex])
		data.animalImageIndex += 1
		if data.animalImageIndex >= len(data.animalImages):
			data.animalImageIndex = 0

#################################################
#################################################

class Obstacle(object):
	def __init__(self, data, x, y, endHeight, gap, obstacleWidth = 25):
		self.top = ObstaclePart(x, y, obstacleWidth, endHeight)
		self.bottom = ObstaclePart(x ,y + endHeight + gap, obstacleWidth, data.height)
		self.passed = False

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

	def move(self, data):
		self.top.onTimerFired(data)
		self.bottom.onTimerFired(data)

	def onTimerFired(self, data):
		self.move(data)

		if data.animal.x > self.getCenterX() + data.topObstacle.width() and self.passed == False:
			data.score += 1
			self.passed = True

		if self.top.x2 < 0: 
			index = data.obstacles.index(self)
			data.obstacles.remove(self)
		if data.animal.obstacleCollision(self, data, data.animal.x, data.animal.y):
			data.gameOver = True

#################################################
#################################################

class MovingObstacle(Obstacle):
	def __init__(self, data, x, y, startingEndHeight, gap, moveSpeed):
		super().__init__(data, x, y, startingEndHeight, gap)
		self.moveSpeed = moveSpeed

	def move(self, data):
		self.top.move(data, data.itemMove, self.moveSpeed)
		self.bottom.move(data, data.itemMove, self.moveSpeed)
		if 50 > self.top.y2 or self.bottom.y1 > data.height - 50:
			self.moveSpeed = - self.moveSpeed

#################################################
#################################################

class ObstaclePart(object):
	def __init__(self, x, y, obstacleWidth, obstacleHeight):
		self.x1 = x
		self.y1 = y
		self.x2 = x + obstacleWidth
		self.y2 = y + obstacleHeight

	def getCenterX(self):
		return (self.x2 + self.x1)/2

	def move(self, data, x, y):
		if data.gameOver: x = 0
		self.x1 -= x
		self.x2 -= x
		self.y1 -= y
		self.y2 -= y

	def draw(self, canvas, data, obstacleType, anchor):
		canvas.create_rectangle(self.x1 , self.y1, self.x2, self.y2, width = 0)
		x, y = self.x2, self.y2
		if anchor == NW: x, y = self.x1, self.y1
		canvas.create_image(x, y, anchor = anchor, image = obstacleType)

	def onTimerFired(self, data):
		self.move(data, data.itemMove, 0)

#################################################
#################################################

class Border(object):
	def __init__(self, x, y, image):
		self.x = x
		self.y = y
		self.image = image

	def move(self, data, dx = 0, dy = 0):
		if data.gameOver: 
			dx, dy = 0, 0
		self.x -= dx
		self.y -= dy

	def draw(self, canvas, data):
		canvas.create_image(self.x, self.y, anchor = NW, image = data.ground)
		canvas.create_rectangle(self.x, self.y, self.x + self.image.width(), self.y + self.image.height(), width = 0)

#################################################
#################################################

class GameItem(object):
	def __init__(self, x, y, image, itemType):
		self.x = x
		self.y = y
		self.image = image
		self.itemType = itemType

	def draw(self, canvas, data):
		canvas.create_image(self.x, self.y, anchor = CENTER, image = self.image)

	def onTimerFired(self, data):
		if data.gameOver: self.x += data.itemMove
		self.x -= data.itemMove
		if data.animal.itemCollision(self):
			if self.itemType == "Invisble":
				data.invisibleObstacle = True
				data.startTimeInvisble = time.time()
			elif self.itemType == "Increase":
				data.gapIncrease = True
				data.gapIncreaseStartTime = time.time()
				data.gap = 250
				for obstacle in data.obstacles:
					if obstacle.passed == False:
						obstacle.gap = data.gap
			data.gameItems.remove(self)

#################################################
#################################################

def init(data):
	animalImageFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/bunny1.gif"
	data.animalImage = PhotoImage(file = animalImageFile)

	animalImageFile2 = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/bunny2.gif"
	data.animalImage2 = PhotoImage(file = animalImageFile2)

	data.animalImages = 7*[data.animalImage]+ 7*[data.animalImage2]

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

	invisbleFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/invisble.gif"
	data.invisble = PhotoImage(file = invisbleFile)

	increaseFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/increase.gif"
	data.increase = PhotoImage(file = increaseFile)

	matFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/mat.gif"
	data.mat = PhotoImage(file = matFile)

	matFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/mat.gif"
	data.mat = PhotoImage(file = matFile)

	playFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/play.gif"
	data.play = PhotoImage(file = playFile)

	cloudsFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/clouds.gif"
	data.clouds = PhotoImage(file = cloudsFile)

	helpFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/help.gif"
	data.help = PhotoImage(file = helpFile)

	level1File = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/level1.gif"
	data.level1 = PhotoImage(file = level1File)

	level2File = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/level2.gif"
	data.level2 = PhotoImage(file = level2File)

	arcadeOnFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/arcadeOn.gif"
	data.arcadeOn = PhotoImage(file = arcadeOnFile)

	arcadeOffFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/arcadeOff.gif"
	data.arcadeOff = PhotoImage(file = arcadeOffFile)

	helpMenuFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/helpMenu.gif"
	data.helpMenuImage = PhotoImage(file = helpMenuFile)

	backgroundHelpFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/backgroundHelp.gif"
	data.backgroundHelp = PhotoImage(file = backgroundHelpFile)

	crystalsFile = "/Users/Akash/Documents/CMU Summer/15-112/Final Project/Images/crystals.gif"
	data.crystals = PhotoImage(file = crystalsFile)

	data.animal = Animal(data, 48, data.ground.height())

	data.obstacles = []
	data.obstaclesImages = []

	data.gameItems = []
	data.allGameItems = [data.invisble, data.increase]
	data.allGameItemTypes = ["Invisble", "Increase"]

	data.borders = []

	data.timer = 0
	data.timerDelay = 30

	data.obstacleDistance = 275
	data.itemMove = 5

	data.score = 0

	data.gameOver = False
	data.arcadeMode = True
	data.arcade = data.arcadeOff
	data.movingObstacles = False

	data.invisibleObstacle = False
	data.startTimeInvisble = time.time()
	data.timeInvisble = 5

	data.gap = 150
	data.gapIncrease = False
	data.gapIncreaseStartTime = time.time()
	data.gapIncreaseTime = 5

	data.animalImageIndex = 0

	data.gameStart = False
	data.oneTimeStart = True
	data.levelSelect = False

	data.helpMenu = False

	data.loadingAnimal = Animal(data, 40, data.ground.height())
	data.loadingAnimal.x = 0
	data.loadingAnimal.y = data.height - data.ground.height() - data.animalImage.height()//2

#################################################

def mousePressed(event, data):
	x, y = event.x, event.y

	if data.helpMenu:
		if x < data.width//2 - data.helpMenuImage.width()//2 or data.width//2 + data.helpMenuImage.width()//2 < x \
			 or y < data.height//2 - data.helpMenuImage.height()//2 or data.height//2 + data.helpMenuImage.height()//2 < y:
				data.helpMenu = False
		return

	if data.gameOver:
		if 

	if data.levelSelect:
		if data.width//2 - data.level1.width()//2 < x < data.width//2 + data.level1.width()//2:
			if data.height//4 - 25 - data.level1.height()//2 < y < data.height//4 - 25 +data.level1.height()//2:
				if data.arcade == data.arcadeOff:
					data.arcadeMode = False
				else:
					data.arcadeMode = True
				data.movingObstacles = False
				data.gameStart = True
				return

		if data.width//2 - data.level1.width()//2 < x < data.width//2 + data.level1.width()//2:
			if data.height//2 - 25 - data.level1.height()//2 < y < data.height//2 - 25 +data.level1.height()//2:
				if data.arcade == data.arcadeOff:
					data.arcadeMode = False
				else:
					data.arcadeMode = True
				data.movingObstacles = True
				data.gameStart = True
				return

		if data.width//2 - data.level1.width()//2 < x < data.width//2 + data.level1.width()//2:
			if 3*data.height//4 - 25 - data.level1.height()//2 < y < 3*data.height//4 - 25 +data.level1.height()//2:
				if data.arcade == data.arcadeOff:
					data.arcade = data.arcadeOn
				else:
					data.arcade = data.arcadeOff
				return
		data.levelSelect = False
		return

	if not data.gameStart or not data.helpMenu:
		if data.width//2 - data.play.width()//2 < x < data.width//2 + data.play.width()//2:
			if data.height//2 - data.play.height() < y < data.height//2:
				data.levelSelect = True
				return
		if data.width//2 - data.help.width()//2 < x < data.width//2 + data.help.width()//2:
			if 2*data.height//3 - data.play.height()//2 < y < 2*data.height//3 + data.play.height()//2:
				data.helpMenu = True
				return

#################################################

def keyPressed(event, data):
	key = event.keysym
	if key == "Up" or key == "space":
		data.animal.jump(data)
	elif key == "r":
		movingObstacles = data.movingObstacles
		arcadeMode = data.arcadeMode
		init(data)
		data.gameStart = True
		data.arcadeMode = arcadeMode
		data.movingObstacles = movingObstacles
	elif key == "a":
		data.animal.smartJump = not data.animal.smartJump

#################################################

def timerFired(data):

	if not data.gameStart: return

	if data.oneTimeStart:
		newObstacle(data)
		newBorder(data, 0)
		newBorder(data, data.width)
		data.oneTimeStart = False

	if data.gameOver: 
		data.animal.onTimerFired(data)
	else:
		data.animal.onTimerFired(data)
	
	data.timer += 1

	if data.invisibleObstacle and time.time() - data.startTimeInvisble > data.timeInvisble:
		data.invisibleObstacle = False

	if data.gapIncrease and time.time() - data.gapIncreaseStartTime > data.gapIncreaseTime:
		data.gapIncrease = False
		data.gap = 150

	if data.obstacles[len(data.obstacles) - 1].top.x1 < data.width - data.obstacleDistance:
		newObstacle(data)

	for obstacle in data.obstacles:
		obstacle.onTimerFired(data)

	for gameItem in data.gameItems:
		gameItem.onTimerFired(data)

	for border in data.borders:
		border.move(data, data.itemMove)
		if border.x + border.image.width() <= 0:
			data.borders.remove(border)
			break

	lastBorder = data.borders[len(data.borders) - 1]
	if lastBorder.x + lastBorder.image.width() <= data.width:
		newBorder(data, data.width)

#################################################

def redrawAll(canvas, data):

	drawBackground(canvas, data)
	
	if not data.gameStart: 
		canvas.create_image(0, data.height, anchor = SW, image = data.ground)
		canvas.create_image(data.width//2, 2*data.height//3, anchor = CENTER, image = data.help)
		
		canvas.create_image(data.width//2, data.height//2, anchor = S, image = data.play)
		data.loadingAnimal.draw(canvas, data)
		data.loadingAnimal.x = (data.loadingAnimal.x + 5) % data.width
		if data.helpMenu:
			canvas.create_image(data.width//2, data.height//2, anchor = CENTER, image = data.helpMenuImage)

		if data.levelSelect:
			canvas.create_image(data.width//2, data.height//2 - 25, anchor = CENTER, image = data.backgroundHelp)
			canvas.create_image(data.width//2, data.height//4 - 25, anchor = CENTER, image = data.level1)
			canvas.create_image(data.width//2, data.height//2 - 25, anchor = CENTER, image = data.level2)
			canvas.create_image(data.width//2, 3*data.height//4 - 25, anchor = CENTER, image = data.arcade)
		return

	for obstacle in data.obstacles:
		obstacle.draw(canvas, data)
	
	for gameItem in data.gameItems:
		gameItem.draw(canvas, data)

	for border in data.borders:
		border.draw(canvas, data)
	
	data.animal.draw(canvas, data)

	drawMat(canvas, data)

	if data.gameOver:
		drawRestart(canvas, data)

#################################################

def newObstacle(data):
	if data.gameOver: return
	obstacleY = random.randint(data.ground.height() + 50, data.height//2)
	if data.movingObstacles:
		if random.randint(1,3) != 1:
			data.obstacles.append(Obstacle(data, data.width, 0, obstacleY, data.gap))
		else:
			data.obstacles.append(MovingObstacle(data, data.width, 0, obstacleY, data.gap, -5))
	else:
		data.obstacles.append(Obstacle(data, data.width, 0, obstacleY, data.gap))

	if data.arcadeMode:
		if random.randint(1,1) == 1:
			newGameItem(data, data.width + data.obstacleDistance/2)

def newBorder(data, x):
	if data.gameOver: return
	data.borders.append(Border(x, data.height - data.ground.height(), data.ground))

def newGameItem(data, x):
	if data.gameOver: return
	itemIndex = random.randint(0, len(data.allGameItems) - 1)
	item = data.allGameItems[itemIndex]
	itemType = data.allGameItemTypes[itemIndex]
	data.gameItems.append(GameItem(x, random.randint(100, data.height - 100), item, itemType))

#################################################

def drawBackground(canvas, data):
	canvas.create_image(0, 0, anchor = NW, image = data.background)
	canvas.create_image(data.width//2, data.height//4, anchor = CENTER, image = data.clouds)
	canvas.create_image(data.width//2, data.height - data.ground.height(), anchor = S, image = data.crystals)

def drawRestart(canvas, data):
	canvas.create_image(data.width//2, data.height//2 - 20, anchor = CENTER, image = data.restart)
	canvas.create_image(data.width//2, data.height//2 + data.restart.height()/2, anchor = N, image = data.mat)
	canvas.create_text(data.width//2, data.height//2 + data.restart.height()/2 + data.mat.height()/2 - 5, 
		text = str(data.score), fill = "Purple", font = "Komika 40 bold")

def drawMat(canvas, data):
	if data.gameOver: return
	canvas.create_image(data.width, 0, anchor = NE, image = data.mat)
	canvas.create_text(data.width - data.mat.width()//2, data.mat.height()//4 + 5, text = str(data.score), fill = "white",
		font = "Komika 28")
	if data.invisibleObstacle:
		x = abs(data.startTimeInvisble - time.time())/data.timeInvisble
		canvas.create_rectangle(data.width - 3*data.mat.width()//4, data.mat.height()//2, 
			data.width - (data.mat.width()//4) - x*data.mat.width()//2, 7*data.mat.height()//12, fill = "lightblue")
	if data.gapIncrease:
		x = abs(data.gapIncreaseStartTime - time.time())/data.gapIncreaseTime
		canvas.create_rectangle(data.width - 3*data.mat.width()//4, 2*data.mat.height()//3, 
			data.width - (data.mat.width()//4) - x*data.mat.width()//2, 3*data.mat.height()//4 , fill = "pink")

#################################################
#################################################

#Tk Demos Start:
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
#Tk Demos End:

run(600, 600)

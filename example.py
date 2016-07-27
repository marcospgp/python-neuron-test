# Experimenting with a neural network consisting of a single neuron

import random
import time
from tkinter import *

class Perceptron:

	def __init__ (self, numberOfInputs):

		self.weights = [None] * numberOfInputs
		self.learningConstant = 0.01

		for i in range(0, numberOfInputs):
			self.weights[i] = random.uniform(-1, 1)

	def activate (self, sum):
		return (sum > 0)

	def feedForward (self, inputs):
		sum = 0
		for i in range(0, len(self.weights)):
			sum += inputs[i] * self.weights[i]

		return self.activate(sum)

	def train (self, inputs, desired):

		guess = self.feedForward(inputs)
		error = desired - guess

		for i in range(0, len(self.weights)):
			self.weights[i] += self.learningConstant * error * inputs[i]

class Renderer:

	def __init__ (self, width, height, xBound, yBound, perceptron):
		self.windowHasBeenDestroyed = False
		self.points = []
		self.width = width
		self.height = height
		self.xBound = xBound
		self.yBound = yBound
		self.perceptron = perceptron
		self.perceptronLine = None

		self.window = Tk()
		self.window.title('Neural Network Test')
		self.canvas = Canvas(self.window, width=self.width, height=self.height, bg='white')
		self.canvas.pack()

		self.canvas.create_text(20, 20, anchor=W, text='Black dot - Neuron says point is over line')
		self.canvas.create_text(20, 40, anchor=W, text='White dot - Neuron says point is under line')

		self.window.protocol("WM_DELETE_WINDOW", self._onWindowDestroy)

	def _onWindowDestroy (self):
		self.windowHasBeenDestroyed = True
		self.window.destroy()

	# Converts X coordinates to the canvas equivalent
	def _xCoordinateToCanvas (self, x):
		return x + self.xBound

	# Converts Y coordinates to the canvas equivalent
	def _yCoordinateToCanvas (self, y):
		return (-y) + self.yBound

	def render (self, onFrame):
		self.window.after(100, onFrame, self, self.perceptron) # Pass renderer and perceptron to onFrame as argument
		self.window.mainloop()

	def renderLine (self, lineFunction):
		x0 = self._xCoordinateToCanvas(-self.xBound)
		y0 = self._yCoordinateToCanvas(lineFunction(-self.xBound))

		x1 = self._xCoordinateToCanvas(self.xBound)
		y1 = self._yCoordinateToCanvas(lineFunction(self.xBound))

		self.canvas.create_line(x0, y0, x1, y1, width=2, fill='grey')

	def renderPerceptron (self):

		# Go through self.points
		# Find the highest point that is still considered by the perceptron to be under the line
		# Find another point considered to be under the line, such that a line that passes over the point
		# found before and this one has the slope closest to 0

		# Begin by deleting the previous line if it exists
		if self.perceptronLine:
			self.canvas.delete(self.perceptronLine)

		# If we don't have 2 points, yet, skip this. We check other skipping cases below
		if len(self.points) < 2:
			return False

		# Find the highest point

		highestPoint = None

		for point in self.points:

			# Skip this iteration if the point is over the imaginary line
			if point[2] == True:
				continue

			if not(highestPoint) or point[1] > highestPoint[1]:
				highestPoint = point

		if not(highestPoint):
			return False

		# Find another point such that the slope between the two is the lowest

		lowestSlope = None
		correspondingPoint = None

		for point in self.points:

			# Check that the point is under the imaginary line
			if point[2] == True:
				continue

			# If this point is the highest point, skip it
			if highestPoint[0] == point[0] and highestPoint[1] == point[1]:
				continue

			# Calculate slope
			currentSlope = abs((point[1] - highestPoint[1]) / (point[0] - highestPoint[0]))

			if not(lowestSlope) or currentSlope < lowestSlope:
				lowestSlope = currentSlope
				correspondingPoint = point

		# If there weren't enough points under the imaginary line, skip
		if not(correspondingPoint):
			return False

		# Now that we have the two points, draw a line through them

		x0 = self._xCoordinateToCanvas(    highestPoint[0]    )
		y0 = self._yCoordinateToCanvas(    highestPoint[1]    )
		x1 = self._xCoordinateToCanvas( correspondingPoint[0] )
		y1 = self._yCoordinateToCanvas( correspondingPoint[1] )

		self.perceptronLine = self.canvas.create_line(x0, y0, x1, y1, width=1, fill='black')

	def drawPoint (self, x, y):

		answer = self.perceptron.feedForward([x, y, 1])

		if answer:
			fill = 'black'
		else:
			fill = 'white'

		cx = self._xCoordinateToCanvas(x) # Canvas x
		cy = self._yCoordinateToCanvas(y) # Canvas y

		point = self.canvas.create_oval((cx - 5), (cy - 5), (cx + 5), (cy + 5), fill=fill)

		self.points.append([x, y, answer, point])

	# Refreshes the fill of all the points and updates their values on the array
	def refresh (self):
		for point in self.points:
			x = point[0]
			y = point[1]
			a = point[2]
			p = point[3]

			if self.perceptron.feedForward([x, y, 1]):
				point[2] = True
				self.canvas.itemconfig(p, fill='black')
			else:
				point[2] = False
				self.canvas.itemconfig(p, fill='white')

def lineFunction (x):
	return 0.5*x + 10

def main ():

	random.seed(time.time())

	width = 800
	height = 600

	xBound = width / 2
	yBound = height / 2

	p = Perceptron(3)

	renderer = Renderer(width, height, xBound, yBound, p)
	renderer.renderLine(lineFunction)

	# Open the GUI
	renderer.render(onFrame)



# Renders each frame
def onFrame (renderer, perceptron):

	# Make training points

	trainingInputs = [] # Format: [[x, y], answer] where answer is -1 or +1

	bias = 1 # Bias input

	xBound = renderer.xBound
	yBound = renderer.yBound

	x = random.uniform(-xBound, xBound)
	y = random.uniform(-yBound, yBound)

	isOverLine = 1 if (y > lineFunction(x)) else -1

	inputs = [x, y, bias]
	answer = isOverLine

	trainingInputs.append([inputs, answer])

	# Train the perceptron with this point
	perceptron.train(inputs, answer)

	# Redraw the perceptron line
	renderer.renderPerceptron()

	# Refresh the previous points
	renderer.refresh()

	# Draw this point
	renderer.drawPoint(x, y)

	# Stop trying to render if window has been closed
	if renderer.windowHasBeenDestroyed:
		return False
	else:
		# Keep iterating
		renderer.window.after(100, onFrame, renderer, perceptron)

# Run the program
main()

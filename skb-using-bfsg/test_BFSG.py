import time
import os
import psutil
from queue import Queue
from copy import copy, deepcopy
from datetime import datetime
import math
from sortedcontainers import SortedList
import numpy as np
from scipy.optimize import linear_sum_assignment
import pandas as pd


	
class Direction:
	def __init__(self, vector, char):
		self.vector = vector
		self.char = char

	def get_char(self):
		return self.char

L = Direction((-1, 0), 'L')
R = Direction((1, 0), 'R')
U = Direction((0, -1), 'U')
D = Direction((0, 1), 'D')
directions = [U, L, D, R]

def set_distance():
	distanceToGoal = dict()
	dead_squares = set()
	for goal in goals:
		distanceToGoal[goal] = dict()
		for path in paths:
			distanceToGoal[goal][path] = 1e9
	queue = Queue()
	for goal in goals:
		distanceToGoal[goal][goal] = 0
		queue.put(goal)
		while not queue.empty():
			position = queue.get()
			for direction in directions:
				boxPosition = (position[0] + direction.vector[0], position[1] + direction.vector[1])
				playerPosition = (position[0] + 2*direction.vector[0], position[1] + 2*direction.vector[1])
				if boxPosition in paths:
					if distanceToGoal[goal][boxPosition] == 1e9:
						if (boxPosition not in walls) and (playerPosition not in walls):
							distanceToGoal[goal][boxPosition] = distanceToGoal[goal][position] + 1
							queue.put(boxPosition)
	# Add dead squares
	for path in paths:
		ok = 1
		for goal in goals:	
			if distanceToGoal[goal][path] != 1e9:
				ok = 0
				break
		if ok == 1:
			dead_squares.add(path)
	return distanceToGoal, dead_squares

def minimum_cost(boxes):
	temp = []
	for goal in goals:
		for box in boxes:
			# Using Manhattan distance
			temp.append(abs(goal[0] - box[0]) + abs(goal[1] - box[1]))

	arr = np.array(temp)
	cost = arr.reshape(len(goals), len(boxes))
	row_ind, col_ind = linear_sum_assignment(cost)
	return cost[row_ind, col_ind].sum()

def set_available_moves(player, boxes):
	available_moves = []
	for direction in directions:
		if (player[0] + direction.vector[0], player[1] + direction.vector[1]) not in walls:
			if (player[0] + direction.vector[0], player[1] + direction.vector[1]) in boxes:
				if ((player[0] + 2*direction.vector[0], player[1] + 2*direction.vector[1]) not in walls) and ((player[0] + 2*direction.vector[0], player[1] + 2*direction.vector[1]) not in boxes):
					available_moves.append(direction)
			else:
				available_moves.append(direction)
	return available_moves

def move(player, boxes, direction):	
	temp = (player[0] + direction.vector[0], player[1] + direction.vector[1])
	res = True
	boxes = set(boxes)
	if temp in boxes:
		boxes.remove(temp)
		boxes.add((player[0] + 2*direction.vector[0], player[1] + 2*direction.vector[1]))
		
		if (player[0] + 2*direction.vector[0], player[1] + 2*direction.vector[1]) in dead_squares:
			res = False
	boxes = tuple(boxes) 
	player = temp
	return res, player, boxes

def is_win(goals, boxes):
	return goals.issubset(boxes)

def set_value(filename):
	walls = set() # set of Point()
	goals = set()
	boxes = []
	paths = set()
	player = None
	x = 0
	y = 0
	with open(filename, 'r') as f:
		read_data = f.read()
		lines = read_data.split('\n')	
		for line in lines:
			x = 0
			for char in line:
				if char == '#': # Wall
					walls.add((x,y))
				elif char == 'x': # Box
					boxes.append((x,y))
					paths.add((x,y))
				elif char == '?': # Goal
					goals.add((x,y))
					paths.add((x,y))
				elif char == '@': # Player
					player = (x,y)
					paths.add((x,y))
				elif char == '-': # Player and Goal
					goals.add((x,y))
					player = (x,y)
					paths.add((x,y))
				elif char == '+': # Box and Goal
					goals.add((x,y))
					boxes.append((x,y))
					paths.add((x,y))
				elif char == '.': # Path - avaiable move
					paths.add((x,y))
				x += 1
			y += 1
	return walls, goals, tuple(boxes), paths, player


itemMemory = psutil.Process(os.getpid()).memory_info().rss/(1024*1024)


def bfsg(curr_player, curr_boxes):
	node_generated = 0
	frontier = SortedList(key=lambda x: minimum_cost( x[1]))
	explored = set()
	frontier.add((curr_player, curr_boxes, 0, []))

	node_generated += 1
	explored.add((curr_player, curr_boxes))
	startTime = time.time()
	while True:
		(now_player, now_boxes, step, actions) = frontier.pop(0)
		moves = set_available_moves(now_player,now_boxes)
		for m in moves:
			res, new_player, new_boxes = move(now_player, now_boxes, m)
			if (new_player, new_boxes) not in explored and res == True:
				explored.add((new_player, new_boxes))
				if is_win(goals, new_boxes):
					end = time.time() - startTime
					memo_info = psutil.Process(os.getpid()).memory_info().rss/(1024*1024) - itemMemory
					return (node_generated + 1,step + 1, end, memo_info)
				frontier.add((new_player, new_boxes, step+1, actions + [m]))
			node_generated += 1
	

if __name__ == '__main__':
	i = -1
	if not os.path.exists("BFSG.csv"):
		f = open("BFSG.csv", 'w+')
		f.write("Level,Algorithm,Node generated,Step,Time (s),Memory (MB)\n")
		f.close()
		i = 0
	else:
		# load file
		f = open("BFSG.csv", "r")
		contents = f.read()
		i = len(contents.split('\n')) - 2
		f.close()
	
	print("Loading BFS algorithm results from testcase {}".format(i+1))
	sum_times = 0
	sum_memo = 0

	for j in range(i, 40):
		walls, goals, boxes, paths, player = set_value("./Testcases/{}.txt".format(j%40+1))
		distanceToGoal, dead_squares = set_distance()
		print("\nSolving testcase {}: ".format(j+1))
		(node_created, step, times, memo) = bfsg(player, boxes)
		sum_times+=times
		sum_memo+=memo


		f = open("BFSG.csv", 'a+')
		f.write("{},BFSG,{},{},{:0.6f},{:0.6f}\n".format(j%40+1, node_created, step, times, memo))
		print("Results testcase {}. Node generated: {}, Step: {}, Time: {:0.6f} s, Memory: {:0.6f} MB\n".format(j+1, node_created, step, times, memo))
		f.close()

	print("\nSolving BFS algorithm results Completed")
	print(sum_times/40,sum_memo/40)
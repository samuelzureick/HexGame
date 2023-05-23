import hashlib
import socket
from random import choice
from time import sleep
import numpy as np

import random

import os
import json

import copy

class NaiveAgent():
	"""This class describes the default Hex agent. It will randomly send a
	valid move at each turn, and it will choose to swap with a 50% chance.
	"""

	HOST = "127.0.0.1"
	PORT = 1234

	def __init__(self, board_size=11):
		self.s = socket.socket(
			socket.AF_INET, socket.SOCK_STREAM
		)

		self.s.connect((self.HOST, self.PORT))

		self.board_size = board_size
		self.board = []
		self.colour = ""
		self.turn_count = 0
		self.v = {}
		self.history = []

		#eligibilty trace
		self.elig = {}

		#hyperparameters
		self.LAMBDA = 0.9
		self.ALPHA = 0.1
		self.GAMMA = 0.9
		self.EPSILON = 0.1
		if os.path.isfile("agents/Group52/board_eval.json"):
			with open("agents/Group52/board_eval.json", "r") as f:
				self.v = json.load(f)


	def run(self):
		"""Reads data until it receives an END message or the socket closes."""

		while True:
			data = self.s.recv(1024)
			if not data:
				break
			# print(f"{self.colour} {data.decode('utf-8')}", end="")
			if (self.interpret_data(data)):
				break

		# print(f"Naive agent {self.colour} terminated")

	def interpret_data(self, data):
		"""Checks the type of message and responds accordingly. Returns True
		if the game ended, False otherwise.
		"""

		messages = data.decode("utf-8").strip().split("\n")
		messages = [x.split(";") for x in messages]
		# print(messages)
		for s in messages:
			if s[0] == "START":
				self.board_size = int(s[1])
				self.colour = s[2]
				print("I am ", self.colour)
				self.board = [
					[0]*self.board_size for i in range(self.board_size)]

				if self.colour == "R":
					self.make_move()

			elif s[0] == "END":
				if(s[1] == self.colour):
					self.update_end(1)
				else:
					self.update_end(-1)
				return True

			elif s[0] == "CHANGE":
				if s[3] == "END":
					# return True
					pass

				elif s[1] == "SWAP":
					self.colour = self.opp_colour()
					print("SWAP. I am ", self.colour)
					if s[3] == self.colour:
						self.make_move()

				elif s[3] == self.colour:
					action = [int(x) for x in s[1].split(",")]
					self.board[action[0]][action[1]] = self.opp_colour()
					self.history.append(copy.deepcopy(self.board))
					self.add_eligibility(copy.deepcopy(self.board))
					self.make_move()

		return False

	def make_move(self):
		"""Makes a random move from the available pool of choices. If it can
		swap, chooses to do so 50% of the time.
		"""

		# print(f"{self.colour} making move")
		if self.colour == "B" and self.turn_count == 0:
			if choice([0, 1]) == 1:
				self.s.sendall(bytes("SWAP\n", "utf-8"))
			else:
				# same as below
				choices = []
				for i in range(self.board_size):
					for j in range(self.board_size):
						if self.board[i][j] == 0:
							choices.append((i, j))
				pos = self.choose_move(choices)
				self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
				self.board[pos[0]][pos[1]] = self.colour
				self.add_eligibility(copy.deepcopy(self.board))
				self.history.append(copy.deepcopy(self.board))

		else:
			choices = []
			for i in range(self.board_size):
				for j in range(self.board_size):
					if self.board[i][j] == 0:
						choices.append((i, j))
			pos = self.choose_move(choices)
			self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
			self.board[pos[0]][pos[1]] = self.colour
			self.add_eligibility(copy.deepcopy(self.board))
			self.history.append(copy.deepcopy(self.board))


		self.turn_count += 1

	def opp_colour(self):
		"""Returns the char representation of the colour opposite to the
		current one.
		"""
		if self.colour == "R":
			return "B"
		elif self.colour == "B":
			return "R"
		else:
			return "None"

	
	def flip_board(self, board_move):
		for i in range(self.board_size):
			for j in range(self.board_size):
				if(board_move[i][j] == "B"):
					board_move[i][j] = "R"
				elif(board_move[i][j] == "R"):
					board_move[i][j] = "B"
		return board_move
	
	def rotate_board(self,board_move):
		board_copy = copy.deepcopy(board_move)
		for i in range(self.board_size):
			for j in range(self.board_size):
				board_move[i][j] = board_copy[j][self.board_size - i - 1]
		return board_move

	def choose_move(self, choices):
		# epsilon-greedy. It returns a random choice with probability epsilon.
		p = random.random()
		if(p < self.EPSILON):
			return random.choice(choices)

		best_move_r = 0
		best_move = 0
		for choice in choices:
			r = choice[0]
			c = choice[1]
			board_copy = copy.deepcopy(self.board)
			# board_copy = self.convert_board_to_list_of_strings(board_copy)
			# board_copy[r] = board_copy[r][:c] + self.colour + board_copy[r][c+1:]
			board_copy[r][c] = self.colour
			if(self.colour == "R"):
				board_copy = self.flip_board(board_copy)
				
				board_copy = self.rotate_board(board_copy)

			rew = self.get_reward(board_copy)
			if(rew >= best_move_r):
				best_move_r = rew
				best_move = choice
	

		print(best_move)
		return best_move

	def get_reward(self, board):
		board_string = self.convert_board_to_string(board)
		
		return self.v.get(board_string, 0)




	def convert_list_of_strings_to_board(self, list_of_strings):
		new = []
		for line in list_of_strings:
			new.append(line.split(""))
		return new


	def convert_board_to_list_of_strings(self, board):
		new = []
		for row in board:
			new_row = ""
			for el in row:
				new_row += str(el)
			new.append(new_row)
		return new

	def convert_board_to_string(self, board):
		new = self.convert_board_to_list_of_strings(board)
		return "".join(new)

	def get_eligibility(self, board_state):
		"""
		Function to return eligibilty of certain board_state
		If board state is never visited, return 0
		"""
		board_string = self.convert_board_to_string(board_state)
		return self.elig.get(board_string, 0)

	def add_eligibility(self, board_state):
		"""
		Function to increase eligibilty of certain board state
		"""
		board_string = self.convert_board_to_string(board_state)
		#state visited
		if(board_string in self.elig):
			self.elig[board_string] += 1
		#first time visiting state
		else:
			self.elig[board_string] = 1

	def update_eligibility(self):
		"""
		Function to update eligibility every turn
		"""
		self.elig = {key: self.decay(value) for key, value in self.elig.items()}

	def decay(self, value):
		"""
		Fucntion to apply eligibility decay
		"""
		return value * self.LAMBDA * self.GAMMA

	def update_end(self, r):
		list_states = copy.deepcopy(self.history)
		list_states.reverse()
		#update board value
		for count in range(len(list_states) - 2):
			#initialise states
			curr_state = list_states[count]
			next_state = list_states[count + 1]

			# get td_error and update every state value estimate
			td_error = r + self.GAMMA * self.get_reward(next_state) - self.get_reward(curr_state)
			update_value = self.ALPHA * td_error * self.get_eligibility(curr_state)

			# update eligibility trace
			self.update_eligibility()
			self.set_reward(curr_state, self.get_reward(curr_state) + update_value)

		# assign reward to terminal board state based on outcome of the match
		# self.set_reward(list_states[-1], r)

		self.store_v()
		print("I am ", self.colour)


	def set_reward(self, board_state, value):
		board_string = self.convert_board_to_string(board_state)
		if(self.colour == "R"):
			self.v[board_string] = -value
		else:
			self.v[board_string] = value

	def store_v(self):
		with open("agents/Group52/board_eval.json", "w") as f:
			f.write(json.dumps(self.v))


if (__name__ == "__main__"):
	agent = NaiveAgent()
	agent.run()

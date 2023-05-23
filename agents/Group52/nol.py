import hashlib
import socket
from random import choice
from time import sleep

import random

import os

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
		self.LAMBDA = .75
		self.ALPHA = 0.2



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
				self.board = [
					[0]*self.board_size for i in range(self.board_size)]

				if self.colour == "R":
					self.make_move()

			elif s[0] == "END":
				if(s[1] == self.colour):
					self.update_end(1)
				else:
					self.update_end(0)
				return True

			elif s[0] == "CHANGE":
				if s[3] == "END":
					# return True
					pass

				elif s[1] == "SWAP":
					self.colour = self.opp_colour()
					if s[3] == self.colour:
						self.make_move()

				elif s[3] == self.colour:
					action = [int(x) for x in s[1].split(",")]
					self.board[action[0]][action[1]] = self.opp_colour()
					#self.history.append(copy.deepcopy(self.board))
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

	def choose_move(self, choices):
		moves_outcome = []
		for choice in choices:
			r = choice[0]
			c = choice[1]
			board_copy = copy.deepcopy(self.board)
			# board_copy = self.convert_board_to_list_of_strings(board_copy)
			# board_copy[r] = board_copy[r][:c] + self.colour + board_copy[r][c+1:]
			board_copy[r][c] = self.colour
			
			moves_outcome.append([choice, self.get_reward(board_copy)])
		moves_outcome.sort(key = lambda v :v[1], reverse = True)
		count = 0
		while(count < len(moves_outcome)-1 and moves_outcome[count+1][1] == moves_outcome[0][1]):
			count += 1

		i = random.randint(0, count)

		return moves_outcome[i][0]

	def get_reward(self, board):
		board_string = self.convert_board_to_string(board)
		return self.v.get(board_string, 0.5)

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

	def update_end(self, r):
		list_states = copy.deepcopy(self.history)
		list_states.reverse()
		for count, state in enumerate(list_states):
			td_error = r - self.get_reward(state)
			update_value = self.ALPHA * (td_error + (self.LAMBDA ** (len(list_states)-count)) )
			self.set_reward(state, self.get_reward(state) + update_value)
		self.store_v()

	def set_reward(self, board_state, value):
		board_string = self.convert_board_to_string(board_state)
		self.v[board_string] = value
	
	def store_v(self):
		pass

		


		



if (__name__ == "__main__"):
	agent = NaiveAgent()
	agent.run()

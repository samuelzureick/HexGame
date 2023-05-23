import os
import hashlib
import pickle
import random
import numpy as np

class td0():
	def __init__(self, colour, default_payoff = .5, epsilon = .1, alpha = .2, mode = "play", lam = .75):
		"""
		-td(0) class
		-parameters:
			+ colour: represents players colour on the board
			+ default_payoff: default payoff for outcomes not in eval function
			+ epsilon: probability of random exploration
			+ alpha: learning rate for TD update
			+ mode: training or play mode, training mode tracks previous moves
			+ lam: lambda hyperparam effecting how much move history is
				affected by outcome
		"""
		self.DEFAULT_PAYOFF = default_payoff
		self.EPSILON = epsilon
		self.colour = colour
		if self.colour == "R":
			self.enemy = "B"
		else:
			self.enemy = "R"
		self.v = {}
		self.ALPHA = alpha
		self.history = None
		self.LAM = lam
		self.e = {}
		self.DFACTOR = .8

		if mode == "training":
			self.history = []

		#if not os.path.exists("board_eval.pkl"):
		#	open("board_eval.pkl","wb").close()
		#else:
		#	with open("board_eval.pkl", "rb") as f:
		#		self.v = pickle.load(f)


	def get_reward(self, b):
		b_hash = self.b_encode(b)
		if self.v.get(b_hash) == None:
			self.v[b_hash] = self.DEFAULT_PAYOFF
		return self.v[b_hash]

	def b_encode(self,b):
		return hashlib.sha256(bytes("".join(b), "utf-8")).hexdigest()

	def set_reward(self, b, v):
		b_hash = self.b_encode(b)
		if self.v.get(b_hash) == None:
			self.v[b_hash] = 0
		self.v[b_hash] = v

	def get_e(self, b):
		b_hash  = self.b_encode(b)
		if self.e.get(b_hash) == None:
			self.e[b_hash] = 0
		return self.e[b_hash]

	def set_e(self,b,e):
		b_hash = self.b_encode(b)
		self.e[b_hash] = e

	def test_move(self,b, m):
		r = m[0]
		c = m[1]
		tb = b.copy()
		tb[r] = tb[r][:c] + self.colour + tb[r][c+1:]
		return tb

	def update_end(self, r):
		moves = moves.reverse()
		for c, m in enumerate(moves):
			td_error = self.get_reward(m) - r
			update_value = self.alpha * (td_error + (self.lam ** len(moves)-1-c) * self.lam)

			self.set_reward(m, self.get_reward(m) + update_value)

	def make_move(self, b):
		next_move = self.predict(b)
		new_board = self.test_move(b, next_move)
		return next_move, new_board


	def store_v(self):
		#with open("board_eval.pkl", "wb") as f:
		#	pickle.dump(self.v, f, pickle.HIGHEST_PROTOCOL)
		return None



	def heuristic(self, b):
		# simple heuristic to favor moves that are in a straight path to the other side of the board, needs improvement to be more complete

		good_moves = []
		for rc, r in enumerate(b):
			if self.enemy not in r:
				good_moves += [(rc, i) for i in range(len(r)) if b[rc][i] == "0"]

		return good_moves



	def get_possible_moves(self,b):
		"""
		Function to get all available moves given current board state b
		returns list of tuples representing valid moves
		"""
		moves = []

		for i in range(len(b)):
			for j in range(len(b[i])):
				if b[i][j] == "0":
					moves.append((i,j))

		return moves

	def predict(self,b):
		"""
		-function to predict the best move given board state b

		-first gets all possible moves given the board state
		-goes through each possible move and sees potential payoff
		-sorts possible moves to find best payoff
		-chooses this move with probability 1-self.EPSILON, otherwise
			choose random move from possible moves
		-uses VC heuristic to favor moves that
			connect two sides of board
		-board evaluation function stored as hashmap, key = hex digest of sha256(board)
		"""
		moves = self.get_possible_moves(b)

		# to hold moves and possible payoffs
		moves_outcome = []

		for move in moves:
			tb = b.copy()

			r = move[0]
			c = move[1]

			tb[r] = tb[r][:c] + self.colour + tb[r][c+1:]

			# hash board state using sha256
			hash_b = hashlib.sha256(bytes("".join(tb), "utf-8")).hexdigest()

			moves_outcome.append([move, self.get_reward(tb)])


		# sort moves by decreasing value
		# in event of a tie, use randomness to decide on a representative
		moves_outcome.sort(key = lambda v :v[1], reverse = True)
		count = 0
		while(count < len(moves_outcome)-1 and moves_outcome[count+1][1] == moves_outcome[0][1]):
			count += 1

		i = random.randint(0, count)

		return moves_outcome[i][0]


	def epsilon_greedy_policy(self, b, epsilon, t ):
		"""
		-function to decide whether to exploit the best move or explore a random move based on epsilon greedy

		-board_state: current board state
		-epsilon: epsilon value
		-t: Time step. Start from 1. Used to decrease epsilon over time to favour exploitation
		"""
		#reduce epsilon value over Time
		epsilon = epsilon / t

		# initialise the believed best action
		best_move = self.predict(b)

		# initialise a random action that is not the same as the best best action
		rand_move = random.choice(self.get_possible_moves(b))

		# insert both best and random move into a list
		moves = [best_move] + [rand_move]

		# choose between best and random move based on epsilon value
		chosen_move = random.choices([moves], weights=(1-epsilon, epsilon))
		return chosen_move
		

	def epsilon_greedy_policy(self, b, epsilon, t ):
		"""
		-function to decide whether to exploit the best move or explore a random move based on epsilon greedy

		-board_state: current board state
		-epsilon: epsilon value
		-t: Time step. Start from 1. Used to decrease epsilon over time to favour exploitation
		"""
		#reduce epsilon value over Time
		epsilon = epsilon / t

		# initialise the believed best action
		best_move = self.get_best_move(b)

		# initialise a random action that is not the same as the best best action
		rand_move = random.choice(self.get_possible_moves(b))

		# insert both best and random move into a list
		moves = [best_move] + [rand_move]

		# choose between best and random move based on epsilon value
		chosen_move = random.choices([moves], weights=(1-epsilon, epsilon))
		return chosen_move


# testing !

def win_judge(c,b):
	w = "".join([c for i in range(len(b[1]))])
	return 0 < len([None for r in b if r == w])

def display_board(b, m):
	print("****MOVE****")
	print("moved to position " +str(m[0]) + ", " +str(m[1]))
	for r in b:
		print(r)
	print()

red = td0("R", mode ="training")
blue = td0("B", mode = "training")

b = ["00000000000" for i in range(11)]

mr, b = red.make_move(b)
for i in range(60):
	mb, b = blue.make_move(b)
	if win_judge("B",b):
		print("game wone!")
		print("previous v:")
		print(self.v)
		self.update_end(1)
		print("new v:")
		print(self.v)
		break
	mr, b = red.make_move(b)

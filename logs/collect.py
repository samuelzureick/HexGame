import csv
import os

wins = 0
losses = 0
red = 0
blue = 0
win_red = 0
win_blue = 0

for file in os.listdir():
	is_red = False
	if file != "collect.py":
		with open(file, "r") as f:
			csvreader = csv.reader(f)
			for index, row in enumerate(csvreader):
				#check if agent is starting
				if(index == 3 and "52" in row):
					is_red = True

				#check if swap occur
				if(index == 4 and "SWAP" in row):
					is_red = False

				# reached the ended
				if("End" in row):
					# tally wins and losses
					if("52" in row):
						wins += 1
						if(is_red):
							red += 1
							win_red += 1
						else:
							blue += 1
							win_blue += 1
						break
					else:
						losses += 1
						if(is_red):
							red += 1
						else:
							blue += 1
						break







print("Wins: " +str(wins))
print("Losses: " +str(losses))
print("Games as red: " + str(red))
print("Games as blue: " + str(blue))
print("Average win rate: " +str(int((wins/(losses+wins))*100)) +"%")
print("Win rate as red: " + str(int((win_red/red)*100)) +"%")
print("Win rate as blue: " + str(int((win_blue/blue)*100)) +"%")

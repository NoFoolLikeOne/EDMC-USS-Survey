import glob
import json
import ast


event={}


with open('journal.txt', encoding="utf-8") as journal:
	for line in journal:
		if '"event":' in line:
			print(line.strip())
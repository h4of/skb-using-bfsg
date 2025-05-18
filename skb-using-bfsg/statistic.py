import numpy as np
from matplotlib import pyplot as plt
# import matplotlib.pyplot as plt
import pandas as pd


BFSG = pd.read_csv("BFSG.csv",na_values=["???", "??? "])

def drawChart(factor):
	stepBFSG = BFSG[factor][1:len(BFSG)]

	barWidth = 0.25
	fig = plt.subplots(figsize =(12, 8))

	index = []
	for i in range(0,len(stepBFSG)):
			index.append(i+1)

	# set height of bar
	#IT = [12, 30, 1, 8, 22]
	#ECE = [28, 6, 16, 5, 10]
	#CSE = [29, 3, 24, 25, 17]
	
	# Set position of bar on X axis
	br1 = np.arange(len(stepBFSG))

	# Make the plot
	plt.bar(br1, stepBFSG, color ='r', width = barWidth,
			edgecolor ='grey', label ='BFSG')

	if (factor == "Step"):
		ylab = "Step"
	elif (factor == "Time (s)"):
		ylab = "sec"
	elif (factor == "Node generated"):
		ylab = "Node"
	else:
		ylab = "MB"

	plt.xlabel('Level', fontweight ='bold', fontsize = 15)
	plt.ylabel(ylab, fontweight ='bold', fontsize = 15)

	plt.xticks([barWidth/2 + r for r in range(len(stepBFSG))],index)
	if (factor == "Memory (MB)"):
		plt.title("The amount of memory used in " +  " Testcases")
	elif (factor == "Time (s)"):
		plt.title("The amount of time elapsed in " + " Testcases")
	elif (factor == "Node generated"):
		plt.title("The amount of node generated in " + " Testcases")
	else:
		plt.title("The number of " + factor + " taken in " + " Testcases")
	plt.legend()
	
	if (factor == "Memory (MB)"):
		save = "memory"
	elif (factor == "Step"):
		save = "step"
	elif (factor == "Node generated"):
		save = "nodeGenerated"
	else:
		save = "time"
	plt.savefig("./Charts/" + save + ".png")


drawChart("Step")
drawChart("Time (s)")
drawChart("Memory (MB)")
drawChart("Node generated")

print(len(BFSG))

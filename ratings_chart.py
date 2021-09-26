from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

import numpy as np
import random

class RatingChart:
	def __init__(self, a, b):
		ax = plt.figure(figsize=(a, b)).gca()
		ax.xaxis.set_major_locator(MaxNLocator(integer=True))
		ax.yaxis.set_label_coords(0.359, 2.2)

	def get_min_max(self, data:list) -> list:
		result = [9999, 0]
		for i in data:
			if i < result[0]:
				result[0] = i
			if i > result[1]:
				result[1] = i
		return result

	async def _draw_chart(self, user:str, data:list):
		minmax = self.get_min_max(data)
		plt.plot(np.array([x for x in range(1, len(data) + 1)]), np.array(data), 'k-o')
		plt.xlabel("Matches", horizontalalignment="right")
		lby = plt.ylabel("Rating (Highest: %.2f, Lowest: %.2f)" % (minmax[1], minmax[0]), horizontalalignment="right", y=1.03)
		lby.set_rotation(0)
		plt.savefig(f'./temp/{user[3:-1]}.png')
import string
import numpy as np
import math

class chi_square_test:
	def __init__(self):
		table_file = r'chi_square_dist_table.txt'

		row_num = 265
		column_num = 11
		self.alpha_columns = [0.995, 0.975, 0.20, 0.10, 0.05, 0.025, 0.02, 0.01, 0.005, 0.002, 0.001]
		self.chisquare_table = dict()

		table_f = open(table_file,'r')
		line_num = 0
		for line in table_f:
			if line == '\n':
				continue
			values = line[:-1].split('\t')
			df = int(values[0])
			self.chisquare_table[df] = list()
			for i in range(1, 12):
				self.chisquare_table[df].append(float(values[i]))
			line_num += 1
		table_f.close()
	

	# sample_A: observed value
	# sample_B: expected value
	def compute_chi_square(self, sample_A, sample_B):
		length = len(sample_A)
		df = length - 1
		if df < 1:
			return None
		
		chi_square = 0
		for i in range(0, len_A):
			if sample_B[i] == 0:
				continue
			chi_square += math.pow((sample_A[i]-sample_B[i]), 2) / 1.0 / sample_B[i]
			
		return chi_square

	# sample_A: observed value
	# sample_B: expected value
	def compute_array_chi_square(self, sample_A, sample_B):
		row_num = len(sample_A)
		column_num = len(sample_A[0])
		df = (row_num - 1) * (column_num - 1)
		if df < 1:
			return None
		
		chi_square = 0
		for i in range(0, row_num):
			for j in range(0, column_num):
				if sample_B[i,j] == 0:
					continue
				chi_square += math.pow((sample_A[i,j]-sample_B[i,j]), 2) / 1.0 / sample_B[i,j]
			
		return chi_square

	def reject_null(self, chi_square, df, alpha):
		if chi_square == None:
			return None
	#	print 'chi_square:', chi_square
		index = df
		if index not in self.chisquare_table:
			max_value = max(self.chisquare_table.keys())
			if index > max_value:
				index = max_value
			else:
				for value in sorted(self.chisquare_table.keys()):
					if index < value:
						index = value
						break

		if chi_square < self.chisquare_table[index][0]:
			return False
		if chi_square >= self.chisquare_table[index][10]:
			return True
		for i in range(1,11):
			if self.chisquare_table[index][i-1] <= chi_square and chi_square < self.chisquare_table[index][i]:
				if self.alpha_columns[i-1] <= alpha:
					return True
				else:
					return False



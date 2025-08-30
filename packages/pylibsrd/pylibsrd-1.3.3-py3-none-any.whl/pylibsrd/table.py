import re
import tabulate
 

class Table:
	"""
	Table
	=====
	- A table class for reading data from a tab seperated variable (tsv) file.
	- Comments are supported, by default they are indicated with ! at the start of a line, but that can be changed.
	"""
	def __init__(self):
		self.headers = []
		self.data = []
	
	def __str__(self):
		"""Gets the table ready for displaying"""
		return tabulate.tabulate(self.data, self.headers, tablefmt="mixed_outline")

	def get_index(self, colname):
		"""Finds the index of a certain column in a table from its name. Will return None if column isn't found."""
		colindex = None
	   
		for header in self.headers:
			if header.lower() == colname.lower():
				colindex = self.headers.index(header)
 
		return colindex
 
	def get_column(self, colname):
		"""Will return a 1D list representing all the data within a certain column, from its name. Will return None if column not found."""
		colindex = self.get_index(colname)
 
		# return nothing if column not found.
		if colindex == None:
			return None
 
		data = []
 
		# Add data from each row that is in the requested col to a list.
		for row in self.data:
			data.append(row[colindex].strip())
 
		return data
   
	def get_col(self, colindex):
		"""Will return a 1D list representing all the data within a certain column, from its index. Will return None if column not found."""
 
		# return nothing if column not found.
		if colindex > len(self.headers):
			return None
 
		data = []
 
		# Add data from each row that is in the requested col to a list.
		for row in self.data:
			data.append(row[colindex].strip())
 
		return data
 
	def write_tsv(self, path):
		"""
		Writes the table to file: ```path```  
		WARNING: Comments are lost.
		"""
		
		lines = [f"{'\t'.join(self.headers)}\n"]

		for row in self.data:
			lines.append(f"{'\t'.join(row)}\n")

		with open(path, "w+") as f:
			f.writelines(lines)

	@staticmethod
	def read_tsv(Lines: str, commentChar="!"):
		"""Parse and load a TSV table into a table object from a string.
		Comments will be removed and TSV loaded."""
		table = Table()
		NumHeaders = 0

		# Remove Comments
		Lines = re.sub(f"{commentChar}.*?\n", "", Lines)
	
		# Convert to array of strings
		lines = Lines.split("\n")
	
		# Remove all lines without tabs present
		for i in range(len(lines)-1, -1, -1):
			if "\t" not in lines[i]:
				lines.remove(lines[i])

		# Go through each line
		for i in range(len(lines)):
			lines[i] = lines[i].replace("\n", "")  # Remove newline chars
			temp = lines[i].split("\t")  # Split by tabs
	
			if i == 0:  # If header line
				NumHeaders = len(temp)
				table.headers = temp
			else:
				# Append blank cols, until column count the same as header
				while len(temp) < NumHeaders:
					temp.append("")
				table.data.append(temp)
	
		return table
	
	@staticmethod
	def open_tsv(path:str, commentChar="!"):
		"""Read, parse and load a TSV table into a table object from a file path.
		Comments will be removed and TSV loaded."""

		table = None

		# Read lines from filepath
		with open(path) as f:
			lines = f.read()
			table = Table.read_tsv(lines, commentChar)

		return table

"""\nmake everything one line\n"""
import argparse
from collections import deque
bracket_pairs = { "{": "}", "[": "]", "(": ")" }
quotes = "\"\'"
triple_quotes = [q * 3 for q in quotes]
def detect_unmatched(inp: str) -> tuple[bool, [int], int, [int]]:
	"""\n\tdetect an unmatched bracket or string on a line\n\tas well as where a single line comment starts\n\tand if there's a line continuation\n\t:param inp:\n\t:return: if there is anything unmatched, index for line continuation, comment line start\n\t"""
	str_char = None
	triple_quote = None
	stack = deque()
	prune = None
	i = 0
	while i < len(inp):
		c = inp[i]
		c3 = inp[i:i + 3]
		if triple_quote is None:
			'# triple quote detection'
			if c3 in triple_quotes:
				triple_quote = c3
				i += 3
				continue
		else:
			if c == "\\":
				i += 1
			if c3 == triple_quote:
				triple_quote = None
				i += 3
				continue
			i += 1
			continue
		if str_char is None:
			'# not in a string check'
			if c == "\\":
				'# weird line continuation thing'
				prune = i
			elif c == "#":
				'# comment checking'
				break
			elif c == ";":
				'# statement separator'
				if stack:
					raise SyntaxError("File is formatted incorrectly.  Semicolon before closing brackets.")
				return False, 0, 0, i
			elif prune is not None and c not in whitespace:
				raise SyntaxError("File is formatted incorrectly.  Statement after line continuation.")
			elif c in bracket_pairs:
				'# ascend bracket'
				stack.append(bracket_pairs[c])
			elif stack and c == stack[-1]:
				'# descend bracket'
				del stack[-1]
			elif c in quotes:
				str_char = c
		elif c == "\\":
			i += 1
		elif c == str_char:
			str_char = None
		i += 1
	if str_char is not None:
		raise SyntaxError("File is formatted incorrectly.  Single quote string over multiple lines.")
	return bool(stack) or triple_quote is not None or prune is not None, prune, i, None
whitespace = " \n\t\f\r\v"
def reduce_whitespace(line: str) -> str:
	"""\n\tremoves unimportant whitespace (eg repeat whitespaces outside of strings).\n\tAlso converts preceding whitespace to tabs\n\t:param line: string line to modify\n\t:return:\n\t"""
	i = 0
	while i < len(line):
		'# check preceding whitespace'
		c = line[i]
		if c not in whitespace:
			break
		i += 1
	if i >= len(line):
		raise SyntaxWarning("This line is only whitespace, delete it")
	res = ["\t" * i]
	in_quote: [str] = None
	while i < len(line):
		'# check interior whitespace'
		c = line[i]
		if in_quote is None:
			if c in whitespace:
				if res[-1] != " ":
					res.append(" ")
			elif c in quotes:
				if len(line) >= i + 3 and line[i:i + 3] == c * 3:
					in_quote = c * 3
				else:
					in_quote = c
				i += len(in_quote)
				res.append(in_quote)
				continue
			else:
				res.append(c)
		else:
			if c in whitespace:
				res.append(ascii(c)[1:-1])
			elif c == "\\":
				i += 1
				res.append(c)
				if line[i] in whitespace:
					res.append(ascii(line[i])[1:-1])
				else:
					res.append(line[i])
			elif len(line) >= i + len(in_quote) and line[i:i + len(in_quote)] == in_quote:
				i += len(in_quote)
				res.append(in_quote)
				in_quote = None
				continue
			else:
				res.append(c)
		i += 1
	if in_quote:
		raise RuntimeError("unfinished quote in reduce whitespace step")
	while res[-1] == " ":
		del res[-1]
	return "".join(res)
def indentation(line: str):
	i = 0
	while i < len(line):
		if line[i] != "\t":
			return i
		i += 1
	raise RuntimeError("at this point only-whitespace lines should have been removed")
def pre_process(lines: list[str]):
	"""\n\tcollapse statements that are separated across multiple lines, such as\n\n\t[\n\t\tlist constructions\n\t]\n\n\t(\n\t\ttuple constructions, item 2\n\t)\n\n\tor strings like this\n\talso change single line comments to strings alone on a line\n\t"""
	comments_queue = []
	i = 0
	while i < len(lines):
		if not lines[i] or (len(lines[i]) == 1 and lines[i] in whitespace):
			'# remove empty lines'
			print("empty line")
			del lines[i]
			continue
		print("processing " + ascii(lines[i]))
		collapse, prune, comment_start, line_sep = detect_unmatched(lines[i])
		if line_sep is not None:
			print("separating line separator on " + ascii(lines[i]))
			first_non_whitespace = line_sep + 1
			while first_non_whitespace < len(lines[i]) and lines[i][first_non_whitespace] in whitespace:
				first_non_whitespace += 1
			lines.insert(i + 1, lines[i][first_non_whitespace:])
			lines[i] = lines[i][:line_sep]
			lines[i] = reduce_whitespace(lines[i])
			lines[i + 1] = "\t" * indentation(lines[i]) + lines[i + 1]
			i += 1
			continue
		if comment_start < len(lines[i]):
			'# separate single line comments comments'
			print("separating comments on " + ascii(lines[i]))
			comments_queue.append(lines[i][comment_start:-1])
			lines[i] = lines[i][:comment_start]
		if prune is not None:
			'# prune line continuation characters'
			print("pruning line continuation on " + ascii(lines[i]))
			lines[i] = lines[i][:prune]
		if collapse:
			'# if open brackets/triple quote'
			if i + 1 >= len(lines):
				raise SyntaxError("File is formatted incorrectly.  Unmatched brackets.")
			print("unmatched bracket on" + ascii(lines[i]) + ".  Combining with " + ascii(lines[i + 1]))
			lines[i] = lines[i] + lines[i + 1]
			del lines[i + 1]
			continue
		try:
			print("pre_reduced: " + ascii(lines[i]))
			lines[i] = reduce_whitespace(lines[i])
			print("post_reduced: " + ascii(lines[i]))
			indents = "\t" * (indentation(lines[i]) + (lines[i][-1] == ":"))
			while comments_queue:
				i += 1
				print("inserting comment " + ascii(comments_queue[0]))
				lines.insert(i, indents + ascii(comments_queue[0]))
				del comments_queue[0]
			i += 1
		except SyntaxWarning:
			print("only whitespace, deleting")
			del lines[i]
def run(process: str, output: str = ""):
	with open(process, "r") as file:
		lines = file.readlines()
	pre_process(lines)
	with open(output, "w") as file:
		for line in lines:
			file.write(line + "\n")
def parse_command_line() -> tuple[str, str]:
	global print
	parser = argparse.ArgumentParser( prog='One Line Engine', description='Python programs tend to be so long and tedious, so condense it all into one line!', epilog='Make a nice one-liner.')
	parser.add_argument('filename')
	parser.add_argument('-o', '--output', default="")
	parser.add_argument('-v', '--verbose', action="store_true")
	args = parser.parse_args()
	if args.verbose:
		import builtins
		print = builtins.print
	else:
		print = lambda *args, **kwargs: None
	return args.filename, args.output
if __name__ == "__main__":
	run(*parse_command_line())

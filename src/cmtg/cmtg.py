#!/usr/bin/env python3
from importlib.resources import read_text
from itertools import permutations
from pprint import pprint
import argparse
from pathlib import Path
import sys
import re

if __package__:
	from . import resources
else:
	import resources

xres_path = Path.home() / Path('.Xresources')
color_regex = re.compile("#[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]")

def get_combos(targets, sources):
	assert len(targets) <= len(sources)
	return [list(zip(targets, x)) for x in permutations(sources,len(targets))]

# Return text for a given input argument
def input_arg(arg):
	if arg == '-':
		return sys.stdin.read()

	path = Path(arg)
	if path.exists():
		return path.read_text(encoding='utf-8')

	# TODO: CPP or appres?
	if arg == 'xres' and xres_path.exists():
		return xres_path.read_text(encoding='utf-8')

	return read_text(resources, arg)

# Write text to output argument
def output_arg(arg, text):
	if arg == '-':
		sys.stdout.write(text)
	else:
		path = Path(arg)
		path.write_text(text, encoding='utf-8')

def parse_colors(t):
	colors = set()
	for line in t.splitlines():
		if (m := re.search(color_regex, line)):
			c = m.group(0)
			colors.add((int(c[1:3],16),int(c[3:5],16),int(c[5:],16)))
	return colors

def bg_color(c, t):
	r,g,b = c
	return f'\x1b[48;2;{r};{g};{b}m{t}\x1b[0m'

def c_hex(c):
	r,g,b = c
	return f'#{r:02x}{g:02x}{b:02x}'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("source")
	parser.add_argument("template")
	parser.add_argument("out")
	args = parser.parse_args()

	src = input_arg(args.source)
	tpl = input_arg(args.template)

	src_colors = parse_colors(src)
	tpl_colors = parse_colors(tpl)

	print(f'{args.source}:')
	for c in src_colors:
		print(bg_color(c,'        '), c_hex(c))
	print(f'{args.template}:')
	for c in tpl_colors:
		print(bg_color(c,'        '), c_hex(c))

if __name__ == "__main__":
	main()

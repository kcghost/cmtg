#!/usr/bin/env python3
import sys
import re
import argparse
import subprocess
from math import sqrt
from pathlib import Path
from pprint import pprint
import networkx as nx
from importlib.resources import read_text
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if __package__:
	from . import resources
else:
	import resources

xres_path = Path.home() / Path('.Xresources')
color_regex = re.compile("#[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]")

# https://stackoverflow.com/a/75845412/2916285
def solve_assignment(targets, sources, wf):
	graph = nx.complete_bipartite_graph(targets, sources)
	for a, b in graph.edges():
		graph.edges[a, b]['weight'] = wf(a, b)
	matching = nx.bipartite.minimum_weight_full_matching(graph)
	result = [(a, matching[a], graph.edges[a, matching[a]]['weight']) for a in targets]
	s = sum(w for _,_,w in result)
	return (result, s)

# https://en.wikipedia.org/wiki/Color_difference
def euclid_dist(c1,c2):
	r1,g1,b1 = c1
	r2,g2,b2 = c2
	return sqrt((r2-r1)**2+(g2-g1)**2+(b2-b1)**2)

def redmean_dist(c1,c2):
	r1,g1,b1 = c1
	r2,g2,b2 = c2
	cr2 = (r2-r1)**2
	cg2 = (g2-g1)**2
	cb2 = (b2-b1)**2
	rm = (r1+r2)/2
	return sqrt((2+(rm/256))*cr2+4*cg2+(2+((255-rm)/256))*cb2)

# return text for a given input argument
def input_arg(arg):
	if arg == '-':
		return sys.stdin.read()

	path = Path(arg)
	if path.exists():
		return path.read_text(encoding='utf-8')

	if arg == 'xres' and xres_path.exists():
		return subprocess.run(['cpp', '-DCMTG', str(xres_path)],
			capture_output=True, text=True, check=True).stdout

	if arg == 'appres':
		return subprocess.run(['appres', 'cmtg'],
			capture_output=True, text=True, check=True).stdout

	return read_text(resources, arg)

# write text to output argument
def output_arg(arg, text):
	if arg == '-':
		sys.stdout.write(text)
	else:
		path = Path(arg)
		path.write_text(text, encoding='utf-8')

def parse_colors(t):
	colors = []
	for line in t.splitlines():
		if (m := re.search(color_regex, line)):
			c = m.group(0)
			colors.append((int(c[1:3],16),int(c[3:5],16),int(c[5:],16)))
	# remove duplicates while preserving order
	colors = list(dict.fromkeys(colors))
	return colors

def bg_color(c, t):
	r,g,b = c
	return f'\x1b[48;2;{r};{g};{b}m{t}\x1b[0m'

def c_hex(c):
	r,g,b = c
	return f'#{r:02x}{g:02x}{b:02x}'

def p_color(s):
	for c in s:
		print(bg_color(c,'        '), c_hex(c))

def p_diff(r):
	for a, b, w in r:
		print(bg_color(a,'        '),bg_color(b,'        '),c_hex(a),c_hex(b))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("template")
	parser.add_argument("source")
	parser.add_argument("out")
	args = parser.parse_args()

	src_t = input_arg(args.source)
	tpl_t = input_arg(args.template)

	src = parse_colors(src_t)
	tpl = parse_colors(tpl_t)

	print(f'template: {args.template}:')
	p_color(tpl)
	
	print(f'source: {args.source}:')
	p_color(src)
	
	r,s = solve_assignment(tpl, src, redmean_dist)
	p_diff(r)

	r,s =solve_assignment(tpl, src, euclid_dist)
	p_diff(r)

if __name__ == "__main__":
	main()

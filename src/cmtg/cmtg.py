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
color_regex = re.compile("#[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]", re.IGNORECASE)

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

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

# https://stackoverflow.com/a/75845412/2916285
def solve_assignment(targets, sources, wf):
	# Remove entries that are in both lists
	all_targets = targets
	targets = [x for x in targets if x not in sources]
	sources = [x for x in sources if x not in all_targets]
	
	graph = nx.complete_bipartite_graph(targets, sources)
	for a, b in graph.edges():
		graph.edges[a, b]['weight'] = wf(a, b)
	matching = nx.bipartite.minimum_weight_full_matching(graph)
	result = [(t, matching[t], graph.edges[t, matching[t]]['weight']) if t in matching else (t, t, 0.00) for t in all_targets]
	s = sum(w for _,_,w in result)
	return (result, s)

# https://en.wikipedia.org/wiki/Color_difference
def euclid_dist(c1,c2):
	r1,g1,b1 = c1
	r2,g2,b2 = c2
	return sqrt((r2-r1)**2+(g2-g1)**2+(b2-b1)**2)

# Experimentally redmean is actually worse
# at least in vga color testing against its awkward yellow
def redmean_dist(c1,c2):
	r1,g1,b1 = c1
	r2,g2,b2 = c2
	cr2 = (r2-r1)**2
	cg2 = (g2-g1)**2
	cb2 = (b2-b1)**2
	rm = (r1+r2)/2
	return sqrt((2+(rm/256))*cr2+4*cg2+(2+((255-rm)/256))*cb2)

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
	for i,c in enumerate(s):
		eprint(bg_color(c,'        '), c_hex(c), f'{i:02}')

def p_diff(r,src):
	for ti,(tc,sc,w) in enumerate(r):
		si = src.index(sc)
		eprint(bg_color(tc,'        '),bg_color(sc,'        '),c_hex(tc),c_hex(sc),f'{ti:02}',f'{si:02}',f'{w:06.2f}')

# todo: intermediary with pure winxp to recognize ANSI colors?
# -ansi, src should be ansi indexed, tpl relationship to pure colors? or both?
# https://docs.python.org/3/library/colorsys.html, HSV recognition?
# Add HSV and other color space dist, then just pipe from instance to instace for intermediary
# Need to establish the best distance algo for standardizing ANSI colors
# The same for base16?
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("template")
	parser.add_argument("source")
	parser.add_argument("out")
	args = parser.parse_args()

	tpl_t = input_arg(args.template)
	src_t = input_arg(args.source)
	tpl = parse_colors(tpl_t)
	src = parse_colors(src_t)

	eprint(f'template: {args.template}:')
	p_color(tpl)

	eprint(f'source palette: {args.source}:')
	p_color(src)

	if len(tpl) > len(src):
		eprint('Not enough colors in palette!')
		exit(1)
	r,s = solve_assignment(tpl, src, euclid_dist)
	p_diff(r,src)

	for tc,sc,w in r:
		tpl_t = re.sub(c_hex(tc),c_hex(sc),tpl_t,flags=re.IGNORECASE)
	output_arg(args.out, tpl_t)

if __name__ == "__main__":
	main()

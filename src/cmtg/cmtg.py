#!/usr/bin/env python3
import sys
import re
import argparse
import subprocess
from pathlib import Path
from importlib.resources import read_text, contents
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from math import sqrt
import networkx as nx
# monkeypatch to fix colormath use of a deprecated function in numpy
import numpy
def asscalar(a):
	return a.item()
numpy.asscalar = asscalar
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import *

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
	matching = {}
	if targets:
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

def to_LabColor(c):
	r,g,b = c
	s = sRGBColor(r,g,b, is_upscaled=True)
	l = convert_color(s, LabColor)
	return l

def fromCM_dist(cm_eq):
	def cm_func(c1,c2):
		return cm_eq(to_LabColor(c1), to_LabColor(c2))
	return cm_func

dist_functions = {
	"euclidean": euclid_dist,
	"redmean": redmean_dist,
	"cie1976": fromCM_dist(delta_e_cie1976),
	"cie1994": fromCM_dist(delta_e_cie1994),
	"cie2000": fromCM_dist(delta_e_cie2000),
	"cmc":     fromCM_dist(delta_e_cmc)
}

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
		eprint(bg_color(tc,'        '),bg_color(sc,'        '),
			c_hex(tc),c_hex(sc),f'{ti:02}',f'{si:02}',f'{w:06.2f}')

def main():
	parser = argparse.ArgumentParser(
		prog='cmtg',
		description='Generate matching color theme given a template and palette'
	)
	parser.add_argument('--dist', nargs='?',
		const='cie2000', default='cie2000',
		choices=dist_functions.keys(),
		help='the color distance method (default: %(default)s)'
	)
	ex_sources = [x for x in contents(resources) if ".clr" in x]
	ex_templates = [x for x in contents(resources) if x not in ex_sources and "__" not in x]
	parser.add_argument("template", help=f'stdin, file, or builtins: {ex_templates}')
	parser.add_argument("palettes", nargs='+', help=f'stdin, file, xres, appres, or builtins: {ex_sources}')
	parser.add_argument("out", help='stdout or file')
	args = parser.parse_args()

	tpl_t = input_arg(args.template)
	tpl = parse_colors(tpl_t)
	dist = dist_functions[args.dist]

	for pal in args.palettes:
		src_t = input_arg(pal)
		src = parse_colors(src_t)
		if len(tpl) > len(src):
			eprint('Not enough colors in palette!')
			exit(1)
		r,s = solve_assignment(tpl, src, dist)
		p_diff(r,src)

		for tc,sc,w in r:
			tpl_t = re.sub(c_hex(tc),c_hex(sc),tpl_t,flags=re.IGNORECASE)
		tpl = src
	
	output_arg(args.out, tpl_t)

if __name__ == "__main__":
	main()

#!/usr/bin/env python3
import pandas as pd
import re

t = pd.read_html('https://en.wikipedia.org/wiki/ANSI_escape_code')
color_table = t[7]

for k in color_table.keys():
	name = k.split('[')[0].lower().replace(' ','_')
	if name not in ['fg', 'bg', 'name']:
		with open(f'{name}.clr', 'w') as f:
			colors = color_table[k]
			for color in colors:
				r,g,b = [int(x) for x in re.sub(r'[^0-9,]','',color.split('[')[0]).split(',')]
				f.write(f'#{r:02x}{g:02x}{b:02x}\n')

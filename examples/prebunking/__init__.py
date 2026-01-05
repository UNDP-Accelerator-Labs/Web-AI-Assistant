from sys import path as syspath
from os import listdir
from os.path import join, dirname
import json
import re

currdir = dirname(__file__)
## LOAD PROMPT CONVERTER
syspath.append(join(currdir, '..'))
from convert_to_prompt import convert

techniques = []

for fname in listdir(currdir):
	if re.search(r'^(?!__).*\.json$', fname):
		with open(join(currdir, fname), 'r') as f:
			d = json.load(f)
			techniques.append(d)

drop = ['source', 'alt']

prompt = convert(
	examples=[{k: v for k,v in d.items() if k not in drop} for d in techniques],
	agent_type='prebunking',
	technique='misinformation techniques'
)

__all__ = [
	'techniques',
	'prompt',
]
from bs4 import BeautifulSoup
from requests import get
from statistics import stdev
import re

from .vars import datum as obj

def parse(url, **kwargs):
	datum = kwargs.get('datum', obj())
	focus = kwargs.get('focus', False)

	response = get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	strings = [s for s in soup.strings if len(re.split(r'\s+', s)) > 10]
	content = ''.join([s for s in strings])

	if focus == True:
		linebreaks = list(map(len, re.findall(r'\n+', content)))
		avglinebreaks = sum(linebreaks) / len(linebreaks)
		cutoff = int(avglinebreaks + stdev(linebreaks))
		regex = r''.join(['\n' for i in range(cutoff)])
		clean_content = [re.sub(r'\s+', ' ', c.strip()) for c in re.split(regex, content)]
		return clean_content
	else:
		return re.sub(r'\n+', '\n', content)

if __name__ == '__main__':
	# url = 'https://www.lefigaro.fr/actualite-france/bruno-retailleau-devoile-son-organisation-pour-s-attaquer-aux-ecosystemes-islamistes-20250526'
	# url = 'https://edition.cnn.com/2025/05/27/us/trump-harvard-cancel-federal-contracts'
	url = 'https://www.iea.org/reports/world-energy-outlook-2024'
	parse(url)
"""
This part of the script initiates the global chat interface 
that the user will interact with. 

It takes a conversation input, and can be passed any Ollama operable model.
"""

import ollama
from ollama import chat
import json
from parsers import parse_docx, parse_pdf

from colorama import Fore # this is to colorize the terminal output

def compile_SYS_PROMT ():
	return f"""
	You are not an AI assistant that responds to a users.
	You are an AI agent that summarizes CONTEXTUAL INFORMATION provided in a json format 
	that you will pass on to an AI assistant that will respond to a USER PROMPT.
	
	You base your summary on the information provided in the "content" 
	and "title" fields of the CONTEXTUAL INFORMATION json objects.

	Only use the information provided in the CONTEXTUAL INFORMATION 
	if it is relevant for answering the USER PROMPT.
	"""

def summarize_search_result(**kwargs):
	prompt = kwargs.get('prompt')
	json_input = kwargs.get('json_input')
	stream_output = kwargs.get('stream_output', False)
	model = kwargs.get('model', 'llama3.1:8b')

	if prompt is None:
		raise Exception('missing prompt')
	if json_input is None:
		raise Exception('missing json input')

	stream: ChatResponse = chat(
		model=model, 
		options={
			'seed': 42,
			'temperature': 0.2,
			'num_ctx': 10000,
		},
		messages = [
			{
				'role': 'system',
				'content': compile_SYS_PROMT(),
			},
			{
				'role': 'user',
				'content': f"""
					CONTEXTUAL INFORMATION: {json_input}
					USER PROMPT: {prompt}
				"""
			},
		],
		stream=stream_output,
	)

	full_response = ''

	if stream_output == True:
		print('[AGENT] SEARCH SUMMARIZER:')
		for chunk in stream:
			print(chunk['message']['content'], end='', flush=True)
			full_response += chunk['message']['content']
		print('\n')
	else:
		full_response = stream['message']['content']

	return full_response

def main ():
	# file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/Homework_SystemsMap_9Nov2021.docx'
	file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/The Long Shadow of Informality--World Bank.pdf'
	doc = parse_pdf(file, chunk=True)
	prompt = 'Can you please summarize the content in the CONTEXTUAL INFORMATION?'

	summarize_search_result(prompt=prompt, json_input=doc['content'][1], stream_output=True)

if __name__ == '__main__':
	main()

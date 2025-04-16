"""
This part of the script initiates the global chat interface 
that the user will interact with. 

It takes a conversation input, and can be passed any Ollama operable model.
"""

import ollama
# from ollama import chat
from ollama_client import ollama_client

from colorama import Fore # this is to colorize the terminal output

def assistant_response (**kwargs):
	conversation = kwargs.get('conversation')
	stream_output = kwargs.get('stream_output', False)
	model = kwargs.get('model', 'llama3.2:3b-instruct-q4_1')

	if conversation is None:
		raise Exception('missing conversation')

	stream: ChatResponse = ollama_client.chat(
		model=model, 
		options= {
			'seed': 42,
			'temperature': 0.2,
			'num_ctx': 20000,
		},
		messages=conversation,
		stream=stream_output,
	)

	full_response = ''

	if stream_output == True:
		print(Fore.CYAN + 'ASSISTANT:')
		for chunk in stream:
			print(chunk['message']['content'], end='', flush=True)
			full_response += chunk['message']['content']
		print('\n')
	else:
		full_response = stream['message']['content']

	return full_response

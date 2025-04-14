"""
This part of the script derives `n_queries` strings 
to search in the desired search engine.

It takes the user prompt, the broader conversation, 
and the number of query terms to return (defaults to 3) 
as input, and can be passed any Ollama operable model.

*Notes*: the search engine is not called here. This script only 
generates a python list of search queries related to the prompt.

"""

from sys import argv
from ollama import chat
import json

def compile_SYS_PROMT (n_queries=3):
	return f"""
	You are not an AI assistant that responds to a users.
	You are an AI web search query generator that returns a list of simple search queries 
	that will then be used to search for content online using an engine like Google Search.
	
	You are given a USER_PROMPT and a CONVERSATION for context. 
	The CONVERSATION is provided as a json array of objets.
	From the USER_PROMPT and the CONVERSATION, you infer {n_queries} associated search queries 
	that you return as a Python list of strings with no syntax errors.

	It the USER_PROMPT or CONVERSATION contain important entities like dates and locations, 
	include these in all search queries. Aim for diversity of search queries.

	You retrun the Python list of search queries and nothing else. 
	The list needs to be iterable in Python directly.
	"""

def interpret_prompt (**kwargs):
	prompt = kwargs.get('prompt')
	conversation = kwargs.get('conversation', [])
	n_queries = kwargs.get('n_queries', 3)
	stream_output = kwargs.get('stream_output', False)
	model = kwargs.get('model', 'llama3.2:3b-instruct-q4_1')

	if prompt is None:
		raise Exception('missing prompt')

	stream: ChatResponse = chat(
		model=model, 
		options={
			'seed': 42,
			'temperature': 0.5,
			'num_ctx': 10000,
		},
		messages = [
			{
				'role': 'system',
				'content': compile_SYS_PROMT(n_queries),
			},
			# Few shot prompts
			{
				'role': 'user',
				'content': """
					CONVERSATION: []
					CREATE A JSON INTERPRETABLE LIST OF SEARCH QUERIES FROM THIS PROMPT: What are the most recent black metal releases?
				"""
			},
			{
				'role': 'assistant',
				'content': '["black metal releases 2023", "recent black metal albums", "new black metal music"]'
			},
			{
				'role': 'user',
				'content': """
					CONVERSATION: []
					CREATE A JSON INTERPRETABLE LIST OF SEARCH QUERIES FROM THIS PROMPT: I am a business owner looking to expand in Colombia. What do I need to know?
				"""
			},
			{
				'role': 'assistant',
				'content': '["business expansion in Colombia", "Colombia market research for entrepreneurs", "starting a business in Colombia"]'
			},
			{
				'role': 'user',
				'content': """
					CONVERSATION: [{ 'role': 'user', 'content': 'My name is Bob' }, { 'role': 'assistant', 'content': 'Hello Bob! It's nice to meet you. Is there something I can help you with, or would you like to chat for a bit?' }]
					CREATE A JSON INTERPRETABLE LIST OF SEARCH QUERIES FROM THIS PROMPT: Can you tell me about some celebrities who share my first name?
				"""
			},
			{
				'role': 'assistant',
				'content': '["celebrities named Bob", "famous people named Robert", "bob celebrity news"]'
			},
			# Actual prompt
			{
				'role': 'user',
				'content': f"""
					CONVERSATION: {conversation}
					CREATE A JSON INTERPRETABLE LIST OF SEARCH QUERIES FROM THIS PROMPT: {prompt}
				"""
			},
		],
		stream=stream_output,
	)

	full_response = ''

	if stream_output == True:
		print('[AGENT] SEARCH QUERY GENERATOR:')
		for chunk in stream:
			print(chunk['message']['content'], end='', flush=True)
			full_response += chunk['message']['content']
		print('\n')
	else:
		full_response = stream['message']['content']

	return json.loads(full_response.strip())[:int(n_queries)]

def main ():
	if len(argv) < 2:
		print ('missing prompt')
	else:
		prompt = argv[1]
		interpret_prompt(prompt=prompt, stream_output=True)

if __name__ == '__main__':
	main()
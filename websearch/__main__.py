"""
This script serves for testing the module. For running the full application,
prefer the @root/main.py file.

The general workflow in this file is inspired by: https://www.youtube.com/watch?v=9KKnNh89AGU
"""

import pprint
from sys import path as syspath
from os.path import join, dirname
import json, re

from tqdm import tqdm # this is for the loader
from colorama import Fore # this is to colorize the terminal output

# Search steps (as modules)
from .steps import *

syspath.append(join(dirname(__file__), '..'))
from preferences import connect_to_db, invalid_sources as stored_invalid_sources

def run_web_search (prompt, conversation, **kwargs):
	QUERIES = kwargs.get('n_queries', 3)
	STREAM = kwargs.get('stream_output', False)
	MODEL = kwargs.get('model', 'llama3.2')
	CONN = kwargs.get('conn', connect_to_db())
	
	# Get previously sotred invalid sources
	INVALID_SOURES = stored_invalid_sources.get(conn=CONN)
	
	# Check if additional web search is needed
	# search_needed = require_search(prompt=prompt, conversation=conversation, model=MODEL, stream_output=STREAM)
	search_needed = 'true'

	all_search_results = []
	next_prompts = []

	if search_needed == 'true':
		print(Fore.YELLOW + "A set of AI agents and workers will work to retrieve online information in order to improve your AI Assistant's response.")
		print(Fore.RED + 'Would you like to see how they reason? y/n')
		show_reasoning = input(Fore.WHITE)
		if show_reasoning.strip().lower() == 'y':
			STREAM = True
		else:
			STREAM = False

		# Interpret the prompt as a set of queries
		queries = interpret_prompt(prompt=prompt, conversation=conversation, n_queries=QUERIES, model=MODEL, stream_output=STREAM)

		# For each generated keyword, perform a search
		summaries = []
		for q in tqdm(queries, desc=Fore.YELLOW + 'iterating over online searches'):
			search_results, invalid_sources = perform_search(search=q, stream_output=STREAM, invalid_sources=INVALID_SOURES)
			all_search_results += search_results
			# Update the invalid sources
			INVALID_SOURES = invalid_sources
			# Generate a summary of the top level in formation of the search results
			summary = summarize_search_result(prompt=prompt, json_input=search_results, model=MODEL, stream_output=STREAM)
			summaries.append(summary)
		
		# Reset stream output
		STREAM = False
		# Suggest follow up prompts
		next_prompts = infer_next_prompts(prompt=prompt, json_input=[r['content'] for r in all_search_results], model=MODEL, stream_output=STREAM)
		
		if summaries is not None and len(summaries) > 0:
			conversation.append({
				'role': 'user', 
				'content': f"""
					SEARCH RESULTS: {summaries}
					USING THE SEARCH RESULTS, RESPOND AS BEST YOU CAN TO THE USER PROMPT: {prompt}
				"""
			})
		else:
			conversation.append({ 'role': 'user', 'content': prompt })
	else:
		# Reset stream output
		STREAM = False
		conversation.append({ 'role': 'user', 'content': prompt })

	response = assistant_response(conversation=conversation, model=MODEL, stream_output=False)
	# Integrate references to the response
	if len(all_search_results) > 0:
		output = integrate_sources(
			input_json=all_search_results, 
			full_response=response, 
			conservativeness=1.5, 
			limit=2
		)
	else:
		output = response
	
	# Print the output, simulating a stream
	print(Fore.CYAN + 'ASSISTANT:')
	chunk = 0
	while chunk < len(output):
		print(output[chunk:chunk+3], sep=' ', end='')
		chunk += 3

	# Add the response to the conversation thread
	conversation.append({ 'role': 'assistant', 'content': response })
	# Store the invalidated_sources
	stored_invalid_sources.add(INVALID_SOURES, conn=CONN)
	# Show the suggested follow up prompts
	if len(next_prompts) > 0:
		print(Fore.MAGENTA + '[AGENT] SUGGESTED NEXT PROMPTS:')
		print('\n'.join(next_prompts))

	return conversation

def main ():
	MODEL = 'llama3.2'
	STREAM = False

	# Initialize the conversation
	conversation = [
		{ 
			'role': 'system',
			'content': """
				You are an AI assistant that responds to a USER PROMPT.

				You have several AI agents and workers working for you to retrieve 
				relevant and up-to-date information from search enginge queries 
				using engines like Google Search. 
				These SEARCH RESULTS are passed to you as a python list of strings.
				
				You must use the SEARCH RESULTS as context to produce 
				a high quality response to the USER PROMPT. 
				Your response must be intelligible and useful to a human reader.
			"""
		}
	]

	while True:
		print(Fore.WHITE + 'USER:')
		prompt = input()

		if prompt.lower() == 'bye':
			break
		else: 
			summaries, invalid_sources = run_web_search(prompt, conversation, n_queries=3, model=MODEL, stream_output=STREAM)
			if summaries and len(summaries) > 0:
				conversation.append({
					'role': 'user', 
					'content': f"""
						SEARCH RESULTS: {summaries}
						USER PROMPT: {prompt}
					"""
				})
			else:
				conversation.append({ 'role': 'user', 'content': prompt })

			response = assistant_response(conversation=conversation, model=MODEL, stream_output=True)
			conversation.append({ 'role': 'assistant', 'content': response })


if __name__ == '__main__':
	main()
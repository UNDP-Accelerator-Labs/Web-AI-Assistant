from tqdm import tqdm # this is for the loader
from colorama import Fore # this is to colorize the terminal output
from sys import argv

from websearch import *
from memory import *
from preferences import *
from documents import *

import examples

def main ():
	# MODEL = 'llama3.2:3b-instruct-q4_1'
	MODEL = 'llama3.1:8b'
	# MODEL = 'phi3:mini'
	# MODEL = 'mistral'
	STREAM = False

	# GET PREFERENCES
	conn = connect_to_db()
	PREFERENCES = {}
	PREFERENCES['invalid_sources'] = invalid_sources.get(conn=conn)

	# Initialize memory
	DB_NAME = 'conversations'
	DB = get_vector_db(DB_NAME)

	sys_arg = 'neutral'
	if len(argv) == 2:
		arg = argv[1]
		# Check if the conversation should be altered
		if arg.lower() == 'unbiased':
			sys_arg = 'unbiased'
		elif arg.lower() == 'falsified':
			sys_arg = 'falsified'
		elif arg.lower() == 'compare':
			sys_arg = 'compare'
	
	# Initialize the conversation
	technique, system_prompt = examples.prebunking

	conversation = [
		{ 
			'role': 'system',
			'content': get_system_prompt(sys_arg),
		},
		# {
		# 	'role': 'system',
		# 	'content': system_prompt,
		# }
	]


	while True:
		print(Fore.WHITE + f'Using technique: {technique["title"]}')
		print(Fore.WHITE + 'USER:')
		prompt = input()
		# Check if there are any urls in the prompt
		# If there are urls, replace them with the content of the target page
		prompt = detect_and_replace_urls(prompt)

		if prompt.lower() == 'bye':
			close_connection(conn=conn)
			break
		elif prompt.lower()[:9] == '/memorize':
			print(conversation)
			prompt_to_memorize = conversation[-2]['content'].strip()
			print(prompt_to_memorize)
			response_to_memorize = conversation[-1]['content'].strip()
			print(response_to_memorize)
			populate_vector_db(DB, { 'prompt': prompt_to_memorize, 'response': response_to_memorize })
		elif prompt.lower()[:7] == '/search':
			conversation = run_web_search(
				prompt, 
				conversation, 
				n_queries=3, 
				model=MODEL, 
				stream_output=STREAM, 
				conn=conn
			)
		else:
			conversation.append({ 'role': 'user', 'content': prompt })
			response = assistant_response(conversation=conversation, model=MODEL, stream_output=True)
			conversation.append({ 'role': 'assistant', 'content': response })

if __name__ == '__main__':
	main()
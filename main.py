from tqdm import tqdm # this is for the loader
from colorama import Fore # this is to colorize the terminal output

from process import *
from memory import *
from preferences import *

COUNTRY = 'France'

def main ():
	MODEL = 'llama3.2'
	STREAM = False

	# GET PREFERENCES
	conn = connect_to_db()
	PREFERENCES = {}
	PREFERENCES['invalid_sources'] = invalid_sources.get(conn=conn)

	# Initialize memory
	DB_NAME = 'conversations'
	DB = get_vector_db(DB_NAME)

	# Initialize the conversation
	conversation = [
		{ 
			'role': 'system',
			'content': f"""
				You are an AI assistant that responds to a USER PROMPT.
				The user is located in {COUNTRY}. You must respond in a 
				contextually aware and appropriate manner.

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
			close_connection(conn=conn)
			break
		elif prompt.lower()[:9] == '/memorize':
			print(conversation)
			prompt_to_memorize = conversation[-2]['content'].strip()
			print(prompt_to_memorize)
			response_to_memorize = conversation[-1]['content'].strip()
			print(response_to_memorize)
			populate_vector_db(DB, { 'prompt': prompt_to_memorize, 'response': response_to_memorize })
		else: 
			summaries, list_of_invalid_sources = run_web_search(
				prompt, 
				conversation, 
				n_queries=3, 
				model=MODEL, 
				stream_output=STREAM, 
				invalid_sources=PREFERENCES['invalid_sources']
			)
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
			# Add the response to the conversation thread
			conversation.append({ 'role': 'assistant', 'content': response })
			# Store the invalidated_sources
			invalid_sources.add(list_of_invalid_sources, conn=conn)


if __name__ == '__main__':
	main()
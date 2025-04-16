"""
This part of the script determines whether a search 
is needed to respond to the user. 

It takes the user prompt, and the borader conversation as inputs,
and can be passed any Ollama operable model.

*Note*: this could be improved with some few shot prompting
as (at least the default llama3.2 instruct model tends to
often require futher search—even in seemingly unnecessary cases).
"""

from sys import argv
# from ollama import chat
from ollama_client import ollama_client

def compile_SYS_PROMT ():
	return f"""
	You are not an AI assistant that responds to a users.
	You are an AI agent who's only task is to determine 
	whether a USER_PROMPT in a CONVERSATION with an AI assistant 
	requires more information to respond correctly.

	The CONVERSATION is passed to you as a json array of objects.
	It may or may not already contain the contextual information needed.
	If the needed contextual information is not already in the CONVERSATION,
	or if the USER_PROMPT requires any further contextual information,
	the AI assistant will rely on a online search assistant to provide the context.
	
	If the AI assistant needs this extra information from an online search, 
	simply respond "True". Reasons for this include needing more recent
	or contextualized knowledge than the AI assistant has by defualt, 
	or that is available in the CONVERSATION.
	
	If the CONVERSATION already has the contextual information needed, or an
	online search is not what an intelligent human would do to respond to the USER_PROMPT,
	then you respond "False".
	
	Do not generate any explanations for your response and do not add any punctuation.
	Only generate "True" or "False" as a response using the logic in these instructions.
	"""

def require_search (**kwargs):
	prompt = kwargs.get('prompt')
	conversation = kwargs.get('conversation', [])
	stream_output = kwargs.get('stream_output', False)
	model = kwargs.get('model', 'llama3.2:3b-instruct-q4_1')

	if prompt is None:
		raise Exception('missing prompt')

	stream: ChatResponse = ollama_client.chat(
		model=model, 
		options={
			'seed': 42,
			'temperature': 0.5,
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
					CONVERSATION: {conversation}
					USER_PROMT: {prompt}
				"""
			},
		],
		stream=stream_output,
	)

	full_response = ''

	if stream_output == True:
		print('[AGENT] REQUIRE SEARCH:')
		for chunk in stream:
			print(chunk['message']['content'], end='', flush=True)
			full_response += chunk['message']['content']
		print('\n')
	else:
		full_response = stream['message']['content']

	return full_response.strip().lower()

def main ():
	if len(argv) < 2:
		print ('missing prompt')
	else:
		prompt = argv[1]
		require_search(prompt=prompt, stream_output=True)

if __name__ == '__main__':
	main()
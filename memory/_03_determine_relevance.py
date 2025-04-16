import pprint
# from ollama import chat
from ollama_client import ollama_client

def compile_SYS_PROMT():
	return """
	You are not an AI assistant that responds to a users.
	You are an AI agent that works for an AI assistant that needs to 
	determines whether a RETRIEVED SEGMENT of a previous conversation 
	contains relevant information for responding 
	to a new USER PROMPT.

	The general structure of the RETRIEVED SEGMENT is as follows:
		"PROMPT: the initial prompt of the user RESPONSE: the response of the AI assistant"
	Use both the PROMPT and the RESPONSE in the RETRIEVED SEGMENT to determine the relevance.

	Return "True" if the RETRIEVED SEGMENT is relevant.
	Return "False" if the RETRIEVED SEGMENT is not directly relevant to the USER PROMPT.
	
	Do not generate any explanations for your response and do not add any punctuation.
	Only generate "True" or "False" as a response using the logic in these instructions.
	"""

# Please provide an explanation for your response.

def determine_relevance(**kwargs):
	prompt = kwargs.get('prompt')
	document = kwargs.get('document')
	stream_output = kwargs.get('stream_output', False)
	model = kwargs.get('model', 'llama3.2:3b-instruct-q4_1')

	if prompt is None:
		raise Exception('missing prompt')
	if document is None:
		raise Exception('missing document')

	stream: ChatResponse = ollama_client.chat(
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
			# Few shot prompts
			{
				'role': 'user',
				'content': f"""
					RETRIEVED SEGMENT: "PROMPT: What is Mayhem\n\nRESPONSE: Mayhem is an infamouse black metal band from Norway."
					USER PROMPT: "Do you know about Mayhem?"
				"""
			},
			{
				'role': 'assistant',
				'content': 'True'
			},
			{
				'role': 'user',
				'content': f"""
					RETRIEVED SEGMENT: "PROMPT: My name is Bob\n\nRESPONSE: Hi Bob. How can I help you?"
					USER PROMPT: "What is my name?"
				"""
			},
			{
				'role': 'assistant',
				'content': 'True'
			},
			{
				'role': 'user',
				'content': f"""
					RETRIEVED SEGMENT: "PROMPT: Tell me more about the UNDP Accelerator Labs\n\nRESPONSE: The UNDP Accelerator Labs are a global learning network of 91 labs operating in 115 countries."
					USER PROMPT: "What is UNICEF's main mandate?"
				"""
			},
			{
				'role': 'assistant',
				'content': 'False'
			},
			# Actual prompt
			{
				'role': 'user',
				'content': f"""
					RETRIEVED SEGMENT: "{document}"
					USER PROMPT: "{prompt}"
				"""
			},
		],
		stream=stream_output,
	)

	full_response = ''

	if stream_output == True:
		print('[AGENT] RELEVANCE CLASSIFIER:')
		for chunk in stream:
			print(chunk['message']['content'], end='', flush=True)
			full_response += chunk['message']['content']
		print('\n')
	else:
		full_response = stream['message']['content']

	return full_response

def main ():
	prompt = "Do you know anything about a parisian football club?"
	determine_relevance(
		prompt=prompt, 
		document="PROMPT: What is PSG\n\nRESPONSE: PSG is the Paris Saint Germain football club of Paris.", 
		stream_output=True
	)

if __name__ == '__main__':
	main()
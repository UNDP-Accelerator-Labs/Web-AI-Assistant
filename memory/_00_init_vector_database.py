import chromadb # Documentation at: https://docs.trychroma.com/docs/querying-collections/query-and-get
from ollama import embeddings
from datetime import datetime

from os.path import join, dirname

def get_vector_db(DB_NAME):
	client = chromadb.PersistentClient(join(dirname(__file__), './chromadb'))
	# client.delete_collection(DB_NAME)
	DB = client.get_or_create_collection(
		name=DB_NAME,
		metadata={
			'description': 'my Chroma collection of local conversations',
			'created': str(datetime.now())
		}
	)
	return DB

def populate_vector_db(DB, conversation={}):
	if not conversation:
		raise Exception('missing conversation')

	# Get the last ID
	ids = DB.get(include=['documents'])['ids']
	
	if len(ids) > 0:
		conversation_id = int(ids[-1]) + 1
		# Maybe change this to uuid
	else:
		conversation_id = 0

	serialized_conversation = f"""
		PROMPT: {conversation['prompt']}
		RESPONSE: {conversation['response']}
	"""
	response = embeddings(
		model='nomic-embed-text',
		prompt=serialized_conversation.strip()
	)
	embedding = response['embedding']

	DB.add(
		ids=[str(conversation_id)],
		embeddings=[embedding],
		documents=[serialized_conversation]
	)
	return None

def delete_from_vector_db(DB, ids=[]):
	DB.delete(ids=ids)
	return None
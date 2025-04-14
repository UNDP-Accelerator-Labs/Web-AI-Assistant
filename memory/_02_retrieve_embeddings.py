from ollama import embeddings
from sys import argv, path as syspath
from os.path import join, dirname

# Custom modules
syspath.append(join(dirname(__file__), './'))
from _00_init_vector_database import get_vector_db, populate_vector_db

def retrieve_embeddings(**kwargs):
	DB = kwargs.get('DB')
	queries = kwargs.get('queries')
	n_results = kwargs.get('n_results', 3)
	stream_output = kwargs.get('stream_output', False)

	if DB is None:
		raise Exception('you must specify the vector database to retrieve chat history from')

	# embeddings = set()

	for q in queries:
		response = embeddings(
			model='nomic-embed-text',
			prompt=q
		)
		embedding = response['embedding']

		results = DB.query(query_embeddings=[embedding], n_results=n_results)
		top_results = results['documents'][0]

		return top_results

def main():
	if len(argv) < 2:
		print ('missing query')
	else:
		DB_NAME = 'conversations'
		DB = get_vector_db(DB_NAME)
		query = argv[1]
		results = retrieve_embeddings(DB=DB, queries=[query])
		print(results)

if __name__ == '__main__':
	main()
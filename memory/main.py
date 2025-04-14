# This is inspired by https://www.youtube.com/watch?v=5xPvsMX2q2M
from sys import argv, path as syspath
from os.path import join, dirname


import chromadb

# Custom modules
syspath.append(join(dirname(__file__), './'))
from _00_init_vector_database import get_vector_db, populate_vector_db, delete_from_vector_db
from _01_interpret_prompt import interpret_prompt

def main():
	DB_NAME = 'conversations'
	DB = get_vector_db(DB_NAME)
	delete_from_vector_db(DB=DB, ids=['1'])
	print(DB.get())

	if len(argv) < 2:
		print ('missing prompt')
	else:
		prompt = argv[1]
		interpret_prompt(prompt=prompt, stream_output=True)

if __name__ == '__main__':
	main()
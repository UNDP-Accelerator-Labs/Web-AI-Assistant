"""
This file contains a number of helper functions for interacting
with a sqlite database and storing user preferences regarding
online sources.

The point is to keep track locally of what the user considers
untrustworthy sources as they interact with the websearch enabled assistant.
"""

from sys import argv, path as syspath
from os.path import join, dirname

syspath.append(join(dirname(__file__), './'))
from _00_connect import connect_to_db, close_connection

def create (**kwargs):
	conn = kwargs.get('conn', None)
	conn = connect_to_db(conn=conn)
	cur = conn.cursor()

	cur.execute("""
		CREATE TABLE IF NOT EXISTS invalid_sources(
			value VARCHAR(999) UNIQUE
		)
	;""")

	conn.commit()

def get (**kwargs):
	conn = kwargs.get('conn', None)
	conn = connect_to_db(conn=conn)
	cur = conn.cursor()
	
	create(conn=conn)

	res = cur.execute("""
		SELECT * FROM invalid_sources
	;""")
	data = res.fetchall()
	conn.commit()
	
	return [d[0] for d in data]

def add (source, **kwargs):
	if source is None:
		raise Exception('missing source')

	conn = kwargs.get('conn', None)
	conn = connect_to_db(conn=conn)
	cur = conn.cursor()

	create(conn=conn)

	if type(source) == list:
		for s in source:
			cur.execute(f"""
				INSERT INTO invalid_sources(value)
				VALUES (?)
				ON CONFLICT(value) DO NOTHING
			;""", (s,))
	else:
		cur.execute(f"""
			INSERT INTO invalid_sources(value)
			VALUES (?)
			ON CONFLICT(value) DO NOTHING
		;""", (source,))

	conn.commit()

def drop (**kwargs):
	conn = kwargs.get('conn', None)
	conn = connect_to_db(conn=conn)
	cur = conn.cursor()

	cur.execute("""
		DROP TABLE invalid_sources
	;""")


if __name__ == '__main__':
	conn = connect_to_db()

	if len(argv) > 1:
		if argv[1] == 'drop':
			drop(conn=conn)
		else:
			add(source=argv[1], conn=conn)
			data = get(conn=conn)
			print(data)

	close_connection(conn)
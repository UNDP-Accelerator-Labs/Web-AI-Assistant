"""
This file contains two simple helper functions for connecting
to a local sqlite database.
"""

import sqlite3

def connect_to_db (**kwargs):
	conn = kwargs.get('conn', None)
	
	if conn is None:
		try:
			conn = sqlite3.connect('preferences/preferences.db')
		except sqlite3.OperationalError as e:
			print('Failed to open database:', e)
			conn = None
	return conn

def close_connection (conn):
	conn.close()
	print('Connection closed')
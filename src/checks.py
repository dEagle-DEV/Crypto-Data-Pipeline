import psycopg2
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def run_checks():
	with open("sql/checks.sql") as f:
		queries = f.read()
		split_queries = queries.split(";")
		updated_split_queries = [item for item in split_queries if item]

	connection = None
	cursor = None

	connection_param = {
		'dbname': os.getenv('DB_NAME'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASSWORD'),
		'host' : os.getenv('DB_HOST'),
		'port' : os.getenv('DB_PORT')
	}

	try:

		connection = psycopg2.connect(**connection_param)
		cursor = connection.cursor()
		for index, q in enumerate(updated_split_queries, start=1):
			cursor.execute(q)
			check_query = cursor.fetchall()

			if check_query != []:
				logger.warning(f"Check {index} failed: {len(check_query)} number of row(s) returned.")
			else:
				logger.info(f"Check {index} passed: {len(check_query)} number of row(s) returned.")

	except psycopg2.Error as e:
		logger.error(f"Database error: {e}")
		if connection:
			connection.rollback()

	finally:
		if cursor:
			cursor.close()
		if connection:
			connection.close()

if __name__ == "__main__":
	run_checks()


import sqlite3
import pandas as pd


def query_db(query, param=None):

	statcast_dbs = ['MLB_2015.db', 'MLB_2016.db',
					'MLB_2017.db', 'MLB_2018.db',
					'MLB_2019.db', 'MLB_2020.db']
	
	df = pd.DataFrame()

	for db in statcast_dbs:
		conn = sqlite3.connect(db)
		df = pd.concat([df, pd.read_sql(query, conn,
							params=(param,))])
		
		conn.close()

	df.to_csv(f"queries/{param}.csv", index=False)


def where_query(field_name, event):
	query_db('''SELECT *
				FROM statcast
				WHERE {} = ?'''.format(field_name), param=event)


if __name__ == "__main__":
	where_query('player_name', 'Zack Greinke')


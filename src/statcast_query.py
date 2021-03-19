import sqlite3
import pandas as pd


def query_db(query, sort_col=None, limit=None, param=None):

	statcast_dbs = ['MLB_2015.db', 'MLB_2016.db',
					'MLB_2017.db', 'MLB_2018.db',
					'MLB_2019.db', 'MLB_2020.db']
	
	df = pd.DataFrame()

	for db in statcast_dbs:
		conn = sqlite3.connect(db)
		
		if param != None:
			df = pd.concat([df, pd.read_sql(query, conn,
							params=(param,))])
		else:
			df = pd.concat([df, pd.read_sql(query, conn)])
		
		conn.close()

	
	if limit != None:
		sort_df(df, sort_col)
		save_df(df.head(limit), sort_col, limit)
	else:
		save_df(df, param)


def sort_df(df, sort_col):
	df.sort_values(sort_col, ascending=False, inplace=True)


def save_df(df, param, limit='all'):
	df.to_csv(f"queries/{param}_{limit}.csv", index=False)
	print(f"Dataframe saved as {param}_{limit}.csv")


def top_query(stat, limit):
	query_db('''SELECT *
				FROM statcast
				ORDER BY {} DESC
				LIMIT {}'''.format(stat, limit), sort_col=stat, limit=limit)


def where_query(field_name, event):
	query_db('''SELECT *
				FROM statcast
				WHERE {} = ?'''.format(field_name), param=event)


def two_where_query(stat1, stat2, param=None):
	query_db('''SELECT *
			FROM statcast
			WHERE {} IS NOT NULL
			AND {} = ?'''.format(stat1, stat2), param=param)


if __name__ == "__main__":
	#top_query('release_speed', 100)
	#top_query('launch_speed', 100)
	#where_query('events', strikeout')
	#two_where_query('events', 'strikes', param=2)
	where_query('player_name', 'Aaron Nola')


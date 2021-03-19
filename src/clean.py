import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def id_parser(df):
    '''
    Takes specific player ID, renames the fields, and merges with df.
    '''
    pid=pd.read_csv('PLAYERIDMAP.csv')
    pid=pid[["PLAYERNAME", "MLBID"]]
    pid=pid.dropna(how='any', axis=0)
    pid=pid.rename(columns={"PLAYERNAME": "batter_name", "MLBID": "batter"})
    pid=pid.astype({"batter": 'int64'})
    return df.merge(pid)


def rename_pitch(df, old_name, new_name):
    '''
    Args: df, str, str
    Renames pitch_type in df.
    Outs: None
    '''
    for ix, pitch in enumerate(df["pitch_type"]):
        if pitch == old_name:
            df.at[ix, "pitch_type"] = new_name
            
            
def standardize_pitches(df):
    rename_pitch(df, "KC", "CU")
    rename_pitch(df, "FT", "SI")
    
    for ix, pitch in enumerate(df["pitch_type"]):
        if pitch not in ["FF","CU","SI","CH",
                         "FO","KN","SL","EP","FC"]:
            df.drop(ix, axis=0, inplace=True)
            
    
def runners_binary(df):
    for col in ['on_3b', 'on_2b', 'on_1b']:
        df[col] = df[col] > 0
        df[col] = pd.get_dummies(df[col])
        #Dummies made it look like runners are always on
        df[col] = np.logical_xor(df[col],1).astype(int)
      

def sort_df(df):
    df['game_date'] = pd.to_datetime(df['game_date'])
    df=df.sort_values(['game_date', 'at_bat_number', 'pitch_number'], ascending=[True, True, True])
    df.reset_index(inplace=True)
    df=df.drop(columns=['index'],  axis=1)
    return df


def stat_histories(df):
	#Average wOBA and launch speed angle calculated as average of all previous plate appearances for individual batter.
	df["woba_hist"] = None
	df["lsangle_hist"] = None
	df["prev_hth"] = 0

	for bid in df.batter.unique():
	    hist = df[df.batter==bid][df.woba_value>=0]
	    while hist.shape[0] > 1:
	        df.woba_hist.iloc[hist.index[-1]] = hist[:-1].woba_value.mean()
	        df.lsangle_hist.iloc[hist.index[-1]] = hist[:-1].launch_speed_angle.mean()
	        df.prev_hth.iloc[hist.index[-1]] = hist.shape[0]-1
	        hist.drop(hist.index[-1], inplace=True)

	#backfill above categories for whole at-bat
	x = df.shape[0]-1
	for ix, fill in enumerate(reversed(df.woba_hist)):
	    if ix==x:
	        break
	    if isinstance(fill, float):
	        if df.batter[x-ix] == df.batter[x-ix-1]:
	            df.woba_hist[x-ix-1] = fill
	            
	for ix, fill in enumerate(reversed(df.prev_hth)):
	    if ix==x:
	        break
	    if df.batter[x-ix] == df.batter[x-ix-1]:
	        df.prev_hth[x-ix-1] = fill
	        
	for ix, fill in enumerate(reversed(df.lsangle_hist)):
	    if ix==x:
	        break
	    if isinstance(fill, float):
	        if df.batter[x-ix] == df.batter[x-ix-1]:
	            df.lsangle_hist[x-ix-1] = fill

	#Delete noisy values for thin histories
	for ix, p in enumerate(df.prev_hth):
	    if p < 5:
	        df.woba_hist[ix] = None
	        df.lsangle_hist[ix] = None

def pitch_features(df):
	#Makes a string from strikes and balls
	df["count_id"] = None
	for ix, (b,s) in enumerate(zip(df.balls, df.strikes)):
	    df.count_id[ix] = str(b)+"-"+str(s)
	    
	#Create pitch count & batter count.
	df["pitch_count"] = None
	df["batter_count"] = None
	x=len(df.game_pk)-1
	i, b = 0, 1

	for ix, pk in enumerate(df.game_pk):
	    i += 1
	    df.pitch_count[ix]=i
	    df.batter_count[ix]=b
	    
	    if ix==x:
	        break
	    if df.batter[ix] != df.batter[ix+1]:
	        b += 1
	    if pk != df.game_pk[ix+1]:
	        i=0
	        b=1

def pitch_histories(df):
	#Last pitch and average pitch histories
	df["pitch_last"] = None

	for ix, p in enumerate(df.pitch_type):
	    if ix == df.shape[0]-1:
	        break
	        
	    df.pitch_last[ix+1] = p
	    
	    if df.pitch_count[ix] == 2:
	        df.pitch_last[ix-1] = None


	#Pitch thrown to individual batter based on all past pitches
	df["pitch_hist"] = None

	for bid in df.batter.unique():
	    hist = df[df.batter==bid][["batter", "pitch_type"]]
	    while hist.shape[0] > 1:
	        ix = hist.index[-1] 
	        hist.drop(hist.index[-1], inplace=True) #no leakage - don't calculate based on current pitch
	        commonest_pitch = hist.groupby(["pitch_type"]).agg({"pitch_type": "count"}).pitch_type.sort_values(ascending=False).index[0]
	        df.pitch_hist.iloc[ix] = commonest_pitch
	
	#Predict most common pitch by pitch number
	df["pitch_common"] = None

	for ix, n in enumerate(df.pitch_common):
	    if n==1:
	        df.pitch_common[ix]="FF" #Nola only
	    else:
	        df.pitch_common[ix]="CU" #Nola only


def velocities(df):
	#Last 3 pitches velo. gradient
	from scipy.stats import linregress
	df["velo_grad"] = None
	df["last_velo"] = None
	x = [1,2,3]

	for ix, _ in enumerate(df.release_speed):
		if df.pitch_count[ix] > 1:
			df.last_velo[ix] = df.release_speed[ix-1]
		if df.pitch_count[ix] > 3:
			y = df.release_speed[ix-3:ix]
			df.velo_grad[ix] = linregress(x,y)[0]

def mean_backfill(df):
	grad_mean = np.mean(df.velo_grad)
	velo_mean = np.mean(df.last_velo)
	woba_mean = np.mean(df.woba_hist)
	lsangle_mean = np.mean(df.lsangle_hist)

	values = {"woba_hist": woba_mean, "lsangle_hist": lsangle_mean,
				"pitch_last": "CU", "pitch_hist": "CU",
				"last_velo": velo_mean, "velo_grad": grad_mean}

	df.fillna(value=values, inplace=True) #Nola only


if __name__ == "__main__":
	player = "Aaron Nola"
	df = pd.read_csv(f"queries/{player}_all.csv")
	df = df[['player_name', 'game_date', 'pitch_type', 'batter', 'game_pk',
 				'at_bat_number', 'pitch_number', 'inning', 'bat_score',
				'fld_score', 'balls', 'release_speed', 'strikes', 'on_3b',
				'on_2b', 'on_1b', 'woba_value', 'launch_speed_angle']]
	df = id_parser(df)
	standardize_pitches(df)
	runners_binary(df)
	df=sort_df(df)
	df["runner_pressure"] = (df.on_1b+2*df.on_2b+3*df.on_3b)/6.
	df["score_diff"] = df.fld_score - df.bat_score
	stat_histories(df)
	pitch_features(df)
	pitch_histories(df)
	velocities(df)
	mean_backfill(df)
	df=pd.concat([df,pd.get_dummies(df.count_id)], axis=1) #Add count inputs
	df.drop(columns=['woba_value', 'launch_speed_angle', 'release_speed', 'fld_score',
					'balls', 'strikes', 'bat_score', 'on_3b', 'on_2b', 'on_1b', 'count_id'],  axis=1, inplace=True)
	
	#Multinomial only
	for ix, p in enumerate(["FF","SI","CU","CH"]): df=df.replace(p,ix)
	df.to_csv(f"queries/{player}_features.csv", index=False)

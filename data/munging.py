import pandas as pd


def player_id_parser(filename, columns, names):
    '''
    Takes specific player ID, renames the fields, and merges with df.
    '''
    pid=pd.read_csv(f'{filename}.csv')
    pid=pid[[columns[0], columns[1]]]
    pid.dropna(how='any', axis=0, inplace=True)
    pid.rename(columns={columns[0]:names[0], columns[1]:names[1]},
               inplace=True)
    pid=pid.astype({names[1]:'int64'})
    return pid


def merge_id(df):
    pid = player_id_parser("PLAYERIDMAP",
                            ["PLAYERNAME", "MLBID"],
                            ["batter_name", "batter"])
    return df.merge(pid)
    
    
def drop_na(filename):
    '''
    Drops depracated fields and sorts by date
    '''
    df=pd.read_csv(f'{filename}.csv')
    df.dropna(how='all', axis=1, inplace=True)
    df.drop(columns=['index'], axis=1, inplace=True)
    df.sort_values(by='game_date', inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=['index'], axis=1, inplace=True)
    
    return df


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
            
            
def save_df(df, file_name):
    '''
    Args: df, str
    Outs: None
    '''
    df.to_csv(f'{file_name}.csv', index=False)
    
    
def dummyize(df, columns):
    for col in columns:
        df[col] = pd.get_dummies(df[col])
        
        
def boolyize(df, columns):
    for col in columns:
        df[col] = df[col]>0

        
def create_index(df):
    df['game_date'] = pd.to_datetime(df['game_date'])
    #Create index because sv_id was incomplete
    df["pitch_index"] = None
    for ix, d in enumerate(df.game_date):
        df["pitch_index"][ix] = d.strftime("%Y%m%d") + str(df.at_bat_number[ix]).zfill(2) + str(df.pitch_number[ix]).zfill(2)
    return df.sort_values(by='pitch_index')
    
    
if __name__ == "__main__":
    
    nola = drop_na("Nola_all")
    nola = merge_id(nola)
    standardize_pitches(nola)
    nola = nola[['player_name', 'batter_name', 'game_date', 'home_team', 'away_team', 'pitch_type', 'batter',
                 'at_bat_number', 'pitch_number', 'inning', 'bat_score', 'fld_score', 'stand', 'balls', 
                 'strikes', 'outs_when_up', 'inning_topbot', 'on_3b', 'on_2b', 'on_1b', 'woba_value',
                 'launch_speed_angle', 'description', 'des']]
    
    
    nola['game_date'] = pd.to_datetime(nola['game_date'])
    boolyize(nola, ['on_3b', 'on_2b', 'on_1b'])
    #L is 1, R is 0; Bot is 1, Top is 0; on-base is 0, 1 is not
    dummyize(nola, ['stand', 'inning_topbot', 'on_3b', 'on_2b', 'on_1b'])
    #nola = create_index(nola)
    save_df(nola, "Nola_clean")
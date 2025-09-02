def calculate_dk_points(df, prefix=''):
    return (
        df[f'{prefix}PTS'] +
        df[f'{prefix}REB'] * 1.25 + 
        df[f'{prefix}AST'] * 1.5 + 
        df[f'{prefix}STL'] * 2.0 + 
        df[f'{prefix}BLK'] * 2.0 + 
        df[f'{prefix}FG3M'] * 0.5 + 
        df[f'{prefix}TO'] * (-0.5) + 
        df[f'{prefix}DOUBLE_DOUBLE'] * 1.5 + 
        df[f'{prefix}TRIPLE_DOUBLE'] * 3.0
    )

def got_double_double(df):
    return ((
        (df['PTS'] >= 10).astype(int) + 
        (df['REB'] >= 10).astype(int) + 
        (df['AST'] >= 10).astype(int) + 
        (df['STL'] >= 10).astype(int) + 
        (df['BLK'] >= 10).astype(int)  
    ) >= 2).astype(int)

def got_triple_double(df):
    return ((
        (df['PTS'] >= 10).astype(int) + 
        (df['REB'] >= 10).astype(int) + 
        (df['AST'] >= 10).astype(int) + 
        (df['STL'] >= 10).astype(int) + 
        (df['BLK'] >= 10).astype(int)  
    ) >= 3).astype(int)

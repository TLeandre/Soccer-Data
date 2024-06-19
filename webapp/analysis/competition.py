from mplsoccer import Sbopen
import pandas as pd

def get_competition() -> pd.core.frame.DataFrame:
    """
    Information on each match 

    Returns:
        pd.core.frame.DataFrame: information on each match 
    """
    parser = Sbopen()

    df_match = parser.match(competition_id=43, season_id=106)
    df_match[['match_id', 'match_date', 
            'home_score', 'away_score', 
            'home_team_name', 'away_team_name', 
            'competition_stage_name', 'stadium_name', 
            'referee_name']]
    
    return df_match

def get_matchs(df_match: pd.core.frame.DataFrame, competition_stage:str) -> pd.core.frame.DataFrame:
    """
    Information on each match filtered by competition stage

    Args:
        df_match (pd.core.frame.DataFrame): Information on each match 
        competition_stage (str): competition stage 

    Returns:
        pd.core.frame.DataFrame: Information on each match filtered by competition stage
    """
    df_match_filtered = df_match.loc[df_match.competition_stage_name == competition_stage,
                                     ['match_id', 'match_date', 'home_score', 'away_score', 'home_team_name', 
                                      'away_team_name', 'competition_stage_name', 'stadium_name', 'referee_name']]
    df_match_filtered['teams'] = df_match_filtered['home_team_name'] + ' vs ' + df_match_filtered['away_team_name']
    
    return df_match_filtered
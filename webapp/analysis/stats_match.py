import numpy as np
import pandas as pd
from mplsoccer import Sbopen
from matplotlib.colors import LinearSegmentedColormap

class stat_match:

    def __init__(self, id_match: np.int64):
        """
        Match Data recovery 

        Args:
            id_match (np.int64): id match
        """
        parser = Sbopen()

        self.df_event = parser.event(id_match)[0]
        self.teams = self.df_event.team_name.unique()
        self.colors = ['#3e5eeb','#ff3131']
        
        blue = np.array([0.243, 0.369, 0.922])  # #3E5EEB
        white_blue = np.array([0.925, 0.937, 0.992])  # #eceffd
        red = np.array([1.0, 0.192, 0.192])  # #cc2727
        white_red = np.array([1.0, 0.917, 0.917])  # #ffeaea
        
        blue_cmap = [white_blue * (1 - i/9) + blue * (i/9) for i in range(10)]
        red_cmap = [white_red * (1 - i/9) + red * (i/9) for i in range(10)]

        self.cmap = [LinearSegmentedColormap.from_list('blue_cmap', blue_cmap),
                     LinearSegmentedColormap.from_list('red_cmap', red_cmap)]

    def get_events(self) -> pd.core.frame.DataFrame:
        """
        Position of event data for each team

        Returns:
            pd.core.frame.DataFrame: position event data
        """
        events = []
        for team in self.teams:
            events.append(self.df_event.loc[self.df_event.team_name == team, ['x', 'y']])
    
        return events

    def get_shots_compact(self) -> list:
        """
        All shot during the match 

        Returns:
            list: shots
        """
        mask_shots = (self.df_event.type_name == 'Shot')
        shots = self.df_event.loc[mask_shots, ['x', 'y', 'end_x', 'end_y', 'outcome_name', 'shot_statsbomb_xg', 'player_name', 'team_name']]
    
        return shots
        
    def get_shots(self) -> list:
        """
        Shot for each team

        Returns:
            list: shot of team
        """
        shots = []
        for team in self.teams:
            mask_shots = (self.df_event.type_name == 'Shot') & (self.df_event.team_name == team)
            shots.append(self.df_event.loc[mask_shots, ['x', 'y', 'end_x', 'end_y', 'outcome_name', 'shot_statsbomb_xg','player_name']])
    
        return shots
    
    def get_xG(self) -> pd.core.frame.DataFrame:
        """
        Cumulative xG for each shot

        Returns:
            pd.core.frame.DataFrame: xG data
        """
        mask_xG = (self.df_event.type_name == 'Shot')
        xG = self.df_event.loc[mask_xG, ["period", "minute", "shot_statsbomb_xg", "team_name", "player_name", "outcome_name"]]  

        xG.rename(columns = {"shot_statsbomb_xg":"xG", "outcome_name":"result"}, inplace = True)
        xG.sort_values(by=["team_name","period","minute"], inplace=True)
        xG['cumul_xG'] = xG.groupby('team_name')['xG'].cumsum()

        start_rows = pd.DataFrame([
            {'period': 1, 'minute': 0, 'xG': 0., 'team_name': self.teams[0], 'player_name':"start", 'result':"start", 'cumul_xG': 0,},
            {'period': 1, 'minute': 0, 'xG': 0., 'team_name': self.teams[1], 'player_name':"start", 'result':"start", 'cumul_xG': 0,}
        ])
        xG = pd.concat([start_rows, xG], ignore_index=True)

        return xG 

    def get_statistics(self) -> pd.core.frame.DataFrame:
        """
        Statistics for each team on various actions 

        Returns:
            pd.core.frame.DataFrame: Statistic data
        """
        statistics = {'name': [], self.teams[0]: [], self.teams[1]: [], 'cumul': []}
        actions = ['Shot', 'Pass', 'Duel', 'Foul Committed', 'Dribble', 'Interception']

        for action in actions:
            mask = (self.df_event.type_name == action)
            action_counts = self.df_event.loc[mask, ['team_name']].groupby(['team_name']).size()
            
            for team in self.teams:
                if team not in action_counts:
                    action_counts[team] = 0

            statistics['name'].append(action)
            statistics[self.teams[0]].append(action_counts[self.teams[0]])
            statistics[self.teams[1]].append(action_counts[self.teams[1]])
            statistics['cumul'].append(action_counts[self.teams[0]] + action_counts[self.teams[1]])

        statistics = pd.DataFrame(statistics)

        return statistics

    def get_passing_network(self) -> tuple:
        """
        Size, position of players and link between them 

        Returns:
            tuple: position, line
        """
        teams_scatter_df = []
        teams_lines_df = []
    
        for team in self.teams:
            #first sub
            sub = self.df_event.loc[self.df_event["type_name"] == "Substitution"].loc[self.df_event["team_name"] == team].iloc[0]["index"]
            #successfull passes until the first substitution
            mask_pass = ((self.df_event.type_name == 'Pass') & (self.df_event.team_name == team) & 
                         (self.df_event.index < sub) & (self.df_event.outcome_name.isnull()) & 
                         (self.df_event.sub_type_name != "Throw-in"))
            df_pass = self.df_event.loc[mask_pass, ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]]
            #surname of a player
            df_pass["player_name"] = df_pass["player_name"].apply(lambda x: str(x).split()[-1])
            df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].apply(lambda x: str(x).split()[-1])
    
            scatter_df = pd.DataFrame()
            for i, name in enumerate(df_pass["player_name"].unique()):
                passx = df_pass.loc[df_pass["player_name"] == name]["x"].to_numpy()
                recx = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
                passy = df_pass.loc[df_pass["player_name"] == name]["y"].to_numpy()
                recy = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
                scatter_df.at[i, "player_name"] = name
                #average x and y location
                scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
                scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))
                #calculate number of passes
                scatter_df.at[i, "no"] = df_pass.loc[df_pass["player_name"] == name].count().iloc[0]

            scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max() * 1500)
    
            df_pass["pair_key"] = df_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
            lines_df = df_pass.groupby(["pair_key"]).x.count().reset_index()
            lines_df.rename({'x':'pass_count'}, axis='columns', inplace=True)
            #minimum pass
            lines_df = lines_df[lines_df['pass_count']>2]
    
            teams_scatter_df.append(scatter_df)
            teams_lines_df.append(lines_df)
    
        return teams_scatter_df, teams_lines_df
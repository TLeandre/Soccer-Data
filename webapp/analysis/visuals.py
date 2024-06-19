import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from mplsoccer import Pitch, Sbopen, VerticalPitch


def display_events(events : pd.core.frame.DataFrame, color: str):
    """
    KDE plot on event team 

    Args:
        events (pd.core.frame.DataFrame): all events
        color (str): team cmap color

    """
    pitch = Pitch(line_color='#1c2632', line_zorder=2, 
                  corner_arcs=True, linewidth=1.5)
    fig, ax = pitch.draw(figsize=(4.4, 6.4))

    kde = pitch.kdeplot(events.x, events.y, ax=ax, 
                        fill=True, levels=25, thresh=0, 
                        cut=20, cmap=color)
    
    return fig

def display_passing_network(scatter_df: pd.core.frame.DataFrame, lines_df: pd.core.frame.DataFrame, team: str, color: str):
    """
    Passing Network Plot 

    Args:
        scatter_df (pd.core.frame.DataFrame): player positions 
        lines_df (pd.core.frame.DataFrame): number of passes between two players  
        team (str): team name
        color (str): team color

    """
    pitch = Pitch(line_color='#1c2632', line_zorder=2, corner_arcs=True,
                          linewidth=4)
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                         endnote_height=0.0, title_space=0, endnote_space=0)
    
    #scatter
    pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color=color, 
                  edgecolors='grey', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)
    for i, row in scatter_df.iterrows():
        pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', 
                       ha='center', weight = "bold", size=16, ax=ax["pitch"], zorder = 4)
    
    #arrow
    for i, row in lines_df.iterrows():     
        player1 = row["pair_key"].split("_")[0]
        player2 = row['pair_key'].split("_")[1]
        #take the average location of players to plot a line between them
        player1_x = scatter_df.loc[scatter_df["player_name"] == player1]['x'].iloc[0]
        player1_y = scatter_df.loc[scatter_df["player_name"] == player1]['y'].iloc[0]
        player2_x = scatter_df.loc[scatter_df["player_name"] == player2]['x'].iloc[0]
        player2_y = scatter_df.loc[scatter_df["player_name"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        #adjust the line width so that the more passes, the wider the line
        line_width = (num_passes / lines_df['pass_count'].max() * 10)
        pitch.lines(player1_x, player1_y, player2_x, player2_y,alpha=1, 
                    lw=line_width, zorder=2, color=color, ax = ax["pitch"])
    
    return fig

def display_shots_separate_pitch(shots: pd.core.frame.DataFrame, teams: np.ndarray, colors: np.ndarray):
    """
    Shot for each team on different Plot

    Args:
        shots (pd.core.frame.DataFrame): shots
        teams (np.ndarray): team names 
        colors (np.ndarray): team colors

    """
    pitch = VerticalPitch(pad_left=-10, pad_right=-10, pad_bottom=-30,
                          line_color='#1c2632', corner_arcs=True,
                          half = True, linewidth=5)
    fig, axs = pitch.grid(ncols=2, endnote_height=0, title_height=0)

    #each team
    for i, ax in enumerate(axs):
        df_team = shots[shots.team_name == teams[i]]
        #each shot
        for j, row in df_team.iterrows():
            if row["outcome_name"] == 'Goal':
                pitch.arrows(row.x, row.y, row.end_x, row.end_y, headwidth=4, headlength=4, color=colors[i], ax=ax)
                pitch.scatter(row.x, row.y, alpha = 1, s = 700, c = colors[i], ax=ax, marker='football') 
                pitch.annotate(row["player_name"], (row.x - 2, row.y - 2), ax=ax, fontsize = 12)
            else:
                pitch.scatter(row.x, row.y, alpha = 0.5, s = 700, color = colors[i], ax=ax)

    return fig 

def display_statistics(statistics: pd.core.frame.DataFrame, teams: np.ndarray, colors: np.ndarray):
    """
    Statistics Plot for each team

    Args:
        statistics (pd.core.frame.DataFrame): statistics
        teams (np.ndarray): team names 
        colors (np.ndarray): team colors

    """
    fig, axs = plt.subplots(len(statistics), 1, figsize=(8, 4))

    #each statistics
    for i, row in enumerate(statistics.itertuples()):
        axs[i].barh(0, row[2], color=colors[0])
        axs[i].barh(0, row[3], left=row[2], color=colors[1])
        axs[i].text(row[2] / 2, 0, f'{row[2]}', va='center', ha='center', color='white', fontsize=12)
        axs[i].text(row[2] + row[3] / 2, 0, f'{row[3]}', va='center', ha='center', color='black', fontsize=12)
        axs[i].set_title(row[1])
        axs[i].set_axis_off()

    plt.tight_layout()
    
    return fig

def display_shots_same_pitch(shots: pd.core.frame.DataFrame, teams: np.ndarray, colors: np.ndarray):
    """
    Shot for each team on same Plot

    Args:
        shots (pd.core.frame.DataFrame): shots
        teams (np.ndarray): team names 
        colors (np.ndarray): team colors

    """
    pitch = Pitch(pad_top=0.05, pad_right=0.05, pad_bottom=0.05, pad_left=0.05, line_zorder=2)    
    fig, axs = pitch.jointgrid(figheight=10, left=None, bottom=0.075, grid_height=0.8, 
                               axis=False, title_height=0, endnote_height=0)
    
    df_team1 = shots[shots.team_name == teams[0]]
    df_team2 = shots[shots.team_name == teams[1]]
    #change shot side 
    df_team1['x'] = pitch.dim.right - df_team1.x
    #add histogram
    team1_hist_y = sns.kdeplot(y=df_team1.y, ax=axs['left'], color=colors[0], fill=True)
    team1_hist_x = sns.kdeplot(x=df_team1.x, ax=axs['top'], color=colors[0], fill=True)
    team2_hist_x = sns.kdeplot(x=df_team2.x, ax=axs['top'], color=colors[1], fill=True)
    team2_hist_y = sns.kdeplot(y=df_team2.y, ax=axs['right'], color=colors[1], fill=True)
    #team 1 
    for i, row in df_team1.iterrows():
        if row["outcome_name"] == 'Goal':
            pitch.scatter(row.x, row.y, s=row.shot_statsbomb_xg * 700, c=colors[0], ax=axs['pitch'])
        else:
            pitch.scatter(row.x, row.y, alpha = 0.5, s=row.shot_statsbomb_xg * 700, color = colors[0], ax=axs['pitch'])
    #team 2
    for i, row in df_team2.iterrows():
        if row["outcome_name"] == 'Goal':
            pitch.scatter(row.x, row.y, s=row.shot_statsbomb_xg * 700, c=colors[1], ax=axs['pitch'])
        else:
            pitch.scatter(row.x, row.y, alpha = 0.5, s=row.shot_statsbomb_xg * 700, color = colors[1], ax=axs['pitch'])

    return fig


def display_shots_one_team(shots: pd.core.frame.DataFrame, team: str, color: str):
    """
    Shot Plot for one team

    Args:
        shots (pd.core.frame.DataFrame): shots
        team (str): team name
        color (str): team color

    """
    pitch = VerticalPitch(pad_left=-5, pad_right=-5, pad_bottom=-20,
                          line_color='#1c2632', corner_arcs=True,
                          half = True, linewidth=3)
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.1, axis=False,
                         endnote_height=0.0, title_space=0, endnote_space=0)

    for i, row in shots.iterrows():
        if row["outcome_name"] == 'Goal':
            pitch.scatter(row.x, row.y, alpha = 1, s = 500, c = color, ax=ax['pitch'], marker='football') 
            pitch.arrows(row.x, row.y, row.end_x, row.end_y, ax=ax['pitch'])
            pitch.annotate(row["player_name"], (row.x - 2, row.y - 2), ax=ax['pitch'], fontsize = 12)
        else:
            pitch.scatter(row.x, row.y, alpha = 0.5, s = 500, color = color, ax=ax['pitch'])

    return fig

def display_xG(xG: pd.core.frame.DataFrame, teams: np.ndarray, colors: list): 
    """
    Cumulative xG Plot

    Args:
        xG (pd.core.frame.DataFrame): xG informations 
        teams (np.ndarray): team names 
        colors (np.ndarray): team colors

    """
    fig, ax = plt.subplots(figsize=(14, 4))

    team1_df = xG[xG['team_name'] == teams[0]]
    team2_df = xG[xG['team_name'] == teams[1]]
    #plot line
    ax.step(team1_df['minute'], team1_df['cumul_xG'], where = 'post', color=colors[0], label=teams[0], linewidth=3)
    ax.step(team2_df['minute'], team2_df['cumul_xG'], where = 'post', color=colors[1], label=teams[1], linewidth=3)
    #team 1 annotation
    for i, row in team1_df[team1_df['result'] == "Goal"].iterrows():
            ax.annotate(f"{team1_df['player_name'][i]}", (team1_df['minute'][i], team1_df['cumul_xG'][i]),xycoords='data',ha='center',
                    xytext=(-90, 50), textcoords='offset points', arrowprops=dict(arrowstyle="->",connectionstyle="arc,angleA=0,armA=50,rad=10", color = colors[0]))
    #team 2 annotation
    for i, row in team2_df[team2_df['result'] == "Goal"].iterrows():
            ax.annotate(f"{team2_df['player_name'][i]}", (team2_df['minute'][i], team2_df['cumul_xG'][i]),xycoords='data',ha='center',
                    xytext=(-90, 50), textcoords='offset points', arrowprops=dict(arrowstyle="->",connectionstyle="arc,angleA=0,armA=50,rad=10", color = colors[1]))
            
    ax.set_title('Evolution of xG and Goals')
    ax.set_xlim(0, 90)

    ax.tick_params(axis='both', length=0)

    ax.axvline(x=45, color='grey', linestyle='--')
    ax.axvline(x=89.95, color='grey', linestyle='--')

    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.grid(axis='y')
            
    return fig
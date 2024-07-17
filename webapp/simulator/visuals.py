import matplotlib.pyplot as plt
import pandas as pd

from mplsoccer import Pitch, Sbopen, VerticalPitch

PAD = 0.2
pitch_spec = {'pad_left': 10, 'pad_right': 10,
              'pad_bottom': PAD, 'pad_top': PAD, 'pitch_color': 'None'}
pitch_width, pitch_length = 68, 105

def display_state(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame):
    """
    Position players plot

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    """
    gk = pd.DataFrame([track.iloc[0,:]])
    track = track.iloc[1:,:]

    pitch = VerticalPitch(half=True, pitch_type='custom', line_zorder=0, corner_arcs=True,
                          linewidth=2, pitch_width=pitch_width, pitch_length=pitch_length,
                   line_color='#1c2632', **pitch_spec)
    
    fig, axs = pitch.grid(figheight=7, endnote_height=0, 
                          title_height=0.001, title_space=0,
                          axis=False,
                          grid_height=0.83)
    
    # Plot the players
    sc1 = pitch.scatter(shot.x, shot.y, marker='football', s=150, label='Shooter', ax=axs['pitch'])
    sc2 = pitch.scatter(track.x, track.y, s=150, c='#5ba965', label='Defender', ax=axs['pitch'])
    sc3 = pitch.scatter(gk.x, gk.y, s=150, c='#5b0965', label='Goalkeeper', ax=axs['pitch'])
    
    # plot the angle to the goal
    pitch.goal_angle(shot.x, shot.y, ax=axs['pitch'], alpha=0.2, zorder=1.1,
                     color='#cb5a4c', goal='right')
    
    legend = axs['pitch'].legend(loc='lower left',  bbox_to_anchor=(0.12, 0.01, 0.5, 0.5), labelspacing=2.5)
    
    return fig
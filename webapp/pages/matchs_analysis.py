import streamlit as st
from analysis import competition 
from analysis import stats_match
from analysis import visuals

st.set_page_config(
    page_title="Matchs analysis",
    page_icon=":soccer:",
    layout="wide"
)

st.title("Matchs analysis")

st.markdown(
    """
    Faudra écrire un peu de markdown pour présenter ce qui est dispo sur cette page 
"""
)

df_match = competition.get_competition()

col_button1, col_button2 = st.columns(2)

with col_button1:
    competition_stage = st.selectbox(
        "Selectionner votre partie de la compétition ",
        df_match.competition_stage_name.unique())
    df_filtered_match = competition.get_matchs(df_match, competition_stage)

with col_button2:
    teams = st.selectbox(
        "Sélectionnez un match", 
        df_filtered_match['teams'])

    id_match = df_filtered_match[df_filtered_match['teams'] == teams]['match_id'].values[0]
    match_info = df_filtered_match[df_filtered_match['teams'] == teams]

st.divider()

match_tilte = f'{match_info.home_team_name.values[0]} {match_info.home_score.values[0]} - {match_info.away_score.values[0]} {match_info.away_team_name.values[0]}'

st.markdown(
    f"""
    <h1 style='text-align: center; color: black;'>{match_tilte}</h1>
    <h5 style='text-align: center; color: grey;'>Stadium : {match_info.stadium_name.values[0]}</h5>
    <h5 style='text-align: center; color: grey;'>Referee : {match_info.referee_name.values[0]}</h5>
    """ , unsafe_allow_html=True)   

st.divider()

team1, all, team2 = st.columns([0.3,0.4,0.3])

match = stats_match.stat_match(id_match)

with team1:
    st.pyplot(visuals.display_events(match.get_events()[0], match.cmap[0]))
    st.pyplot(visuals.display_passing_network(match.get_passing_network()[0][0], match.get_passing_network()[1][0], match.teams[0], match.colors[0]))

with all:
    st.pyplot(visuals.display_xG(match.get_xG(), match.teams, match.colors))
    st.pyplot(visuals.display_shots_separate_pitch(match.get_shots_compact(), match.teams, match.colors))
    st.pyplot(visuals.display_statistics(match.get_statistics(), match.teams, match.colors))

with team2:
    st.pyplot(visuals.display_events(match.get_events()[1], match.cmap[1]))
    st.pyplot(visuals.display_passing_network(match.get_passing_network()[0][1], match.get_passing_network()[1][1], match.teams[1], match.colors[1]))
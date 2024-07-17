import streamlit as st
import pandas as pd

from simulator import visuals
from simulator import xG

st.set_page_config(
    page_title="xG simulator",
    page_icon=":soccer:",
    layout="wide"
)

st.title("xG simulator")

st.markdown(
    """
    Faudra écrire un peu de markdown pour présenter ce qui est dispo sur cette page 
    """
)

with st.expander("#### Change players positions"):
    st.markdown("##### Shooter position")
    col1, col2, col3 = st.columns(3)
    with col1:
        shoter_x = st.number_input("Shooter X position :", min_value=52.5, max_value=105., value=89., step=0.1, format="%.1f")
    with col2:
        shoter_y = st.number_input("Shooter Y position :", min_value=0., max_value=68., value=34., step=0.1, format="%.1f")
    with col3:
        shoter_contact = st.selectbox("Body part shoot", options=["Foot", "Head"])

    # Ligne pour la position du goal keeper
    st.markdown("##### Goalkeeper position")
    col4, col5 = st.columns(2)
    with col4:
        goal_keeper_x = st.number_input("Goalkeeper X position :", min_value=52.5, max_value=105., value=102., step=0.1, format="%.1f")
    with col5:
        goal_keeper_y = st.number_input("Goalkeeper Y position :", min_value=0., max_value=68., value=34., step=0.1, format="%.1f")

    # Afficher les champs pour la position des joueurs adverses en fonction du nombre spécifié
    st.markdown("##### Defender")
    opponent_number = st.number_input("Defender number:", min_value=0, value=0, step=1)

    opponents = []

    for i in range(opponent_number):
        col_a, col_b = st.columns(2)
        with col_a:
            opponent_x = st.number_input(f"Defender {i + 1} X position :", min_value=52.5, max_value=105., 
                                         value=95., step=0.1, format="%.1f", key=f"opponent_x_{i}")
        with col_b:
            opponent_y = st.number_input(f"Defender {i + 1} Y position :", min_value=0., max_value=68., 
                                         value=34., step=0.1, key=f"opponent_y_{i}")
        if len(opponents) <= i:
            opponents.append((opponent_x, opponent_y))
        else:
            opponents[i] = (opponent_x, opponent_y)

# Shot dataframe Creation
data_shot = [[shoter_x,shoter_y,shoter_contact]]
cols_shot = ['x','y','body_part_name']

shot_df = pd.DataFrame(data = data_shot, columns = cols_shot)

# Track dataframe Creation
data_track = [[goal_keeper_x,goal_keeper_y,'Goalkeeper']]
for i, (opponent_x, opponent_y) in enumerate(opponents):
    data_track.append([opponent_x, opponent_y, 'Defender'])

cols_track = ['x','y','position_name']
track_df = pd.DataFrame(data = data_track, columns = cols_track)

# Simulator
model_vars = xG.get_model_vars(shot_df, track_df)

X = model_vars[["x0", "is_closer", "angle", "distance", "gk_distance", 
                "gk_distance_y", "triangle", "close_players", "header"
                ]].values

prediction = xG.prediction(X)

#visual 
st.divider()

pitch, variable = st.columns([0.6, 0.3])
with pitch:
    st.html("<h3><center>Pitch position</center></h3>")
    st.pyplot(visuals.display_state(shot_df, track_df))
with variable:
    st.html("<h3><center>Variables</center></h3>")
    st.markdown(
        f"""
        ### Distance from the goal : {round(model_vars.distance.values[0], 2)}
        ### Angle from the goal : {round(model_vars.angle.values[0], 2)}
        ### Number of players closer than 3 metres : {model_vars.close_players.values[0]}
        ### Number of players in the triangle : {model_vars.triangle.values[0]}
        ### Shoot from the head : {bool(model_vars.header.values[0])}
        """
                )
    st.divider()
    st.html(f"<h2><center>Expected Goal : {round(prediction, 3)}</center></h2>")
    #st.dataframe(model_vars.T)

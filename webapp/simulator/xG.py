import numpy as np
import pandas as pd
import tensorflow as tf
import joblib

scaler = joblib.load('../../models/xG_scaler.pkl')
model = tf.keras.models.load_model("../../models/xG_predictor.keras")

def dist_to_gk(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> float:
    """
    Distance between ball and goalkeeper

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        float: euclidean distance
    """
    gk_pos = track.loc[track["position_name"] == "Goalkeeper"][["x", "y"]]
    dist = np.sqrt((shot["x"].values[0] - gk_pos["x"])**2 + (shot["y"].values[0] - gk_pos["y"])**2)

    return dist.iloc[0]

def y_to_gk(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> float:
    """
    Distance between ball and goalkeeper on y axis

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        float: distance on y axis
    """
    gk_pos = track.loc[track["position_name"] == "Goalkeeper"][["x", "y"]]
    dist = abs(shot["y"].values[0] - gk_pos["y"])

    return dist.iloc[0]

#number of players less than 3 meters away from the ball
def three_meters_away(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> int:
    """
    Number of players less than 3 meters away from the ball

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        int: number of players
    """
    player_position = track[["x", "y"]]
    dist = np.sqrt((shot["x"].values[0] - player_position["x"])**2 + (shot["y"].values[0] - player_position["y"])**2)

    return len(dist[dist<3])

def players_in_triangle(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> int:
    """
    Number of players inside a triangle

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        int: number of players
    """
    player_position = track[["x", "y"]]
    x1 = 105
    y1 = 34 - 7.32/2
    x2 = 105
    y2 = 34 + 7.32/2
    x3 = shot["x"].values[0]
    y3 = shot["y"].values[0]
    xp = player_position["x"]
    yp = player_position["y"]
    c1 = (x2-x1)*(yp-y1)-(y2-y1)*(xp-x1)
    c2 = (x3-x2)*(yp-y2)-(y3-y2)*(xp-x2)
    c3 = (x1-x3)*(yp-y3)-(y1-y3)*(xp-x3)

    return len(player_position.loc[((c1<0) & (c2<0) & (c3<0)) | ((c1>0) & (c2>0) & (c3>0))])

def gk_dist_to_goal(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> float:
    """
    Distance between goalkeeper and goal 

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        float: euclidean distance
    """
    gk_pos = track.loc[track["position_name"] == "Goalkeeper"][["x", "y"]]
    dist = np.sqrt((105 -gk_pos["x"])**2 + (34 - gk_pos["y"])**2)

    return dist.iloc[0]

def get_model_vars(shot: pd.core.frame.DataFrame, track: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """
    Variable calculation

    Args:
        shot (pd.core.frame.DataFrame): shot informations
        track (pd.core.frame.DataFrame): opponent informations

    Returns:
        tuple: variables in dataframe, variables values
    """
    #simple calculation 
    model_vars = shot[["x", "y"]]
    model_vars['x0'] = model_vars.x
    model_vars["x"] = model_vars.x.apply(lambda cell: 105-cell)
    model_vars["c"] = model_vars.y.apply(lambda cell: abs(34-cell))
    model_vars["angle"] = np.where(np.arctan(7.32 * model_vars["x"] / (model_vars["x"]**2 + model_vars["c"]**2 - (7.32/2)**2)) >= 0,
                                   np.arctan(7.32 * model_vars["x"] /(model_vars["x"]**2 + model_vars["c"]**2 - (7.32/2)**2)), 
                                   np.arctan(7.32 * model_vars["x"] /(model_vars["x"]**2 + model_vars["c"]**2 - (7.32/2)**2)) + np.pi
                                   )*180/np.pi
    model_vars["distance"] = np.sqrt(model_vars["x"]**2 + model_vars["c"]**2)

    ##fonctions 
    model_vars["gk_distance"] = dist_to_gk(shot, track)
    model_vars["gk_distance_y"] = y_to_gk(shot, track)
    model_vars["close_players"] = three_meters_away(shot, track)
    model_vars["triangle"] = players_in_triangle(shot, track)
    model_vars["gk_dist_to_goal"] = gk_dist_to_goal(shot, track)

    #processed 
    model_vars["is_closer"] = np.where(model_vars["gk_dist_to_goal"] > model_vars["distance"], 1, 0)
    model_vars["header"] = shot.body_part_name.apply(lambda cell: 1 if cell == "Head" else 0)
    
    return model_vars

def prediction(X: np.ndarray) -> float:
    """
    xG prediction 

    Args:
        X (np.ndarray): Variables

    Returns:
        float: xG
    """
    X_predict = scaler.transform(X)
    prediction = model.predict(np.array(X_predict))

    return float(prediction[0][0])
import pandas as pd
import random
import math


def calculate_df(train_set):
    """Calculate frequency tables for each feature in the training set.

    Args:
        train_set (pd.DataFrame): Training dataset containing features and PlayGolf target

    Returns:
        tuple: A tuple containing:
            - list of tuples: Each tuple contains (feature_name, frequency_dataframe)
            - tuple: Count of (yes_cases, no_cases) in the target variable
    """
    dataframes = []

    playGolf_yes = train_set[train_set["PlayGolf"] == "Yes"]
    playGolf_no = train_set[train_set["PlayGolf"] == "No"]

    # Outlook
    outlook_df = pd.DataFrame(
        {
            "Outlook": ["Sunny", "Overcast", "Rainy"],
            "PlayGolf_Yes": [
                (playGolf_yes["Outlook"] == "Sunny").sum(),
                (playGolf_yes["Outlook"] == "Overcast").sum(),
                (playGolf_yes["Outlook"] == "Rainy").sum(),
            ],
            "PlayGolf_No": [
                (playGolf_no["Outlook"] == "Sunny").sum(),
                (playGolf_no["Outlook"] == "Overcast").sum(),
                (playGolf_no["Outlook"] == "Rainy").sum(),
            ],
        }
    )

    outlook_df["Total"] = outlook_df["PlayGolf_Yes"] + outlook_df["PlayGolf_No"]
    dataframes.append(("Outlook", outlook_df))

    # Temperature
    temperature_df = pd.DataFrame(
        {
            "Temperature": ["Hot", "Mild", "Cool"],
            "PlayGolf_Yes": [
                (playGolf_yes["Temperature"] == "Hot").sum(),
                (playGolf_yes["Temperature"] == "Mild").sum(),
                (playGolf_yes["Temperature"] == "Cool").sum(),
            ],
            "PlayGolf_No": [
                (playGolf_no["Temperature"] == "Hot").sum(),
                (playGolf_no["Temperature"] == "Mild").sum(),
                (playGolf_no["Temperature"] == "Cool").sum(),
            ],
        }
    )

    temperature_df["Total"] = temperature_df["PlayGolf_Yes"] + temperature_df["PlayGolf_No"]
    dataframes.append(("Temperature", temperature_df))

    # Humidity
    humidity_df = pd.DataFrame(
        {
            "Humidity": ["Normal", "High"],
            "PlayGolf_Yes": [
                (playGolf_yes["Humidity"] == "Normal").sum(),
                (playGolf_yes["Humidity"] == "High").sum(),
            ],
            "PlayGolf_No": [
                (playGolf_no["Humidity"] == "Normal").sum(),
                (playGolf_no["Humidity"] == "High").sum(),
            ],
        }
    )

    humidity_df["Total"] = humidity_df["PlayGolf_Yes"] + humidity_df["PlayGolf_No"]
    dataframes.append(("Humidity", humidity_df))

    # Windy
    windy_df = pd.DataFrame(
        {
            "Windy": ["True", "False"],
            "PlayGolf_Yes": [
                (playGolf_yes["Windy"] == "True").sum(),
                (playGolf_yes["Windy"] == "False").sum(),
            ],
            "PlayGolf_No": [
                (playGolf_no["Windy"] == "True").sum(),
                (playGolf_no["Windy"] == "False").sum(),
            ],
        }
    )

    windy_df["Total"] = windy_df["PlayGolf_Yes"] + windy_df["PlayGolf_No"]
    dataframes.append(("Windy", windy_df))

    return dataframes, (len(playGolf_yes), len(playGolf_no))


def calculate_points(df, yes=True):
    """Calculate log-likelihood ratios for feature values.

    Args:
        df (tuple): Tuple containing (feature_name, frequency_dataframe)
        yes (bool, optional): If True, calculate points for "Yes" class, else "No" class. Defaults to True.

    Returns:
        list: List of tuples containing (feature_value, log_likelihood_ratio)
    """
    variable, df = df
    p_yes = df["PlayGolf_Yes"].sum()
    p_no = df["PlayGolf_No"].sum()
    return_values = []
    for i in range(df.shape[0]):
        if yes:
            value = math.log(((df["PlayGolf_Yes"][i] + 1) / (df["PlayGolf_No"][i] + 1)) / ((p_yes + 1) / (p_no + 1)))
        else:
            value = math.log(((df["PlayGolf_No"][i] + 1) / (df["PlayGolf_Yes"][i] + 1)) / ((p_no + 1) / (p_yes + 1)))
        return_values.append((df[variable][i], value))
    return return_values


def generate_random(num_rows=20):
    """Generate random training data for the golf playing example.

    Args:
        num_rows (int, optional): Number of samples to generate. Defaults to 20.

    Returns:
        pd.DataFrame: Generated dataset with features and target variable
    """
    header = ["Outlook", "Temperature", "Humidity", "Windy", "PlayGolf"]
    rows = []
    for _ in range(num_rows):
        row_data = [
            random.choice(["Sunny", "Overcast", "Rainy"]),  # Outlook
            random.choice(["Hot", "Cool", "Mild"]),  # Temperature
            random.choice(["High", "Normal"]),  # Humidity
            random.choice(["True", "False"]),  # Windy
            random.choice(["Yes", "No"]),  # PlayGolf
        ]
        rows.append(row_data)

    return pd.DataFrame(rows, columns=header)

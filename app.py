from flask import Flask, render_template, request
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import math

app = Flask(__name__)

DATA_FILE = "tank_data.csv"
CONFIG_FILE = "tank_config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["timestamp", "tank_id", "inches"])

    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    df = df.dropna(subset=["timestamp", "tank_id", "inches"])
    return df

def filter_by_range(df, time_range):
    now = datetime.now()
    if time_range == "day":
        start = now - timedelta(days=1)
    elif time_range == "week":
        start = now - timedelta(days=7)
    elif time_range == "month":
        start = now - timedelta(days=30)
    elif time_range == "year":
        start = now - timedelta(days=365)
    else:
        return df
    return df[df["timestamp"] >= start]

def compute_gallons(inches, diameter_inches):
    radius = diameter_inches / 2
    volume_cubic_inches = math.pi * (radius ** 2) * inches
    gallons = volume_cubic_inches * 0.004329
    return round(gallons, 2)

@app.route("/")
def index():
    tank_id = request.args.get("tank", "Dry Creek")
    time_range = request.args.get("range", "day")

    df = load_data()
    config = load_config()

    if tank_id not in config:
        return f"Tank '{tank_id}' not in config file."

    diameter = config[tank_id]["diameter_inches"]
    df = df[df["tank_id"] == tank_id]
    df = filter_by_range(df, time_range)

    df["gallons"] = df["inches"].apply(lambda x: compute_gallons(x, diameter))
    data = {
        "timestamps": df["timestamp"].astype(str).tolist(),
        "inches": df["inches"].tolist(),
        "gallons": df["gallons"].tolist()
    }

    tank_list = sorted(config.keys())
    return render_template("index.html", tank_id=tank_id, tank_list=tank_list, data=data, range=time_range)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# ==========================
# Car Price Prediction System
# Step 3: Flask Backend (app.py)
# ==========================

from flask import Flask, render_template, request
import pandas as pd
import pickle
from datetime import datetime

# ==========================
# Create Flask App
# ==========================

app = Flask(__name__)

# ==========================
# Load Trained Model
# ==========================

with open("car_price_model.pkl", "rb") as file:
    model = pickle.load(file)

# ==========================
# Load Label Encoders
# ==========================

with open("label_encoders.pkl", "rb") as file:
    label_encoders = pickle.load(file)

# ==========================
# Home Route
# ==========================

@app.route("/")
def home():

    return render_template(
        "index.html",
        brands=sorted(label_encoders["Brand"].classes_),
        locations=sorted(label_encoders["Location"].classes_),
        fuel_types=sorted(label_encoders["Fuel_Type"].classes_),
        transmissions=sorted(label_encoders["Transmission"].classes_),
        owner_types=sorted(label_encoders["Owner_Type"].classes_)
    )

# ==========================
# Prediction Route
# ==========================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # --------------------------
        # Read User Inputs
        # --------------------------

        location = request.form["location"]
        brand = request.form["brand"]
        fuel = request.form["fuel"]
        transmission = request.form["transmission"]
        owner = request.form["owner"]

        year = int(request.form["year"])
        kms = float(request.form["kms"])
        mileage = float(request.form["mileage"])
        engine = float(request.form["engine"])
        power = float(request.form["power"])
        seats = float(request.form["seats"])

        # --------------------------
        # Feature Engineering
        # --------------------------

        current_year = datetime.now().year
        car_age = current_year - year

        # --------------------------
        # Encode Categorical Values
        # --------------------------

        location = label_encoders["Location"].transform([location])[0]
        brand = label_encoders["Brand"].transform([brand])[0]
        fuel = label_encoders["Fuel_Type"].transform([fuel])[0]
        transmission = label_encoders["Transmission"].transform([transmission])[0]
        owner = label_encoders["Owner_Type"].transform([owner])[0]

        # --------------------------
        # Prepare Input Data
        # --------------------------

        input_data = pd.DataFrame([{
            "Location": location,
            "Year": year,
            "Kilometers_Driven": kms,
            "Fuel_Type": fuel,
            "Transmission": transmission,
            "Owner_Type": owner,
            "Mileage": mileage,
            "Engine": engine,
            "Power": power,
            "Seats": seats,
            "Brand": brand,
            "Car_Age": car_age
        }])

        # --------------------------
        # Predict Price
        # --------------------------

        prediction = model.predict(input_data)[0]
        prediction = round(prediction, 2)

        return render_template(
            "index.html",
            prediction=prediction,
            brands=sorted(label_encoders["Brand"].classes_),
            locations=sorted(label_encoders["Location"].classes_),
            fuel_types=sorted(label_encoders["Fuel_Type"].classes_),
            transmissions=sorted(label_encoders["Transmission"].classes_),
            owner_types=sorted(label_encoders["Owner_Type"].classes_)
        )

    except Exception as e:

        return render_template(
            "index.html",
            error=str(e),
            brands=sorted(label_encoders["Brand"].classes_),
            locations=sorted(label_encoders["Location"].classes_),
            fuel_types=sorted(label_encoders["Fuel_Type"].classes_),
            transmissions=sorted(label_encoders["Transmission"].classes_),
            owner_types=sorted(label_encoders["Owner_Type"].classes_)
        )

# ==========================
# Run Flask App
# ==========================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

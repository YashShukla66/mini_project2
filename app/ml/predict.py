import pandas as pd
import joblib
import os

# 🔥 DEFINE BASE PATH FIRST (IMPORTANT)
base_path = os.path.dirname(__file__)

# LOAD MODEL + ENCODERS
model = joblib.load(os.path.join(base_path, "model.pkl"))

le_gender = joblib.load(os.path.join(base_path, "le_gender.pkl"))
le_race = joblib.load(os.path.join(base_path, "le_race.pkl"))
le_parent = joblib.load(os.path.join(base_path, "le_parent.pkl"))
le_lunch = joblib.load(os.path.join(base_path, "le_lunch.pkl"))
le_prep = joblib.load(os.path.join(base_path, "le_prep.pkl"))
le_perf = joblib.load(os.path.join(base_path, "le_perf.pkl"))


def predict_performance(
    gender,
    race,
    parental_education,
    lunch,
    test_prep,
    math_score,
    coding_score,
    iot_score
):

    # 🔥 ENCODE INPUT
    gender = le_gender.transform([gender])[0]
    race = le_race.transform([race])[0]
    parental_education = le_parent.transform([parental_education])[0]
    lunch = le_lunch.transform([lunch])[0]
    test_prep = le_prep.transform([test_prep])[0]

    # CREATE DATAFRAME
    data = pd.DataFrame([[
        gender,
        race,
        parental_education,
        lunch,
        test_prep,
        math_score,
        coding_score,
        iot_score
    ]], columns=[
        "gender",
        "race",
        "parental_education",
        "lunch",
        "test_prep",
        "math_score",
        "coding_score",
        "iot_score"
    ])

    # PREDICT
    prediction = model.predict(data)

    # 🔥 DECODE OUTPUT
    result = le_perf.inverse_transform(prediction)

    return result[0]
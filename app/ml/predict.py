import pandas as pd
import joblib
import os

# 🔥 DEFINE BASE PATH FIRST (IMPORTANT)
base_path = os.path.dirname(__file__)

# LOAD MODEL + ENCODERS
model = joblib.load(os.path.join(base_path, "new_model.pkl"))

le_gender = joblib.load(os.path.join(base_path, "new_le_gender.pkl"))
le_med = joblib.load(os.path.join(base_path, "new_le_med.pkl"))
le_drug = joblib.load(os.path.join(base_path, "new_le_drug.pkl"))
le_perf = joblib.load(os.path.join(base_path, "new_le_perf.pkl"))

def predict_performance(
    gender,
    sleep_hours,
    doom_scrolling_time,
    productive_screen_time,
    study_hours,
    medical_issue,
    drug_addiction,
    math_score,
    physics_score,
    chemistry_score,
    biology_score,
    english_score
):

    # 🔥 ENCODE INPUT
    gender_encoded = le_gender.transform([gender])[0]
    med_encoded = le_med.transform([medical_issue])[0]
    drug_encoded = le_drug.transform([drug_addiction])[0]

    # CREATE DATAFRAME
    data = pd.DataFrame([[
        gender_encoded,
        sleep_hours,
        doom_scrolling_time,
        productive_screen_time,
        study_hours,
        med_encoded,
        drug_encoded,
        math_score,
        physics_score,
        chemistry_score,
        biology_score,
        english_score
    ]], columns=[
        "gender",
        "sleep_hours",
        "doom_scrolling_time",
        "productive_screen_time",
        "study_hours",
        "medical_issue",
        "drug_addiction",
        "math_score",
        "physics_score",
        "chemistry_score",
        "biology_score",
        "english_score"
    ])

    # PREDICT
    prediction = model.predict(data)

    # 🔥 DECODE OUTPUT
    result = le_perf.inverse_transform(prediction)

    return result[0]
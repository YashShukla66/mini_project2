import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier


print("Loading dataset...")

df = pd.read_csv("data/students.csv")


# rename dataset columns correctly
df = df.rename(columns={
    "race/ethnicity": "race",
    "parental_level_of_education": "parental_education",
    "test_preparation_course": "test_prep"
})


print("Encoding categorical columns...")

le_gender = LabelEncoder()
le_race = LabelEncoder()
le_parent = LabelEncoder()
le_lunch = LabelEncoder()
le_prep = LabelEncoder()


df["gender"] = le_gender.fit_transform(df["gender"])
df["race"] = le_race.fit_transform(df["race"])
df["parental_education"] = le_parent.fit_transform(df["parental_education"])
df["lunch"] = le_lunch.fit_transform(df["lunch"])
df["test_prep"] = le_prep.fit_transform(df["test_prep"])


# create performance label
df["average"] = (df["math_score"] + df["coding_score"] + df["iot_score"]) / 3


def get_performance(avg):
    if avg < 40:
        return "poor"
    elif avg < 60:
        return "average"
    elif avg < 80:
        return "good"
    else:
        return "excellent"


df["performance"] = df["average"].apply(get_performance)


le_perf = LabelEncoder()
df["performance"] = le_perf.fit_transform(df["performance"])


X = df[[
    "gender",
    "race",
    "parental_education",
    "lunch",
    "test_prep",
    "math_score",
    "coding_score",
    "iot_score"
]]

y = df["performance"]


print("Splitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("Training model...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)


accuracy = model.score(X_test, y_test)

print("Model accuracy:", accuracy)


print("Saving model and encoders...")

# 🔥 SAVE EVERYTHING (IMPORTANT)
joblib.dump(model, "app/ml/model.pkl")

joblib.dump(le_gender, "app/ml/le_gender.pkl")
joblib.dump(le_race, "app/ml/le_race.pkl")
joblib.dump(le_parent, "app/ml/le_parent.pkl")
joblib.dump(le_lunch, "app/ml/le_lunch.pkl")
joblib.dump(le_prep, "app/ml/le_prep.pkl")
joblib.dump(le_perf, "app/ml/le_perf.pkl")

print("Model and encoders saved successfully!")
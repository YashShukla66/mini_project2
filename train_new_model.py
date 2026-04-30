import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Set seed for reproducibility
np.random.seed(42)

# Generate synthetic dataset
n_samples = 5000

# Existing Features
genders = np.random.choice(['male', 'female'], n_samples)
sleep_hours = np.random.normal(7, 1.5, n_samples).clip(2, 12).round(1)

# New Features
doom_scrolling_time = np.random.normal(3, 2, n_samples).clip(0, 10).round(1)
productive_screen_time = np.random.normal(4, 2, n_samples).clip(0, 12).round(1)
study_hours = np.random.normal(3, 2, n_samples).clip(0, 10).round(1)
medical_issue = np.random.choice(['yes', 'no'], n_samples, p=[0.05, 0.95])
drug_addiction = np.random.choice(['yes', 'no'], n_samples, p=[0.02, 0.98])

# Base scores - use uniform to ensure all performance buckets are well-represented
math_scores = np.random.uniform(0, 100, n_samples).astype(int)
physics_scores = np.random.uniform(0, 100, n_samples).astype(int)
chemistry_scores = np.random.uniform(0, 100, n_samples).astype(int)
biology_scores = np.random.uniform(0, 100, n_samples).astype(int)
english_scores = np.random.uniform(0, 100, n_samples).astype(int)

# Correlation Impacts
bonus = (study_hours * 3) + (productive_screen_time * 1.5)
penalty = (doom_scrolling_time * 2.5) 
penalty += np.where(sleep_hours < 5, (5 - sleep_hours) * 4, 0)
penalty += np.where(medical_issue == 'yes', 15, 0)
penalty += np.where(drug_addiction == 'yes', 25, 0)

net_effect = bonus - penalty

math_scores = (math_scores + net_effect).clip(0, 100).astype(int)
physics_scores = (physics_scores + net_effect).clip(0, 100).astype(int)
chemistry_scores = (chemistry_scores + net_effect).clip(0, 100).astype(int)
biology_scores = (biology_scores + net_effect).clip(0, 100).astype(int)
english_scores = (english_scores + net_effect).clip(0, 100).astype(int)

# Determine Performance based on avg score
avg_score = (math_scores + physics_scores + chemistry_scores + biology_scores + english_scores) / 5

def get_performance(score):
    if score >= 91:
        return "Excellent"
    elif score >= 81:
        return "Good"
    elif score >= 71:
        return "Nice"
    elif score >= 50:
        return "Decent"
    elif score >= 33:
        return "Just Pass"
    else:
        return "Worst"

performances = np.array([get_performance(score) for score in avg_score])

# Create DataFrame
df = pd.DataFrame({
    'gender': genders,
    'sleep_hours': sleep_hours,
    'doom_scrolling_time': doom_scrolling_time,
    'productive_screen_time': productive_screen_time,
    'study_hours': study_hours,
    'medical_issue': medical_issue,
    'drug_addiction': drug_addiction,
    'math_score': math_scores,
    'physics_score': physics_scores,
    'chemistry_score': chemistry_scores,
    'biology_score': biology_scores,
    'english_score': english_scores,
    'performance': performances
})

os.makedirs('data', exist_ok=True)
df.to_csv('data/new_students.csv', index=False)
print("Dataset generated and saved to data/new_students.csv")

# Encoders
le_gender = LabelEncoder()
df['gender'] = le_gender.fit_transform(df['gender'])

le_med = LabelEncoder()
df['medical_issue'] = le_med.fit_transform(df['medical_issue'])

le_drug = LabelEncoder()
df['drug_addiction'] = le_drug.fit_transform(df['drug_addiction'])

le_perf = LabelEncoder()
df['performance'] = le_perf.fit_transform(df['performance'])

# Train Model
X = df.drop('performance', axis=1)
y = df['performance']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
accuracy = accuracy_score(y_test, preds)
print(f"Model trained with accuracy: {accuracy * 100:.2f}%")

app_ml_dir = 'app/ml'
os.makedirs(app_ml_dir, exist_ok=True)

joblib.dump(model, f'{app_ml_dir}/new_model.pkl')
joblib.dump(le_gender, f'{app_ml_dir}/new_le_gender.pkl')
joblib.dump(le_med, f'{app_ml_dir}/new_le_med.pkl')
joblib.dump(le_drug, f'{app_ml_dir}/new_le_drug.pkl')
joblib.dump(le_perf, f'{app_ml_dir}/new_le_perf.pkl')

print("Model and encoders saved in app/ml")

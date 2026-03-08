import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

data = pd.read_csv("students.csv")

data["average"] = (data["math_score"] + data["coding_score"] + data["iot_score"]) / 3

data["result"] = data["average"].apply(lambda x: "Pass" if x >= 50 else "Fail")

X = data[["math_score","coding_score","iot_score"]]
y = data["result"]

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train,y_train)

def predict_student(math,coding,iot):

    prediction = model.predict([[math,coding,iot]])

    return prediction[0]
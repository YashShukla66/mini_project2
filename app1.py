from flask import Flask, render_template, request, redirect, url_for
from model import predict_student

app = Flask(__name__)

# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# STUDENT DETAILS PAGE
@app.route("/details", methods=["GET","POST"])
def index():

    if request.method=="POST":

        name=request.form["name"]
        rollno=request.form["rollno"]
        course=request.form["course"]

        return redirect(url_for("prediction",name=name,rollno=rollno,course=course))

    return render_template("index.html")


# PREDICTION PAGE
@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    name = request.args.get("name")
    rollno = request.args.get("rollno")
    course = request.args.get("course")

    result = None

    if request.method == "POST":

        math = int(request.form.get("math"))
        coding = int(request.form.get("coding"))
        iot = int(request.form.get("iot"))

        prediction = predict_student(math, coding, iot)

        if prediction == "Fail":
            result = "You Need Improvement"
        else:
            result = "Good Performance"

    return render_template(
        "prediction.html",
        name=name,
        rollno=rollno,
        course=course,
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)
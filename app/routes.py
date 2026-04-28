from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from app.models import Prediction, User
from app import db, oauth
from app.ml.predict import predict_performance 
import secrets

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("landing.html")

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@main.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    if request.method == "POST":
        gender = request.form.get("gender")
        race = request.form.get("race")
        parental_education = request.form.get("parental_education")
        lunch = request.form.get("lunch")
        test_prep = request.form.get("test_prep")
        math_score = request.form.get("math_score")
        coding_score = request.form.get("coding_score")
        iot_score = request.form.get("iot_score")

        if not math_score or not coding_score or not iot_score:
            return "All scores are required"

        math_score = int(math_score)
        coding_score = int(coding_score)
        iot_score = int(iot_score)

        result = predict_performance(
            gender, race, parental_education, lunch, test_prep, 
            math_score, coding_score, iot_score
        )

        new_prediction = Prediction(
            user_id=current_user.id,
            gender=gender,
            race=race,
            parental_education=parental_education,
            lunch=lunch,
            test_prep=test_prep,
            math_score=math_score,
            coding_score=coding_score,
            iot_score=iot_score,
            result=result
        )
        db.session.add(new_prediction)
        db.session.commit()
        
        return render_template("result.html", result=result)
        
    return render_template("prediction.html")

# --- GOOGLE OAUTH ROUTES ---

@main.route("/login/google")
def google_login():
    """Redirects the user to the Google login page"""
    redirect_uri = url_for("main.google_authorize", _external=True)
    print(f"[GOOGLE OAUTH] Redirect URI being sent: {redirect_uri}", flush=True)
    return oauth.google.authorize_redirect(redirect_uri)

@main.route("/login/google/authorize")
def google_authorize():
    """Handles the callback from Google and logs the user in"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash("Error logging in with Google. Please try again.", "error")
            return redirect(url_for("auth.login"))

        # Check if the user already exists
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            # Create a new user with a dummy password since they authenticate via Google
            dummy_password = secrets.token_hex(16)
            user = User(
                username=user_info['name'], 
                email=user_info['email'], 
                password=dummy_password 
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        print(f"[GOOGLE OAUTH ERROR] {e}")
        flash("Google login failed. Please check your OAuth configuration.", "error")
        return redirect(url_for("auth.login"))
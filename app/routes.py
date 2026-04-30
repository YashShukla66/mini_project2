from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from app.models import Prediction, User
from app import db, oauth
from app.ml.predict import predict_performance 
import secrets
import os
from dotenv import load_dotenv
from google import genai
import markdown

# Load .env file so GEMINI_API_KEY is available
load_dotenv()

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
        sleep_hours = request.form.get("sleep_hours")
        doom_scrolling_time = request.form.get("doom_scrolling_time")
        productive_screen_time = request.form.get("productive_screen_time")
        study_hours = request.form.get("study_hours")
        medical_issue = request.form.get("medical_issue")
        drug_addiction = request.form.get("drug_addiction")
        math_score = request.form.get("math_score")
        physics_score = request.form.get("physics_score")
        chemistry_score = request.form.get("chemistry_score")
        biology_score = request.form.get("biology_score")
        english_score = request.form.get("english_score")

        if not all([sleep_hours, doom_scrolling_time, productive_screen_time, study_hours, math_score, physics_score, chemistry_score, biology_score, english_score]):
            return "All scores and time entries are required"

        sleep_hours = float(sleep_hours)
        doom_scrolling_time = float(doom_scrolling_time)
        productive_screen_time = float(productive_screen_time)
        study_hours = float(study_hours)
        math_score = int(math_score)
        physics_score = int(physics_score)
        chemistry_score = int(chemistry_score)
        biology_score = int(biology_score)
        english_score = int(english_score)

        result = predict_performance(
            gender, sleep_hours, doom_scrolling_time, productive_screen_time,
            study_hours, medical_issue, drug_addiction,
            math_score, physics_score, chemistry_score, biology_score, english_score
        )

        percentage = round((math_score + physics_score + chemistry_score + biology_score + english_score) / 5, 1)

        # Enforce exact label match based on user's strict percentage boundaries
        if percentage < 33:
            result = "Worst"
        elif percentage < 50:
            result = "Just Pass"
        elif percentage < 71:
            result = "Decent"
        elif percentage < 81:
            result = "Nice"
        elif percentage < 91:
            result = "Good"
        else:
            result = "Excellent"

        new_prediction = Prediction(
            user_id=current_user.id,
            gender=gender,
            sleep_hours=sleep_hours,
            doom_scrolling_time=doom_scrolling_time,
            productive_screen_time=productive_screen_time,
            study_hours=study_hours,
            medical_issue=medical_issue,
            drug_addiction=drug_addiction,
            math_score=math_score,
            physics_score=physics_score,
            chemistry_score=chemistry_score,
            biology_score=biology_score,
            english_score=english_score,
            result=result
        )
        db.session.add(new_prediction)
        db.session.commit()
        
        # --- GEMINI FEEDBACK GENERATION ---
        feedback_html = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                import time
                client = genai.Client(api_key=api_key)
                prompt = f"""You are an expert student counselor and AI tutor. A student just received a performance prediction.
Here are their stats:
- Overall Percentage: {percentage}%
- Predicted Category: {result}
- Study Hours per day: {study_hours}
- Sleep Hours per day: {sleep_hours}
- Doom Scrolling Time per day: {doom_scrolling_time} hours
- Productive Screen Time per day: {productive_screen_time} hours
- Medical Issues: {medical_issue}
- Drug Addiction: {drug_addiction}
- Math Score: {math_score}
- Physics Score: {physics_score}
- Chemistry Score: {chemistry_score}
- Biology Score: {biology_score}
- English Score: {english_score}

Please provide:
1. The mistakes the student is currently making based on this data.
2. Practical, actionable ways to improve.
3. A special bonus tip for their specific situation.

Keep the tone encouraging, empathetic, but direct about their habits. Use Markdown formatting."""

                # Try multiple models - each has its own separate quota
                models_to_try = ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-2.5-flash']
                response = None
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if response and response.text:
                            print(f"[GEMINI SUCCESS] Used model: {model_name}", flush=True)
                            break
                    except Exception as model_err:
                        print(f"[GEMINI] {model_name} failed: {model_err}", flush=True)
                        time.sleep(2)
                        continue
                
                if response and response.text:
                    feedback_html = markdown.markdown(response.text)
                else:
                    feedback_html = "<p><em>AI models are currently overloaded. Please try again in a minute.</em></p>"
            except Exception as e:
                print(f"[GEMINI API ERROR] {e}", flush=True)
                feedback_html = "<p><em>AI Feedback could not be generated at this time. Please try again shortly.</em></p>"
        else:
            feedback_html = "<p><em>Configure the <code>GEMINI_API_KEY</code> in the .env file to enable AI-powered feedback.</em></p>"

        return render_template("result.html", result=result, percentage=percentage, feedback_html=feedback_html)
        
    return render_template("prediction.html")

import datetime

@main.before_request
def update_streak():
    if current_user.is_authenticated:
        today = datetime.date.today()
        if current_user.last_login_date != today:
            if current_user.last_login_date == today - datetime.timedelta(days=1):
                # Logged in yesterday
                current_user.streak = (current_user.streak or 0) + 1
            else:
                # Streak broken or first login
                current_user.streak = 1
            current_user.last_login_date = today
            db.session.commit()

@main.route("/analytics")
@login_required
def analytics():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    
    # Calculate some basic metrics
    total_predictions = len(predictions)
    excellent_count = sum(1 for p in predictions if p.result == "Excellent")
    good_count = sum(1 for p in predictions if p.result == "Good")
    nice_count = sum(1 for p in predictions if p.result == "Nice")
    decent_count = sum(1 for p in predictions if p.result == "Decent")
    pass_count = sum(1 for p in predictions if p.result == "Just Pass")
    worst_count = sum(1 for p in predictions if p.result == "Worst")
    
    avg_sleep = round(sum(p.sleep_hours for p in predictions) / total_predictions, 1) if total_predictions else 0
    avg_study = round(sum(p.study_hours for p in predictions) / total_predictions, 1) if total_predictions else 0
    
    # Group by date for daily progress
    daily_progress = {}
    for p in predictions:
        date_str = p.created_at.strftime('%Y-%m-%d')
        if date_str not in daily_progress:
            daily_progress[date_str] = []
        daily_progress[date_str].append(p)

    return render_template(
        "analytics.html", 
        predictions=predictions,
        total_predictions=total_predictions,
        excellent_count=excellent_count,
        good_count=good_count,
        nice_count=nice_count,
        decent_count=decent_count,
        pass_count=pass_count,
        worst_count=worst_count,
        avg_sleep=avg_sleep,
        avg_study=avg_study,
        daily_progress=daily_progress,
        streak=current_user.streak
    )

@main.route("/history")
@login_required
def history():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return render_template("history.html", predictions=predictions)

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
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from .models import User
from . import db

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

auth = Blueprint("auth", __name__)


def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp_code):
    """Send OTP to the user's email using SMTP.
    If email creds are not configured, returns the OTP so it can be shown on screen (dev mode).
    """
    sender_email = current_app.config.get("MAIL_USERNAME")
    sender_password = current_app.config.get("MAIL_PASSWORD")
    smtp_server = current_app.config.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = current_app.config.get("MAIL_PORT", 587)

    # If email credentials are not configured, return False (dev mode)
    if not sender_email or not sender_password:
        print(f"[DEV MODE] OTP for {recipient_email}: {otp_code}")
        return False  # Signal that email was NOT sent

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your OTP - AI Student Analytics"
        msg["From"] = sender_email
        msg["To"] = recipient_email

        html_body = f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background: #0a0e1a; padding: 40px;">
            <div style="max-width: 480px; margin: 0 auto; background: #111827; border-radius: 16px; padding: 40px; border: 1px solid rgba(255,255,255,0.06);">
                <h2 style="color: #f1f5f9; text-align: center; margin-bottom: 8px;">Verify Your Email</h2>
                <p style="color: #94a3b8; text-align: center; margin-bottom: 32px;">Enter this code to complete your verification</p>
                <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
                    <span style="font-size: 36px; font-weight: 800; color: white; letter-spacing: 12px;">{otp_code}</span>
                </div>
                <p style="color: #64748b; font-size: 13px; text-align: center;">This code expires in 10 minutes. Do not share it with anyone.</p>
                <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 24px 0;">
                <p style="color: #64748b; font-size: 12px; text-align: center;">AI Student Analytics &mdash; Predict. Analyze. Succeed.</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        return True  # Email sent successfully

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send OTP: {e}")
        print(f"[DEV MODE] OTP for {recipient_email}: {otp_code}")
        return False  # Email failed, use dev mode


# ==================== LOGIN ====================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with this email. Please sign up first.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Invalid password. Please try again.", "error")
            return redirect(url_for("auth.login"))

        # Generate and send OTP for login verification
        otp = generate_otp()
        session["login_otp"] = otp
        session["login_email"] = email
        session["otp_purpose"] = "login"

        email_sent = send_otp_email(email, otp)

        if email_sent:
            flash("OTP sent to your email. Please verify.", "info")
        else:
            # Dev mode: show OTP on the verification page
            session["dev_otp_display"] = otp
            flash("Dev Mode: OTP is shown below (email not configured).", "info")

        return redirect(url_for("auth.verify_otp"))

    return render_template("login.html")


# ==================== REGISTER ====================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login instead.", "error")
            return redirect(url_for("auth.login"))

        # Store registration data in session and send OTP
        otp = generate_otp()
        session["register_otp"] = otp
        session["register_username"] = username
        session["register_email"] = email
        session["register_password"] = password
        session["otp_purpose"] = "register"

        email_sent = send_otp_email(email, otp)

        if email_sent:
            flash("OTP sent to your email. Please verify to complete registration.", "info")
        else:
            # Dev mode: show OTP on the verification page
            session["dev_otp_display"] = otp
            flash("Dev Mode: OTP is shown below (email not configured).", "info")

        return redirect(url_for("auth.verify_otp"))

    return render_template("register.html")


# ==================== VERIFY OTP ====================

@auth.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    purpose = session.get("otp_purpose")

    if not purpose:
        flash("Session expired. Please try again.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()

        if purpose == "login":
            stored_otp = session.get("login_otp")
            email = session.get("login_email")

            if entered_otp == stored_otp:
                user = User.query.filter_by(email=email).first()
                if user:
                    login_user(user)
                    # Clear session OTP data
                    session.pop("login_otp", None)
                    session.pop("login_email", None)
                    session.pop("otp_purpose", None)
                    session.pop("dev_otp_display", None)
                    flash("Login successful! Welcome back.", "success")
                    return redirect(url_for("main.dashboard"))
            else:
                flash("Invalid OTP. Please try again.", "error")
                return redirect(url_for("auth.verify_otp"))

        elif purpose == "register":
            stored_otp = session.get("register_otp")

            if entered_otp == stored_otp:
                username = session.get("register_username")
                email = session.get("register_email")
                password = session.get("register_password")

                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

                new_user = User(
                    username=username,
                    email=email,
                    password=hashed_password,
                    is_admin=False
                )

                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)

                # Clear session data
                session.pop("register_otp", None)
                session.pop("register_username", None)
                session.pop("register_email", None)
                session.pop("register_password", None)
                session.pop("otp_purpose", None)
                session.pop("dev_otp_display", None)

                flash("Account created successfully! Welcome aboard.", "success")
                return redirect(url_for("main.dashboard"))
            else:
                flash("Invalid OTP. Please try again.", "error")
                return redirect(url_for("auth.verify_otp"))

    email_display = session.get("login_email") or session.get("register_email") or ""
    dev_otp = session.get("dev_otp_display")

    return render_template("verify_otp.html", email=email_display, purpose=purpose, dev_otp=dev_otp)


# ==================== RESEND OTP ====================

@auth.route("/resend-otp")
def resend_otp():
    purpose = session.get("otp_purpose")

    if purpose == "login":
        email = session.get("login_email")
        otp = generate_otp()
        session["login_otp"] = otp
        email_sent = send_otp_email(email, otp)
        if not email_sent:
            session["dev_otp_display"] = otp

    elif purpose == "register":
        email = session.get("register_email")
        otp = generate_otp()
        session["register_otp"] = otp
        email_sent = send_otp_email(email, otp)
        if not email_sent:
            session["dev_otp_display"] = otp

    else:
        flash("Session expired. Please try again.", "error")
        return redirect(url_for("auth.login"))

    flash("New OTP sent to your email.", "info")
    return redirect(url_for("auth.verify_otp"))


# ==================== LOGOUT ====================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("main.home"))
# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

import os
import json
import uuid
import sys
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.db import (
    init_db, get_user_by_email, get_user_by_id, create_user,
    save_prediction, get_user_predictions, get_prediction_by_id,
    delete_prediction, get_user_stats, get_all_stats
)
from utils.predictor import predict_image, model_status

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# ── Init DB & folders ──────────────────────────────────────────────────────────
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)
init_db()

# ── Auth decorator ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = get_all_stats()
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name      = request.form.get('name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif get_user_by_email(email):
            flash('An account with this email already exists.', 'error')
        else:
            hashed = generate_password_hash(password)
            if create_user(name, email, hashed):
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_user_by_id(session['user_id'])
    stats = get_user_stats(session['user_id'])
    recent_preds = get_user_predictions(session['user_id'])[:5]
    # Parse all_probs JSON for recent preds
    recent = []
    for p in recent_preds:
        d = dict(p)
        d['all_probs'] = json.loads(d['all_probs'])
        d['class_color'] = Config.CLASS_COLORS.get(d['predicted_class'], '#64748b')
        recent.append(d)
    return render_template('dashboard.html', user=user, stats=stats, recent_preds=recent,
                           class_colors=Config.CLASS_COLORS)

@app.route('/model_status')
def get_model_status():
    return jsonify(model_status())

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    # Eagerly load the model when predict page is opened
    from utils.predictor import get_model
    try:
        get_model()
    except Exception:
        pass

    # Check model availability on every request (GET and POST)
    status = model_status()

    if request.method == 'POST':
        if not status['torch']:
            flash('⚠️ PyTorch is not installed. Install it first — see the setup guide below.', 'error')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload PNG, JPG, BMP, or TIFF.', 'error')
            return redirect(request.url)

        # Save uploaded file
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"upload_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            result = predict_image(filepath)
            pred_id = save_prediction(
                user_id          = session['user_id'],
                image_filename   = filename,
                gradcam_filename = result['gradcam_filename'],
                predicted_class  = result['predicted_class'],
                confidence       = result['confidence'],
                all_probs_json   = json.dumps(result['all_probs'])
            )
            return redirect(url_for('result', pred_id=pred_id))
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('predict.html', model_status=status)

@app.route('/result/<int:pred_id>')
@login_required
def result(pred_id):
    pred = get_prediction_by_id(pred_id, session['user_id'])
    if not pred:
        flash('Prediction not found.', 'error')
        return redirect(url_for('history'))
    d = dict(pred)
    d['all_probs'] = json.loads(d['all_probs'])
    d['class_color'] = Config.CLASS_COLORS.get(d['predicted_class'], '#64748b')
    d['class_info']  = Config.CLASS_INFO.get(d['predicted_class'], {})
    return render_template('result.html', pred=d)

@app.route('/history')
@login_required
def history():
    preds = get_user_predictions(session['user_id'])
    history_list = []
    for p in preds:
        d = dict(p)
        d['all_probs']   = json.loads(d['all_probs'])
        d['class_color'] = Config.CLASS_COLORS.get(d['predicted_class'], '#64748b')
        history_list.append(d)
    return render_template('history.html', predictions=history_list)

@app.route('/delete_prediction/<int:pred_id>', methods=['POST'])
@login_required
def delete_pred(pred_id):
    pred = get_prediction_by_id(pred_id, session['user_id'])
    if pred:
        # Remove image files
        for fname_key in ['image_filename', 'gradcam_filename']:
            fname = pred[fname_key]
            if fname:
                folder = Config.UPLOAD_FOLDER if fname_key == 'image_filename' else Config.RESULTS_FOLDER
                fpath = os.path.join(folder, fname)
                if os.path.exists(fpath):
                    os.remove(fpath)
        delete_prediction(pred_id, session['user_id'])
        flash('Prediction deleted.', 'success')
    return redirect(url_for('history'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_user_stats(session['user_id'])
    return jsonify(stats)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("NeuroScan AI - Parkinson's Disease Dementia Detection System")
    print("=" * 50)
    print(f"   Model: {Config.MODEL_PATH}")
    print(f"   DB:    {Config.DATABASE_PATH}")
    print("   URL:   http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

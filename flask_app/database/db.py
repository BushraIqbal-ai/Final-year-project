# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

import sqlite3
import os
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'patient',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_filename TEXT NOT NULL,
            gradcam_filename TEXT,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            all_probs TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def create_user(name, email, password_hash):
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def save_prediction(user_id, image_filename, gradcam_filename, predicted_class, confidence, all_probs_json):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO predictions (user_id, image_filename, gradcam_filename, predicted_class, confidence, all_probs)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, image_filename, gradcam_filename, predicted_class, confidence, all_probs_json)
    )
    conn.commit()
    pred_id = cursor.lastrowid
    conn.close()
    return pred_id

def get_user_predictions(user_id):
    conn = get_db()
    preds = conn.execute(
        'SELECT * FROM predictions WHERE user_id = ? ORDER BY timestamp DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return preds

def get_prediction_by_id(pred_id, user_id):
    conn = get_db()
    pred = conn.execute(
        'SELECT * FROM predictions WHERE id = ? AND user_id = ?',
        (pred_id, user_id)
    ).fetchone()
    conn.close()
    return pred

def delete_prediction(pred_id, user_id):
    conn = get_db()
    conn.execute('DELETE FROM predictions WHERE id = ? AND user_id = ?', (pred_id, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM predictions WHERE user_id = ?', (user_id,)).fetchone()[0]
    class_dist = conn.execute(
        '''SELECT predicted_class, COUNT(*) as count 
           FROM predictions WHERE user_id = ? 
           GROUP BY predicted_class ORDER BY count DESC''',
        (user_id,)
    ).fetchall()
    avg_conf = conn.execute(
        'SELECT AVG(confidence) FROM predictions WHERE user_id = ?', (user_id,)
    ).fetchone()[0]
    conn.close()
    return {
        'total': total,
        'class_distribution': [dict(r) for r in class_dist],
        'avg_confidence': round((avg_conf or 0) * 100, 1)
    }

def get_all_stats():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_preds = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    class_dist = conn.execute(
        '''SELECT predicted_class, COUNT(*) as count 
           FROM predictions GROUP BY predicted_class ORDER BY count DESC'''
    ).fetchall()
    conn.close()
    return {
        'total_users': total_users,
        'total_predictions': total_preds,
        'class_distribution': [dict(r) for r in class_dist]
    }

# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'parkinsons-dementia-detection-secret-2024')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'app.db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'results')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'best_model.pt')

    CLASSES = {
        0: "Mild Demented",
        1: "Moderate Demented",
        2: "Non Demented",
        3: "Severe Demented",
        4: "Very Mild Demented"
    }

    CLASS_COLORS = {
        "Non Demented":       "#10b981",
        "Very Mild Demented": "#f59e0b",
        "Mild Demented":      "#f97316",
        "Moderate Demented":  "#ef4444",
        "Severe Demented":    "#7c3aed",
    }

    CLASS_INFO = {
        "Non Demented": {
            "icon": "✅",
            "description": "No signs of dementia detected. The brain scan appears normal with no significant cognitive decline indicators.",
            "recommendations": ["Maintain a healthy lifestyle", "Regular cognitive exercises", "Annual check-ups recommended"]
        },
        "Very Mild Demented": {
            "icon": "⚠️",
            "description": "Very mild cognitive impairment detected. Minor memory lapses may occur but daily activities remain unaffected.",
            "recommendations": ["Consult a neurologist", "Cognitive stimulation therapy", "Monitor progression every 6 months"]
        },
        "Mild Demented": {
            "icon": "🔶",
            "description": "Mild dementia detected. Noticeable memory problems and difficulty with complex tasks. Daily life may be slightly impacted.",
            "recommendations": ["Seek medical evaluation immediately", "Medication may be prescribed", "Caregiver support recommended"]
        },
        "Moderate Demented": {
            "icon": "🔴",
            "description": "Moderate dementia detected. Significant memory loss and confusion. Assistance with daily activities is needed.",
            "recommendations": ["Intensive medical treatment required", "Full-time caregiver support", "Consider specialized memory care"]
        },
        "Severe Demented": {
            "icon": "🚨",
            "description": "Severe dementia detected. Extensive cognitive decline with loss of ability to communicate and perform basic functions.",
            "recommendations": ["Immediate specialist consultation", "24/7 professional care required", "Palliative care planning"]
        }
    }

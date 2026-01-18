from flask import Blueprint, jsonify
import json
import os
import numpy as np
from ai.ml_logic import calculate_weakness_scores, calculate_dropout_risk, calculate_study_profile

mentor = Blueprint("mentor", __name__)

@mentor.route("/stats", methods=["GET"])
def get_mentor_stats():
    """
    Aggregates high-level intelligence for Parents/Mentors.
    """
    history_file = 'database/study_history.json'
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)

    # 1. Consistency Score (last 7 days)
    # Heuristic: (Days active / 7) * (Completion Rate)
    last_7 = history[-7:] if history else []
    days_active = len(set(d.get('date') for d in last_7 if d.get('date')))
    completion_rate = sum(1 for d in last_7 if d.get('completed')) / len(last_7) if last_7 else 0
    
    consistency_score = int((days_active / 7) * 100 * (0.5 + 0.5 * completion_rate))

    # 2. Effort Trend
    # Compare actual minutes against a "Standard Goal" (e.g. 90m/day)
    effort_trend = []
    for d in last_7:
        effort_trend.append({
            "date": d.get('date'),
            "actual": d.get('minutes', 0),
            "target": 90 # Heuristic target
        })

    # 3. ML Intelligence (Reusing existing models)
    # Streak is fetched from a session state in a real app, here we heuristic it
    # We'll assume streak is the count of consecutive active days till now
    streak = 0
    if history:
        # Simplified streak calculation
        dates = sorted(list(set(d.get('date') for d in history)))
        # (This is just a mock for the demo)
        streak = len(dates) 

    weaknesses = calculate_weakness_scores(history)
    dropout_risk = calculate_dropout_risk(history, streak)
    study_profile = calculate_study_profile(history)

    # 4. Proactive Parent Alerts
    alerts = []
    if dropout_risk == "High":
        alerts.append({
            "type": "danger",
            "message": "⚠️ High Burnout Risk detected. Decreasing engagement observed."
        })
    elif dropout_risk == "Medium":
        alerts.append({
            "type": "warning",
            "message": "⚡ Consistency is slipping. Consider a supportive check-in."
        })

    if consistency_score < 40:
        alerts.append({
            "type": "info",
            "message": "📅 Low activity this week. Encouragement might help."
        })

    # Find Top Weakness for the radar
    sorted_weakness = sorted(weaknesses.items(), key=lambda x: x[1], reverse=True)
    top_priority = sorted_weakness[0][0] if sorted_weakness else "All clear"

    return jsonify({
        "consistency_score": min(100, consistency_score),
        "effort_trend": effort_trend,
        "dropout_risk": dropout_risk,
        "study_profile": study_profile,
        "top_priority": top_priority,
        "alerts": alerts,
        "weekly_summary": {
            "total_minutes": sum(d.get('actual', 0) for d in effort_trend),
            "avg_completion": f"{int(completion_rate * 100)}%"
        }
    })

from flask import Blueprint, request, jsonify
import os
import json
from ai.planner import generate_study_plan
from ai.mentor import mentor_message
from ai.ml_logic import calculate_weakness_scores, calculate_dropout_risk, recommend_time_range, calculate_study_profile

planner = Blueprint("planner", __name__)

@planner.route("/predict-weakness", methods=["POST"])
def predict_weakness():
    data = request.get_json()
    history = data.get("history", [])
    scores = calculate_weakness_scores(history)
    return jsonify({"weakness_scores": scores})

@planner.route("/predict-time", methods=["POST"])
def predict_time():
    data = request.get_json()
    history = data.get("history", [])
    rec = recommend_time_range(history)
    return jsonify({"time_recommendation": rec})

@planner.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    if not data or "subjects" not in data or "daily_time_minutes" not in data:
        return jsonify({"error": "Missing required fields: subjects, daily_time_minutes"}), 400

    streak = data.get("streak", 0)
    history = data.get("history", [])

    # ML Maturity: Get full results with rationales
    weakness_results = calculate_weakness_scores(history)
    dropout_result = calculate_dropout_risk(history, streak)
    profile_result = calculate_study_profile(history)
    time_result = recommend_time_range(history)

    # Extract values for dependency injection
    study_profile = profile_result["value"]
    dropout_risk = dropout_result["level"]

    plan = generate_study_plan(
        data["subjects"],
        data["daily_time_minutes"],
        data.get("last_day_progress", {}),
        study_profile=study_profile
    )

    mentor = mentor_message(
        data["subjects"],
        data["daily_time_minutes"],
        data.get("last_day_progress", {}),
        streak,
        dropout_risk=dropout_risk,
        study_profile=study_profile
    )
    
    return jsonify({
        "study_plan": plan,
        "mentor_message": mentor,
        "weakness_scores": weakness_results,
        "dropout_risk": dropout_risk,
        "dropout_rationale": dropout_result["rationale"],
        "study_profile": study_profile,
        "study_profile_rationale": profile_result["rationale"],
        "study_profile_confidence": profile_result["confidence"],
        "recommended_time_range": time_result["range"],
        "recommended_time_rationale": time_result["rationale"]
    })

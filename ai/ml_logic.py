import numpy as np
import os
import json

def calculate_weakness_scores(history):
    """
    Analyzes historical data to predict subject weakness with MATURE Trend Analysis.
    Returns: { subject: { score, rationale, confidence } }
    """
    if not history:
        return {}

    subjects = {}
    history = sorted(history, key=lambda x: x.get('date', ''))

    # Threshold for confidence
    min_data_points = 5

    # Data exists: Perform Trend Analysis
    for i, entry in enumerate(history):
        sub = entry.get('subject')
        if not sub: continue
        
        recency_weight = 0.5 + (0.5 * (i / len(history)))

        if sub not in subjects:
            subjects[sub] = {
                'weighted_skips': 0, 'weighted_diff': 0, 'weighted_minutes': 0,
                'total_weight': 0, 'session_count': 0,
                'time_history': [], 'completion_history': []
            }
        
        stats = subjects[sub]
        stats['total_weight'] += recency_weight
        stats['session_count'] += 1
        
        skip_val = 1.0 if not entry.get('completed', False) else 0.0
        stats['weighted_skips'] += (skip_val * recency_weight)
        
        diff = entry.get('difficulty', 'average')
        diff_weight = 3 if diff == 'weak' else 2 if diff == 'average' else 1
        stats['weighted_diff'] += (diff_weight * recency_weight)
        
        stats['time_history'].append(entry.get('minutes', 0))
        stats['completion_history'].append(1 if entry.get('completed') else 0)

    results = {}
    for sub, stats in subjects.items():
        w = stats['total_weight']
        
        # Base ML Features
        skip_rate = stats['weighted_skips'] / w
        avg_diff = (stats['weighted_diff'] / w - 1) / 2
        
        # Trend Analysis: Time vs Completion (Confusion Detect)
        confusion_detected = False
        mastery_detected = False
        if len(stats['time_history']) >= 3:
            time_slope = np.polyfit(range(len(stats['time_history'])), stats['time_history'], 1)[0]
            comp_slope = np.polyfit(range(len(stats['completion_history'])), stats['completion_history'], 1)[0]
            
            confusion_detected = (time_slope > 2 and comp_slope < -0.1)
            mastery_detected = (time_slope < -2 and comp_slope > 0.1)
            
            confusion_boost = 0.2 if confusion_detected else 0.0
            mastery_reduction = 0.15 if mastery_detected else 0.0
        else:
            confusion_boost = 0
            mastery_reduction = 0

        raw_score = (skip_rate * 0.4) + (avg_diff * 0.3) + confusion_boost - mastery_reduction
        
        trust = min(1.0, stats['session_count'] / 5.0)
        final_score = (raw_score * trust) + (0.5 * (1.0 - trust))
        final_score = max(0.01, min(0.99, round(float(final_score), 2)))

        # Rationale Building
        rationale = f"Based on {stats['session_count']} sessions. "
        if confusion_detected:
            rationale += "Detected rising study time but falling completion, suggesting potential confusion. "
        elif mastery_detected:
            rationale += "Low time and high completion detected—you're mastering this! "
        elif skip_rate > 0.4:
            rationale += "Frequently skipped in recent sessions. "
            
        confidence = "High" if stats['session_count'] >= min_data_points else "Medium" if stats['session_count'] >= 2 else "Low"

        results[sub] = {
            "score": final_score,
            "rationale": rationale.strip(),
            "confidence": confidence
        }

    return results

def recommend_time_range(history):
    """
    Predicts a range with rationale and confidence.
    """
    if not history:
        return {
            "range": [45, 90],
            "rationale": "Initial baseline for a balanced start.",
            "confidence": "Low"
        }
        
    history_times = [d.get('minutes', 0) for d in history if d.get('minutes', 0) > 0]
    base_time = np.mean(history_times) if history_times else 60
    
    # Simple fatigue wall logic (approximate)
    fail_points = [d.get('minutes', 30) for d in history if not d.get('completed')]
    fatigue_wall = np.mean(fail_points) * 0.9 if fail_points else base_time * 1.5
    
    rec_min = max(30, int(base_time * 0.8))
    rec_max = min(int(fatigue_wall), int(base_time * 1.3))
    
    rationale = f"Aligned with your {int(base_time)}m average focus time. "
    if fail_points:
        rationale += "Capped to avoid your historic 'fatigue wall'. "
    
    return {
        "range": [rec_min, rec_max],
        "rationale": rationale.strip(),
        "confidence": "High" if len(history) >= 5 else "Medium"
    }

def calculate_dropout_risk(history, streak):
    """
    Dropout Risk with Rationale and Confidence.
    """
    if not history or len(history) < 3:
        return {
            "level": "Low", 
            "rationale": "Welcome! We're just getting to know your habits.", 
            "confidence": "Low"
        }

    recent = history[-5:]
    completion_rate = sum(1 for d in recent if d.get('completed', False)) / len(recent)
    
    times = [d.get('minutes', 0) for d in recent]
    slope = np.polyfit(range(len(times)), times, 1)[0] if len(times) >= 2 else 0
    
    risk_score = 0
    rationale = "Your study rhythm is healthy and stable."
    
    if completion_rate < 0.5: 
        risk_score += 0.4
        rationale = "Low recent completion rate detected."
    if slope < -5: 
        risk_score += 0.3
        rationale += " Study duration is decreasing sharply."
    if streak == 0: 
        risk_score += 0.3
        rationale += " Streak broken—momentum needs a boost."

    level = "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"
    
    return {
        "level": level,
        "rationale": rationale.strip(),
        "confidence": "High" if len(history) >= 10 else "Medium"
    }

def calculate_study_profile(history):
    """
    Study Persona with Rationale and Confidence.
    """
    if not history or len(history) < 2:
        return {
            "value": "Universal Learner", 
            "rationale": "Collecting data to reveal your unique study style.",
            "confidence": "Low"
        }

    sessions = [d for d in history if d.get('completed')]
    if not sessions:
        return {"value": "Universal Learner", "rationale": "Complete a session to reveal your style.", "confidence": "Low"}

    avg_session = np.mean([d.get('minutes', 30) for d in sessions])
    completion_rate = len(sessions) / len(history)
    
    times = []
    for d in sessions:
        ts = d.get('timestamp')
        if ts:
            try:
                hour = int(ts.split('T')[1].split(':')[0])
                times.append(hour)
            except: pass
    
    morning_count = sum(1 for h in times if 5 <= h <= 11)
    night_count = sum(1 for h in times if 20 <= h or h <= 4)
    
    persona = "Universal Learner"
    rationale = "You have a balanced and adaptable approach to studying."
    
    if len(times) >= 3:
        if morning_count / len(times) > 0.6: 
            persona = "Morning Starter"
            rationale = "80% of your progress happens in the AM—you're an early bird focus master."
        elif night_count / len(times) > 0.6: 
            persona = "Night Owl"
            rationale = "You do your best work when the world sleeps. A true midnight genius."
    
    if persona == "Universal Learner":
        if avg_session < 35:
            persona = "Focus Sprinter"
            rationale = "You excel in high-intensity, short duration bursts."
        elif avg_session > 50:
            persona = "Marathon Learner"
            rationale = "You have the stamina for deep, extended flow-state sessions."

    return {
        "value": persona,
        "rationale": rationale,
        "confidence": "High" if len(sessions) >= 5 else "Medium"
    }

def persist_shadow_log(model_name, data):
    """
    Saves ML predictions for auditing.
    """
    log_file = 'database/ml_shadow_logs.json'
    try:
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        logs.append({"model": model_name, **data})
        if len(logs) > 100: logs = logs[-100:]
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=4)
    except: pass

from typing import List, Dict, Union, Any

# Study Profile Constants
PROFILE_UNIVERSAL = "Universal Learner"
PROFILE_FOCUS_SPRINTER = "Focus Sprinter"
PROFILE_MARATHON_LEARNER = "Marathon Learner"

# Importance Weights
WEIGHT_WEAK = 0.5
WEIGHT_AVERAGE = 0.3
WEIGHT_STRONG = 0.2

def generate_study_plan(
    subjects: Union[List[str], Dict[str, str]], 
    total_time: int, 
    last_day: Dict[str, bool], 
    study_profile: str = PROFILE_UNIVERSAL
) -> List[Dict[str, Any]]:
    
    weights = {
        "weak": WEIGHT_WEAK,
        "average": WEIGHT_AVERAGE,
        "strong": WEIGHT_STRONG
    }

    # Style-Aware Parameters
    block_size = 40
    if study_profile == PROFILE_FOCUS_SPRINTER:
        block_size = 25 # Pomodoro style
    elif study_profile == PROFILE_MARATHON_LEARNER:
        block_size = 60 # Flow state

    adjusted = {}

    # Handle list input (default to "average" importance)
    if isinstance(subjects, list):
        subjects = {s: "average" for s in subjects}
    
    if not subjects:
        return []

    for subject, level in subjects.items():
        adjusted[subject] = weights.get(level, weights["average"])

        if not last_day.get(subject, True):
            adjusted[subject] += 0.1

    total_weight = sum(adjusted.values())
    if total_weight == 0:
        return []
        
    # Keep track of session per subject for indexing
    session_counts = {s: 1 for s in subjects.keys()}
    plan = []

    for subject, weight in adjusted.items():
        minutes = int((weight / total_weight) * total_time)
        difficulty = subjects.get(subject, "average")
        
        # Split long sessions (e.g. > threshold -> block_size blocks)
        if minutes > (block_size * 1.5):
            while minutes > 0:
                block = block_size if minutes >= block_size else minutes
                plan.append({
                    "subject": subject,
                    "minutes": block,
                    "session_id": session_counts[subject],
                    "difficulty": difficulty
                })
                session_counts[subject] += 1
                minutes -= block
        elif minutes >= 15: # Minimum valid session
             plan.append({
                "subject": subject,
                "minutes": minutes,
                "session_id": session_counts[subject],
                "difficulty": difficulty
            })
             session_counts[subject] += 1

    return plan

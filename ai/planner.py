def generate_study_plan(subjects, total_time, last_day, study_profile="Universal Learner"):
    weights = {
        "weak": 0.5,
        "average": 0.3,
        "strong": 0.2
    }

    # Style-Aware Parameters
    block_size = 40
    if study_profile == "Focus Sprinter":
        block_size = 25 # Pomodoro style
    elif study_profile == "Marathon Learner":
        block_size = 60 # Flow state

    adjusted = {}

    # Handle list input (default to "average" importance)
    if isinstance(subjects, list):
        subjects = {s: "average" for s in subjects}

    for subject, level in subjects.items():
        adjusted[subject] = weights.get(level, 0.3)

        if not last_day.get(subject, True):
            adjusted[subject] += 0.1

    total_weight = sum(adjusted.values())
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

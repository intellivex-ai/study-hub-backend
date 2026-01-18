def mentor_message(subjects, total_time, progress, streak=0, level="Novice", dropout_risk="Low", study_profile="Universal Learner"):
    """
    Standardized 'Supportive Architect' voice for the Study Hub.
    Tone: Data-driven, grounded, professional, yet deeply encouraging.
    """
    completed_sessions = [s for s in progress if s.get('completed')]
    completed_count = len(completed_sessions)
    total_count = len(progress)
    is_all_done = total_count > 0 and completed_count == total_count

    # 1. Critical Support (High Risk)
    if dropout_risk == "High":
        return "I've analyzed your recent pace and noticed some friction. Today, let's prioritize consistency over intensity. Even a 10-minute session is a strategic win. I'm here to help you sustain your momentum, not drain it. 🛡️"

    # 2. Daily Goal Achieved
    if is_all_done:
        return f"Strategic objectives met. You've successfully completed {total_count} sessions and secured your {streak}-day streak. This is high-level discipline. Rest well, your brain needs the recovery phase. 🌌"

    # 3. Personalized Intro based on Profile
    intro_map = {
        "Focus Sprinter": "Let's tap into that high-intensity focus. Your profile favors rapid-fire wins. ⚡",
        "Marathon Learner": "Ready for a deep-work dive? Your stamina is your greatest asset today. 🐢",
        "Morning Starter": "Morning momentum detected. Let's capitalize on your peak energy window. 🌅",
        "Night Owl": "Midnight genius active. The quiet hours are yours to command. 🦉",
        "Universal Learner": "Great to see you. Let's apply standard discipline to today's goals. 🚀"
    }
    intro = intro_map.get(study_profile, "Stay focused! 🚀")

    # 4. Progress-Based Context
    if completed_count == total_count - 1 and total_count > 1:
        return f"One final session remains. You're 90% of the way to a perfect day. Let's close this loop with excellence. 💪"

    if streak >= 7:
        return intro + f" You're on a {streak}-day trajectory. This level of consistency is rare and powerful. Stay the course."

    if streak == 0 and completed_count == 0:
        return "Day One of the new streak. The initial push is always the hardest part of the architecture. Let's lay the first stone together. 🌱"

    # 5. Generic but consistent fallback
    return intro + " Your plan is optimized for today's time window. Stay disciplined with your check-ins, and let's keep the momentum moving."

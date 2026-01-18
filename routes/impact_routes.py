from flask import Blueprint, jsonify, request
import json
import os

impact = Blueprint("impact", __name__)

IMPACT_DATABASE = 'database/impact_state.json'
STUDY_HISTORY = 'database/study_history.json'

def get_impact_state():
    if os.path.exists(IMPACT_DATABASE):
        with open(IMPACT_DATABASE, 'r') as f:
            return json.load(f)
    return {
        "trees": [],
        "seeds": 0,
        "total_impact_points": 0,
        "co2_offset_symbolic": 0.0
    }

def save_impact_state(state):
    with open(IMPACT_DATABASE, 'w') as f:
        json.dump(state, f, indent=4)

@impact.route("/state", methods=["GET"])
def get_state():
    """
    Returns the current state of the Digital Forest.
    Calculates dynamic growth based on study history.
    """
    state = get_impact_state()
    history = []
    if os.path.exists(STUDY_HISTORY):
        with open(STUDY_HISTORY, 'r') as f:
            history = json.load(f)

    # Calculate Total Points from history (1 point per 60 minutes)
    total_minutes = sum(d.get('minutes', 0) for d in history if d.get('completed'))
    # 60m = 1 seed/tree
    expected_total = total_minutes // 60
    
    # Update state if new seeds/trees earned
    if expected_total > state["total_impact_points"]:
        new_items = int(expected_total - state["total_impact_points"])
        for _ in range(new_items):
            state["trees"].append({
                "id": len(state["trees"]) + 1,
                "type": "oak", # Could be randomized
                "stage": "seed", # seed -> sprout -> sapling -> tree
                "planted_at": "Today"
            })
        state["total_impact_points"] = int(expected_total)
        state["co2_offset_symbolic"] = round(expected_total * 0.5, 2) # Heuristic: 0.5kg per tree
        save_impact_state(state)

    return jsonify(state)

@impact.route("/grow", methods=["POST"])
def grow_trees():
    """
    Simulates growth over time.
    Actually just a placeholder for now to advance stages.
    """
    state = get_impact_state()
    for tree in state["trees"]:
        if tree["stage"] == "seed": tree["stage"] = "sprout"
        elif tree["stage"] == "sprout": tree["stage"] = "sapling"
        elif tree["stage"] == "sapling": tree["stage"] = "tree"
    
    save_impact_state(state)
    return jsonify(state)

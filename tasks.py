# tasks.py
import os
import json
from datetime import datetime

TASKS_FILE = 'tasks.json'
TIME_FMT = '%Y-%m-%d %H:%M:%S'

def load_tasks():
    """Load tasks as a list of dicts (with created/completed timestamps)."""
    if not os.path.exists(TASKS_FILE):
        return []

    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)

    now = datetime.now().strftime(TIME_FMT)
    for task in tasks:
        if "created_at" not in task:
            task["created_at"] = now
        if "completed_at" not in task:
            task["completed_at"] = None

    return tasks
def load_tasks():
    """Load tasks as a list of dicts (with created/completed timestamps)."""
    if not os.path.exists(TASKS_FILE):
        return []

    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)

    now = datetime.now().strftime(TIME_FMT)
    for task in tasks:
        if "created_at" not in task:
            task["created_at"] = now
        if "completed_at" not in task:
            task["completed_at"] = None

    return tasks

def save_tasks(tasks):
    """Overwrite tasks.json with the given list."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

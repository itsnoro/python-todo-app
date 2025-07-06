# tasks.py
import os
import json
from datetime import datetime

TASKS_FILE = 'tasks.json'
TIME_FMT = '%Y-%m-%d %H:%M:%S'

def load_tasks():
    """Load tasks as a list of dicts."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    """Overwrite tasks.json with the given list."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

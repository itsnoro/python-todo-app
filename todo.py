#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime

TASKS_FILE = 'tasks.json'
TIME_FMT = '%Y-%m-%d %H:%M:%S'

def load_tasks():
    """Load tasks (sorted by created_at)."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)
    # Sort by creation timestamp
    return sorted(tasks, key=lambda t: t['created_at'])

def save_tasks(tasks):
    """Write the full task list back to disk."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("🎉 No tasks yet!")
        return
    for t in tasks:
        status = '✓' if t.get('done') else ' '
        created = t['created_at']
        line = f"[{t['id']}] [{status}] {t['desc']} (created: {created})"
        if t.get('done'):
            line += f" (done: {t['completed_at']})"
        print(line)

def add_task(description: str):
    tasks = load_tasks()
    next_id = max((t['id'] for t in tasks), default=0) + 1
    now = datetime.now().strftime(TIME_FMT)
    new_task = {
        'id': next_id,
        'desc': description,
        'done': False,
        'created_at': now,
        'completed_at': None
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Added task [{next_id}]: {description}")

def complete_task(task_id: int):
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == task_id:
            if t.get('done'):
                print(f"Task [{task_id}] is already completed.")
            else:
                t['done'] = True
                t['completed_at'] = datetime.now().strftime(TIME_FMT)
                save_tasks(tasks)
                print(f"✅ Marked task [{task_id}] as done.")
            return
    print(f"❌ No task found with ID {task_id}.")

def remove_task(task_id: int):
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t['id'] == task_id:
            removed = tasks.pop(i)
            save_tasks(tasks)
            print(f"🗑️  Removed task [{task_id}]: {removed['desc']}")
            return
    print(f"❌ No task found with ID {task_id}.")

def edit_task(task_id: int, new_desc: str):
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == task_id:
            old = t['desc']
            t['desc'] = new_desc
            save_tasks(tasks)
            print(f"✏️  Edited task [{task_id}]: \"{old}\" → \"{new_desc}\"")
            return
    print(f"❌ No task found with ID {task_id}.")

def main():
    parser = argparse.ArgumentParser(prog='todo')
    subparsers = parser.add_subparsers(dest='cmd')

    subparsers.add_parser('list', help='List all tasks')

    add_p = subparsers.add_parser('add', help='Add a new task')
    add_p.add_argument('desc', metavar='DESCRIPTION', help='Task description')

    done_p = subparsers.add_parser('done', help='Mark a task as done')
    done_p.add_argument('id', type=int, metavar='ID', help='ID of the task to mark done')

    rm_p = subparsers.add_parser('remove', help='Remove a task by ID')
    rm_p.add_argument('id', type=int, metavar='ID', help='ID of the task to remove')

    edit_p = subparsers.add_parser('edit', help='Edit a task’s description')
    edit_p.add_argument('id', type=int, metavar='ID', help='ID of the task to edit')
    edit_p.add_argument('desc', metavar='NEW_DESCRIPTION', help='New task description')

    args = parser.parse_args()

    if args.cmd == 'list':
        list_tasks()
    elif args.cmd == 'add':
        add_task(args.desc)
    elif args.cmd == 'done':
        complete_task(args.id)
    elif args.cmd == 'remove':
        remove_task(args.id)
    elif args.cmd == 'edit':
        edit_task(args.id, args.desc)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

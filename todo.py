#!/usr/bin/env python3

import argparse
import json
import os

TASKS_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("🎉 No tasks yet!")
        return
    for t in tasks:
        status = '✓' if t.get('done', False) else ' '
        print(f"[{t['id']}] [{status}] {t['desc']}")

def add_task(description: str):
    tasks = load_tasks()
    # Determine next ID
    next_id = max((t['id'] for t in tasks), default=0) + 1
    new_task = {
        'id': next_id,
        'desc': description,
        'done': False
    }
    tasks.append(new_task)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)
    print(f"Added task [{next_id}]: {description}")

def complete_task(task_id: int):
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == task_id:
            if t.get('done'):
                print(f"Task [{task_id}] is already completed.")
            else:
                t['done'] = True
                with open(TASKS_FILE, 'w') as f:
                    json.dump(tasks, f, indent=2)
                print(f"✅ Marked task [{task_id}] as done.")
            return
    print(f"❌ No task found with ID {task_id}.")

def main():
    parser = argparse.ArgumentParser(prog='todo')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.add_parser('list', help='List all tasks')
    # Add parser for "add" command
    add_p = subparsers.add_parser('add', help='Add a new task')
    add_p.add_argument('desc', metavar='DESCRIPTION', help='Task description')
    # Add parser for "done" command
    done_p = subparsers.add_parser('done', help='Mark a task as done')
    done_p.add_argument('id', type=int, metavar='ID', help='ID of the task to mark done')

    args = parser.parse_args()

    if args.cmd == 'list':
        list_tasks()
    elif args.cmd == 'add':
        add_task(args.desc)
    elif args.cmd == 'done':
        complete_task(args.id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

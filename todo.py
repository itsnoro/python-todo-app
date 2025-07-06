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

def main():
    parser = argparse.ArgumentParser(prog='todo')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.add_parser('list', help='List all tasks')
    # Add parser for "add" command
    add_p = subparsers.add_parser('add', help='Add a new task')
    add_p.add_argument('desc', metavar='DESCRIPTION', help='Task description')

    args = parser.parse_args()

    if args.cmd == 'list':
        list_tasks()
    elif args.cmd == 'add':
        add_task(args.desc)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

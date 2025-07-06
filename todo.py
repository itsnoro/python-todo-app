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

def main():
    parser = argparse.ArgumentParser(prog='todo')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.add_parser('list', help='List all tasks')
    args = parser.parse_args()

    if args.cmd == 'list':
        list_tasks()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

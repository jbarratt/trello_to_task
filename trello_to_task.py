#!/usr/bin/env python3

from __future__ import print_function
try:
    import simplejson as json
except ImportError:
    import json
import uuid
import sys
import re
from copy import deepcopy
from datetime import datetime

arg_len = len(sys.argv)
if arg_len < 3:
    print(f'Usage: {sys.argv[0]} <trello-file.json> <taskwarrior-output.json> [done_list_name...]')
    sys.exit(1)

infile = open(sys.argv[1], 'r')
outfile = open(sys.argv[2], 'w')
done_list_res = []

if arg_len > 3:
    done_list_re_strings = sys.argv[3:arg_len]
    for done_list_re_string in done_list_re_strings:
        done_list_res.append(re.compile(done_list_re_string))
else:
    done_list_res.append(re.compile("Done"))

import_date_format='%Y-%m-%dT%H:%M:%S.%fZ'
export_date_format='%Y%m%dT%H%M%SZ'

trello = json.loads(infile.read())

tasks = []

def get_tw_time(trello_time):
    """ convert trello time format to taskwarrior time format
    """
    return datetime.strptime(trello_time, import_date_format).strftime(export_date_format)

def matches_done_list_re(list_name):
    for done_list_re in done_list_res:
        if done_list_re.match(list_name):
            return True
        else:
            continue

def get_tw_formatted_string(st):
    return st.replace(' ', '').lower()


def export_task(project_name, card, tlist, status):
    """ find comments and make into annotations.
        find checklist items and make tasks which we then depend on.
    """
    task = {"status": status, "description": card['name']}
    # Someday Maybe => tag somedaymaybe
    task['tags'] = get_tw_formatted_string(tlist['name'])
    task['uuid'] = str(uuid.uuid4())
    task['annotations'] = []

    # Find comments, convert to annotations
    for action in trello['actions']:
        try:
            if action['type'] == 'createCard' and action['data']['card']['id'] == card['id']:
                task['entry'] = get_tw_time(action['date'])
            elif action['type'] == 'commentCard' and action['data']['card']['id'] == card['id']:
                task['annotations'].append({"entry": action['date'],
                                        "description": action['data']['text']})
        except Exception as e:
            print(e)

    if len(task['annotations']) == 0:
        del(task['annotations'])

    task['project'] = get_tw_formatted_string(project_name)

    # find checklists, make this task depend on them
    dependon = []
    for cl_id in card['idChecklists']:
        for cl in trello['checklists']:
            if cl['id'] == cl_id:
                for item in cl['checkItems']:
                    subtask = deepcopy(task)
                    subtask['description'] = item['name']
                    if 'annotations' in subtask:
                        del(subtask['annotations'])
                    subtask['uuid'] = str(uuid.uuid4())
                    dependon.append(subtask['uuid'])
                    tasks.append(subtask)

    if len(dependon) > 0:
        task['depends'] = ','.join(dependon)

    tasks.append(task)

board_name=trello['name']

for card in trello['cards']:
    if not card['closed']:
        # what list is this from?
        for l in trello['lists']:
            if l['id'] == card['idList']:
                if l['closed'] or matches_done_list_re(l['name']):
                    export_task(board_name, card, l, 'completed')
                else:
                    export_task(board_name, card, l, 'pending')

for task in tasks:
    print(json.dumps(task), file=outfile)

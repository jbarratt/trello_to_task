#!/usr/bin/env python

import simplejson as json
import uuid
import sys
from copy import deepcopy
from datetime import datetime

infile = open(sys.argv[1], 'r')
outfile = open(sys.argv[2], 'w')
# print >>outfile json.dumps(dict)

# cheat and use the same date string for all tasks
datestring = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

trello = json.loads(infile.read())

tasks = []


def export_task(card, tlist):
    """ find comments and make into annotations.
        find checklist items and make tasks which we then depend on.
    """
    task = {"status": "pending", "description": card['name']}
    task['entry'] = datestring
    # Someday Maybe => tag somedaymaybe
    task['tags'] = [tlist['name'].replace(' ', '').lower()]
    task['uuid'] = str(uuid.uuid4())
    task['annotations'] = []

    # Find comments, convert to annotations
    for action in trello['actions']:
        try:
            if action['type'] == 'commentCard' and action['data']['card']['id'] == card['id']:
                task['annotations'].append({"entry": datestring,
                                            "description": action['data']['text']})
        except:
            pass

    if len(task['annotations']) == 0:
        del(task['annotations'])

    # make these all the same project
    task['project'] = 'home.' + card['name'].replace(' ', '').lower()

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
    else:
        task['project'] = 'home'

    tasks.append(task)


for card in trello['cards']:
    if not card['closed']:
        # what list is this from?
        for l in trello['lists']:
            if l['id'] == card['idList']:
                if not l['closed'] and l['name'] != 'Done':
                    export_task(card, l)

for task in tasks:
    print >>outfile, json.dumps(task)

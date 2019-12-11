import requests
import argparse
import pdb
import json
from secrets import API_TOKEN
import datetime
import holidays
import pprint
import uuid

pp = pprint.PrettyPrinter()

BASE_URL = 'https://api.todoist.com/rest/v1/'

HEADERS = {
   'Authorization': 'Bearer %s' % API_TOKEN
}

parser = argparse.ArgumentParser()
parser.add_argument('--recurring', '-r', action='store_true', default=False)
parser.add_argument('--force-all', '-f', action='store_true', default=False)
parser.add_argument('--to', '-t')
args = parser.parse_args()

# Stolen from https://stackoverflow.com/questions/9187215/datetime-python-next-business-day
def next_business_day():
    ONE_DAY = datetime.timedelta(days=1)
    HOLIDAYS_US = holidays.US()
    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    next_day = today + ONE_DAY
    while next_day.weekday() in holidays.WEEKEND or next_day in HOLIDAYS_US:
        next_day += ONE_DAY
    return next_day
 

req = requests.get(BASE_URL+'projects', headers=HEADERS)
projects = []
if req.status_code == 200:
    projects = req.json()
work_project_id = [project for project in projects if 'Work' in project['name']][0]['id']

res = requests.get(BASE_URL+'tasks',
        params={'project_id': work_project_id},
        headers=HEADERS
    ).json()

next_work_day = next_business_day()
if args.to:
    date_array = args.to.split('-')
    month = (int)(date_array[0])
    day = (int)(date_array[1])
    pdb.set_trace()
    next_work_day = datetime.datetime.combine(datetime.datetime(year=2019, month=month, day=day), datetime.datetime.min.time())
    # next_work_day = date

tasks_due_before_work = [task for task in res
                   if (args.recurring or task.get('due', {}).get('recurring') == False)
                   and task.get('due', {}).get('date')
                   and datetime.datetime.strptime(task.get(
                       'due', {}).get('date'), '%Y-%m-%d') < next_work_day]

for task in tasks_due_before_work:
    output = f'Move {task["content"]} to {next_work_day.strftime("%Y-%m-%d")}? [y/n]'
    if args.force_all:
        print(output+' y')
    else:
        response = input(output)
    if not args.force_all and response != 'y':
        continue
    res = requests.post(BASE_URL+'tasks/'+str(task['id']),
        data=json.dumps({
            'due_date': next_work_day.strftime('%Y-%m-%d'),
        }),
        headers={**HEADERS, **{'Content-Type': 'application/json', 'X-Request-Id': str(uuid.uuid4())}}
    )
    if res.status_code not in [200, 204]:
        # TODO debug why things end up here
        pdb.set_trace()
        print('Error: ')
        print(res.content.decode('utf-8'))

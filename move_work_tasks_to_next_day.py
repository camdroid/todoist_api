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

BASE_URL = 'https://beta.todoist.com/API/v8/'
HEADERS = {
   'Authorization': 'Bearer %s' % API_TOKEN
}

parser = argparse.ArgumentParser()
parser.add_argument('--recurring', action='store_true', default=False)
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
 

projects = requests.get(BASE_URL+'projects', headers=HEADERS).json()
work_project_id = [project for project in projects if project['name'] == 'Work'][0]['id']

res = requests.get(BASE_URL+'tasks',
        params={'project_id': work_project_id},
        headers=HEADERS
    ).json()

next_work_day = next_business_day()
tasks_due_before_work = [task for task in res
                   if (args.recurring or task.get('due', {}).get('recurring') == False)
                   and task.get('due', {}).get('date')
                   and datetime.datetime.strptime(task.get(
                       'due', {}).get('date'), '%Y-%m-%d') < next_work_day]

for task in tasks_due_before_work:
    response = input(f'Move {task["content"]} to {next_work_day.strftime("%Y-%m-%d")}? [y/n]')
    if response != 'y':
        continue
    requests.post(BASE_URL+'tasks/'+str(task['id']),
        data=json.dumps({
            'due_date': next_work_day.strftime('%Y-%m-%d'),
        }),
        headers={**HEADERS, **{'Content-Type': 'application/json', 'X-Request-Id': str(uuid.uuid4())}}
    )

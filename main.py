from todoist.api import TodoistAPI
from secrets import API_TOKEN


class TaskTracker():
    def __init__(self):
        self.api = TodoistAPI(API_TOKEN)
        self.api.sync()
        self.tasks = self.api.state['items']

    def get_task_by_id(self, tid):
        return [item for item in self.tasks if item['id'] == tid][0]


tracker = TaskTracker()
target_tasks = [item for item in tracker.tasks
                if 'checks' in item['content']]

parent_task = tracker.get_task_by_id(target_tasks[0]['id'])

import pdb; pdb.set_trace()
print(api.state['projects'])

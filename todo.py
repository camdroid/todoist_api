import argparse
import todoist
from secrets import API_TOKEN
import pprint
import sys
import gantt
import datetime
import pdb

pprinter = pprint.PrettyPrinter()
pp = pprinter.pprint

api = todoist.TodoistAPI(API_TOKEN)
api.sync()

def get_label_name(label_id):
    all_labels = api.state['labels']
    labels = [label for label in all_labels if label['id'] == label_id]
    if labels:
        return labels[0]

def get_task_id_by_content(content):
    items = [item for item in api.state['items'] if item['content'] == content]
    if items:
        return items[0]['id']

def mark_task_as_dependent_by_content(content1, content2):
    mark_task_as_dependent_on(get_task_id_by_content(content1), get_task_id_by_content(content2))

def mark_task_as_dependent_on(task1, task2):
    api.notes.add(task1, f'Dependent on {task2}')
    api.notes.add(task2, f'Dependency: {task1}')
    api.commit()
    item = [item for item in api.state['items'] if item['id'] == task1][0]
    pdb.set_trace()
    print(x)

def parse_gantt_args(args):
    if args.add_dependency:
        use_ids = args.fromi and args.toi
        use_content = args.fromc and args.toc
        pdb.set_trace()
        if not use_ids and not use_content:
            pp('Must use either ids or content')
            sys.exit(1)
        if use_ids:
            mark_task_as_dependent_on(args.fromi, args.toi)
        if use_content:
            mark_task_as_dependent_by_content(args.fromc, args.toc)

def parse_item_args(args):
    if not args.id:
        pp('Not sure what you\'re trying to do...')
        sys.exit(1)
    if args.notes:
        notes = get_notes_for_task(args.id)
        pp(notes)
        return notes

    # If nothing else specified, print the content of the task
    task = [item for item in api.state['items'] if item['id'] == args.id]
    pp(task[0]['content'])
    return task[0]

def get_notes_for_task(task_id):
    notes = api.state['notes']
    notes_for_task = [note for note in notes if note['item_id'] == task_id]
    return notes_for_task


def get_dependencies_for_task(task_id):
    pass

        

items = api.state['items']
ll_projects = [project for project in api.state['projects'] if 'Landlord' in project['name']]
if ll_projects:
    ll_project_id = ll_projects[0]['id']

label_names = [get_label_name(lid) for lid in items[0]['labels']]
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help')

item_parser = subparsers.add_parser('item', help='get info on items')
item_parser.add_argument('id', type=int)
item_parser.add_argument('--notes', action='store_true')
item_parser.set_defaults(func=parse_item_args)

gantt_parser = subparsers.add_parser('gantt', help='gantt tools')
gantt_parser.add_argument('--add-dependency', action='store_true')
gantt_parser.add_argument('-f', '--fromi', type=int)
gantt_parser.add_argument('-t', '--toi', type=int)
gantt_parser.add_argument('--fromc', type=str)
gantt_parser.add_argument('--toc', type=str)
gantt_parser.set_defaults(func=parse_gantt_args)

args = parser.parse_args()
if 'func' in args:
    args.func(args)


cam = gantt.Resource('Cam')
landlord = gantt.Project(name='Landlord')
send_task = gantt.Task(name='Send lease addendum',
                  start=datetime.date(2019, 12,10),
                  duration=4,
                  resources=[cam])
sign_task = gantt.Task(
    name='Make sure lease addendum is signed',
    start=datetime.date(2019, 12, 13),
    duration=1,
    resources=[cam],
    depends_of=send_task,
)

landlord.add_task(send_task)
landlord.add_task(sign_task)
# Have to open the SVG manually for now, will have to figure this out later
landlord.make_svg_for_tasks(
    filename='landlord_gantt_chart.svg',
    today=datetime.datetime.today(),
    start=datetime.date.today()-datetime.timedelta(days=7),
    end=datetime.date.today()+datetime.timedelta(days=30),
);

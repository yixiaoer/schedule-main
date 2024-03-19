import datetime
import json
import os
import sys

from tabulate import tabulate

DB_FILE_NAME = os.path.expanduser('~/.cache/data.json')

def get_now() -> str:
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    return time

def read_data() -> list:
    if not os.path.exists(DB_FILE_NAME):
        return []
    with open(DB_FILE_NAME, encoding='utf-8') as f:
        return json.load(f)

def write_data(data: list) -> None:
    with open(DB_FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def get_next_id(data: list) -> int:
    if not data:
        return 0
    return data[-1]['id'] + 1

def operation_insert(name: str, time: str = get_now()) -> None:
    data = read_data()
    id_ = get_next_id(data)

    data.append({
        'id': id_,
        'time': time,
        'name': name,
        'status': {'type': 'ongoing'},
    })

    write_data(data)

def operation_tidspunkt(name: str, time: str = get_now()) -> None:
    data = read_data()

    id_ = get_next_id(data)

    if time == 'now':
        time = get_now()

    data.append({
        'id': id_,
        'time': time,
        'name': name,
        'status': {'type': 'tidspunkt'},
    })

    write_data(data)

def operation_remove(id_: str) -> None:
    data = read_data()

    if id_.startswith('LAST'):
        if id_ == 'LAST':
            idx = 1
        else:
            idx = - int(id_[4:]) + 1  # 4: len('LAST')
    else:
        for idx, item in enumerate(reversed(data)):
            if item['id'] == idx:
                break
    del data[-idx]

    write_data(data)

def operation_amend(id_: str, *, name: str | None = None, time: str | None = None) -> None:
    data = read_data()

    if time == 'now':
        time = get_now()

    if id_.startswith('LAST'):
        if id_ == 'LAST':
            idx = -1
        else:
            idx = int(id_[4:]) - 1  # 4: len('LAST')
        item = data[idx]
    else:
        for item in reversed(data):
            if item['id'] == idx:
                break

    if name is not None:
        item['name'] = name
    if time is not None:
        item['time'] = time

    write_data(data)

def operation_conclude(id_: str, time: str = get_now()) -> None:
    # timemgr -c LAST -t now 
    data = read_data()

    if time == 'now':
        time = get_now()

    if id_.startswith('LAST'):
        if id_ == 'LAST':
            idx = -1
        else:
            idx = int(id_[4:]) - 1  # 4: len('LAST')
        item = data[idx]
    else:
        for item in reversed(data):
            if item['id'] == idx:
                break

    if item['status']['type'] in ('ongoing', 'ended'):
        item['status']['type'] = 'ended'
        item['status']['end_time'] = time
    else:
        raise ValueError(f'Only ongoing events can be concluded.')

    write_data(data)

def _process_item_for_printing(item: dict) -> list:
    id_ = item['id']
    time = item['time']
    time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S").astimezone(datetime.datetime.now().astimezone().tzinfo)
    name = item['name']
    status = item['status']
    if status['type'] == 'ongoing':
        status = 'Ongoing'
    elif status['type'] == 'tidspunkt':
        status = 'Tidspunkt'
    elif status['type'] == 'ended':
        status = f'Ended at {status["end_time"]}'
    return [id_, time, name, status]

def operation_list() -> None:
    data = read_data()

    headers = ['ID', 'Time', 'Name', 'Status']
    contents = [_process_item_for_printing(item) for item in data]

    print(tabulate(contents, headers=headers, tablefmt='grid'))

def operation_help() -> None:
    print('''Usage: schedule-main -i|-p|-c|-a|-r|-l|-h''')

def tokenize_args(args: list) -> dict:
    parsed_args = {}

    args_it = iter(args)

    def parse_option_with_no_arg(option_name: str) -> None:
        if option_name in parsed_args:
            raise ValueError(f'Duplicated option "{option_name}"')
        parsed_args[option_name] = None

    def parse_option_with_one_arg(option: str, option_name: str) -> None:
        try:
            arg = next(args_it)
        except StopIteration:
            raise ValueError(f'Expected an argument for {option}') from None
        if arg.startswith('-'):
            raise ValueError(f'Expected an argument for {option}')
        if option_name in parsed_args:
            raise ValueError(f'Duplicated option "{option_name}"')
        parsed_args[option_name] = arg

    try:
        while True:
            arg = next(args_it)

            # Options with no argument
            if arg == '-i': parse_option_with_no_arg('insert')
            elif arg == '--insert': parse_option_with_no_arg('insert')
            elif arg == '-p': parse_option_with_no_arg('tidspunkt')
            elif arg == '--tidspunkt': parse_option_with_no_arg('tidspunkt')
            elif arg == '-l': parse_option_with_no_arg('list')
            elif arg == '--list': parse_option_with_no_arg('list')
            elif arg == '-h': parse_option_with_no_arg('help')
            elif arg == '--help': parse_option_with_no_arg('help')

            # Options with one argument
            elif arg == '-n': parse_option_with_one_arg('-n', 'name')
            elif arg == '--name': parse_option_with_one_arg('--name', 'name')
            elif arg == '-t': parse_option_with_one_arg('-t', 'time')
            elif arg == '--time': parse_option_with_one_arg('--time', 'time')
            elif arg == '-r': parse_option_with_one_arg('-r', 'remove')
            elif arg == '--remove': parse_option_with_one_arg('--remove', 'remove')
            elif arg == '-a': parse_option_with_one_arg('-a', 'amend')
            elif arg == '--amend': parse_option_with_one_arg('--amend', 'amend')
            elif arg == '-c': parse_option_with_one_arg('-c', 'conclude')
            elif arg == '--conclude': parse_option_with_one_arg('--conclude', 'conclude')

            # Error handling
            elif arg.startswith('-'):
                raise ValueError(f'Unrecognisable option "{arg}"')
            else:
                raise ValueError(f'Stray argument "{arg}"')
    except StopIteration:
        pass

    return parsed_args

def dispatch_operation(parsed_args: dict) -> None:
    if 'insert' in parsed_args:
        del parsed_args['insert']
        operation_insert(**parsed_args)
    elif 'tidspunkt' in parsed_args:
        del parsed_args['tidspunkt']
        operation_tidspunkt(**parsed_args)
    elif 'remove' in parsed_args:
        arg = parsed_args['remove']
        del parsed_args['remove']
        operation_remove(arg, **parsed_args)
    elif 'amend' in parsed_args:
        arg = parsed_args['amend']
        del parsed_args['amend']
        operation_amend(arg, **parsed_args)
    elif 'conclude' in parsed_args:
        arg = parsed_args['conclude']
        del parsed_args['conclude']
        operation_conclude(arg, **parsed_args)
    elif 'list' in parsed_args:
        del parsed_args['list']
        operation_list(**parsed_args)
    elif 'help' in parsed_args:
        del parsed_args['help']
        operation_help(**parsed_args)

def main() -> None:
    args = sys.argv[1:]  # skip program name
    parsed_args = tokenize_args(args)
    dispatch_operation(parsed_args)

if __name__ == '__main__':
    main()

# if parsed_args:
#     redundant_args = ", ".join([f'"{arg}"' for arg in parsed_args])
#     raise ValueError(f'Option(s) {redundant_args} cannot be imposed on operation "list"')


# timexxxxxxx <b>[begin]
# timexxxxxxx <b>[end]

# timexxxxxxx <light>
# xx[b]
# xx[e]


# TIME NAME       STATUS
# now  Bilibili   Ongoing/Ended at <time>/Tidspunkt


# # {'id': 273, 'time': xxxxx, 'name': 'Bilibili', 'status': {'type': 'ongoing'}}
# {'id': 273, 'time': xxxxx, 'name': 'Bilibili', 'status': {'type': 'ended', 'time': 'xxx'}}
# {'id': 274, 'time': xxxxx, 'name': 'Dinner', 'status': {'type': 'ongoing'}}



# timemgr -i -n 'Bilibili' -t now
# -i: insert

# timemgr -p -n 'Bilibili' -t now
# -p: tidspunkt

# timemgr -r LAST
# timemgr -r LAST-1
# -r: remove

# timemgr -a LAST -n 'Bilibili' -t now
# -a: amend

# timemgr -c LAST -t now 
# -c: conclude

# timemgr -l
# -l: list

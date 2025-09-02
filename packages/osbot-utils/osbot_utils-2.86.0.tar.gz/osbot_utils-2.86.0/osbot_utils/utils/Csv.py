import csv
from io                                     import StringIO
from osbot_utils.utils.Http                 import GET
from osbot_utils.utils.Files                import file_open
from osbot_utils.decorators.lists.group_by  import group_by
from osbot_utils.decorators.lists.index_by  import index_by


@index_by
@group_by
def load_csv_from_iterable(iterable, delimiter=','):
    csv_reader = csv.DictReader(iterable, delimiter=delimiter)
    return [row for row in csv_reader]

@index_by
@group_by
def load_csv_from_file(file_path, delimiter=','):
    iterable = file_open(file_path)
    return load_csv_from_iterable(iterable, delimiter=delimiter)

@index_by
@group_by
def load_csv_from_str(csv_data, delimiter=','):
    iterable = StringIO(csv_data)
    return load_csv_from_iterable(iterable, delimiter=delimiter)

@index_by
@group_by
def load_csv_from_url(url, headers, delimiter=','):
    csv_data = GET(url=url, headers=headers)
    return load_csv_from_str(csv_data=csv_data, delimiter=delimiter)


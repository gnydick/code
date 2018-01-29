import json
import os
import sys

args = "sql-to-json.py %s > json" % sys.argv[1]
os.system(args)

file = open("json", "r")
sql = json.load(file)
file.close()


def __process_dict__(dict_name, keys, required, optional):
    for key in required:
        if key not in keys:
            print "Missing key: %s['%s']'" % (dict_name, key)
            exit(255)

    for key in keys:
        if key not in required + optional:
            print "Unknown key: %s['%s']'" % (dict_name, key)
            exit(255)


class Table:
    def __init__(self):
        self.name = None
        self.fields = []
        self.rows = []


class Selector:
    def __init__(self, selector):
        self.source = None
        self.az = None
        self._process_selector_(selector)

    def __repr__(self):
        return self.source.column.name \
               + (':table_' + self.source.column.table if self.source.column.table is not None else '') \
               + (':alias_' + self.az if self.az is not None else '')

    def _process_selector_(self, selector):
        required_keys = ['source']
        optional_keys = ['as']
        __process_dict__('selector', selector.keys(), required_keys, optional_keys)

        source = selector['source']
        self.source = SelectorSource(source)
        self.az = None if 'as' not in selector.keys() else selector['as']

    def fqn(self):
        return self.source.column.name if self.source.column.table is None else self.source.column.table + '.' + self.source.column.name

    def resolved_reference(self):
        return self.az if self.az is not None else self.fqn()


class SelectorSource:
    def __init__(self, source):
        self.column = None
        self.count = None
        self.sum = None
        self._process_selectorsource_(source)

    def _process_selectorsource_(self, source):
        required_keys = ['column']
        optional_keys = ['count', 'sum']

        __process_dict__('selectorsource', source.keys(), required_keys, optional_keys)
        column = source['column']
        self.column = Column(column)
        self.count = None if 'count' not in source.keys() else source['count']
        self.sum = None if 'sum' not in source.keys() else source['sum']


class Column:
    def __init__(self, column):
        self.name = None
        self.table = None
        self._process_column_(column)

    def __repr__(self):
        return self.name + (':table_' + self.table if self.table is not None else '')

    def _process_column_(self, column):
        required_keys = ['name']
        optional_keys = ['table']

        __process_dict__('column', column.keys(), required_keys, optional_keys)
        self.name = column['name']

        if 'table' in column.keys():
            self.table = column['table']


class From:
    def __init__(self, frome):
        self.source = None
        self.az = None
        self._process_from_(frome)

    def _process_from_(self, frome):
        required_keys = ['source']
        optional_keys = ['as']
        __process_dict__('frome', frome.keys(), required_keys, optional_keys)

        source = frome['source']
        self.source = TableSource(source)
        self.az = frome['as'] if 'as' in frome.keys() else None

    def resolved_reference(self):
        return self.source.file if self.az is None else self.az


class TableSource:
    def __init__(self, source):
        self.file = None
        self._process_tablesource_(source)

    def _process_tablesource_(self, source):
        required_keys = ['file']
        optional_keys = []

        __process_dict__('tablesource', source.keys(), required_keys, optional_keys)
        self.file = source['file']


class Where:
    def __init__(self, where):
        self.op = None
        self.left = None
        self.right = None
        self._process_where_(where)

    def _process_where_(self, where):
        required_keys = ['op', 'left', 'right']
        optional_keys = []

        __process_dict__('where', where.keys(), required_keys, optional_keys)
        if where['op'] not in ['=', '!=', '>', '>=', '<', '<=']:
            print 'Op not valid: ' + where['op']
            exit(255)
        self.op = where['op']

        self.left = Term(where['left'])
        self.right = Term(where['right'])


class Term:
    def __init__(self, term):
        self.type = None
        self.value = None

        self._process_term_(term)

    def _process_term_(self, term):
        if len(term.keys()) > 1:
            print 'Too many values in term'
            exit(255)
        if 'column' in term:
            self.type = 'column'
            self.value = Column(term['column'])
        elif 'lit_int' in term:
            self.type = 'lit_int'
            self.value = term['lit_int']
        elif 'lit_str' in term:
            self.type = 'lit_str'
            self.value = term['lit_str']


class QueryColumn:
    def __init__(self, label, field, table):
        self.label = label
        self.field = field
        self.table = table


def _load_selectors_(selectors):
    results = []
    for sel in selectors:
        selector = Selector(sel)
        results.append(selector)
    return results


def _load_froms_(froms):
    results = []
    for frm in froms:
        frome = From(frm)
        results.append(frome)
    return results


def _load_wheres_(wheres):
    results = []
    for whr in wheres:
        where = Where(whr)
        results.append(where)
    return results


def __create_table_obj__(table):
    file = open(table.source.file + '.table.json', 'r')
    table_label = table.resolved_reference()
    table_data = json.load(file)
    file.close()
    tbl = Table()
    tbl.name = table_label
    tbl.fields = table_data[0]
    tbl.rows = table_data[1:]
    return tbl


def _load_tables_():
    tables = {}
    for tbl in froms:
        table = __create_table_obj__(tbl)
        tables[table.name] = table
    return tables


def _validation_(tables, selectors):
    fields = {}

    for table in tables.values():
        fields[table.name] = table.fields

    columns = set()
    for sel in selectors:
        columns.add(str(sel))
        # check to see if table names exist
        table = sel.source.column.table
        if table is not None:
            if table not in map(lambda x: x.resolved_reference(), froms):
                print 'Table not loaded: ' + table
                exit(255)

    # ambiguous columns
    if len(selectors) > len(columns):
        print 'Ambiguous columns'
        exit(255)

    for selector in selectors:
        table_count = 0
        # for key, data in fields.iteritems():
        # if selector.resolved_reference() in map(lambda x: x[0], fields[key]):
        #     table_count += 1
        if table_count > 1:
            print 'Ambiguous column: ' + selector.resolved_reference()
            exit(255)

    # check for columns that don't exist
    for selector in selectors:
        if selector.source.column.table is not None:
            fields = tables[selector.source.column.table].fields
            if selector.source.column.name not in map(lambda x: x[0], fields):
                print 'Field not found: ' + selector.source.column.name
                exit(255)


def _find_table_(field):
    if field.find('.') > -1:
        return field[0:field.index('.')]
    else:
        for table, flds in fields.iteritems():
            for tfield in map(lambda x: x[0], flds):
                if tfield == field:
                    return table


def _find_index_(table, field):
    for index, tfield in enumerate(fields[table]):
        if field == tfield[0]:
            return index


def _generate_fields_(tables):
    fields = {}
    for table in tables.values():
        fields[table.name] = table.fields
    return fields


def _construct_query_columns_(selectors):
    qcs = []
    for selector in selectors:
        field = selector.source.column.name
        table = _find_table_(selector.fqn())
        qc = QueryColumn(selector.resolved_reference(), field, table)
        qcs.append(qc)
    return qcs


def _select_columns_(query_columns):
    loaded_data = {}
    for qc in query_columns:
        data = tables[qc.table].rows
        loaded_data[qc.label] = data
    return loaded_data


def _detect_joins_and_filters_(wheres):
    joins = []
    filters = []
    for where in wheres:
        if where.left.type == 'column' and where.right.type == 'column':
            joins.append(where)
        else:
            filters.append(where)
    return (joins, filters)


def _filter_data_(tables, filters):
    f_data = {}
    for name, table_data in tables.iteritems():
        f_data[name] = table_data.rows
    for fltr in filters:
        if fltr.left.value.table is None:
            table = _find_table_(fltr.left.value.name)
        else:
            table = fltr.left.value.table
        index = _find_index_(table, fltr.left.value.name)
        data_source = f_data[table][:] if table in f_data else f_data[table]
        if fltr.op == '>':
            filtered_rows = filter(lambda x: x[index] > fltr.right.value, data_source)
        elif fltr.op == '>=':
            filtered_rows = filter(lambda x: x[index] >= fltr.right.value, data_source)
        elif fltr.op == '=':
            filtered_rows = filter(lambda x: x[index] == fltr.right.value, data_source)
        elif fltr.op == '<':
            filtered_rows = filter(lambda x: x[index] < fltr.right.value, data_source)
        elif fltr.op == '<=':
            filtered_rows = filter(lambda x: x[index] <= fltr.right.value, data_source)
        f_data[table] = filtered_rows
    return f_data


## data is the previously generated data which will be re-matched by row number
def __join_data__(join, filtered_data, data=None):
    if data is not None:
        rejoin_tables = []
        for t in tables.keys():
            if t != join.left.value.table and t != join.right.value.table:
                rejoin_tables.append(t)

    # cache of rows, overwritten with each pass
    all_joined_rows = {}
    if join.left.value.table is None:
        ltable_name = _find_table_(join.left.value.name)
    else:
        ltable_name = join.left.value.table

    lindex = _find_index_(ltable_name, join.left.value.name)
    if join.right.value.table is None:
        rtable_name = _find_table_(join.right.value.name)
    else:
        rtable_name = join.right.value.table

    rindex = _find_index_(rtable_name, join.right.value.name)

    # copy rows to transient data sources
    if data is None:
        ldata_source = filtered_data[ltable_name][:]
    else:
        ldata_source = data[ltable_name][:]

    if rtable_name in all_joined_rows:
        rdata_source = all_joined_rows[rtable_name][:]
    else:
        rdata_source = filtered_data[rtable_name][:]

    # overwrite old join results
    all_joined_rows[rtable_name] = []
    all_joined_rows[ltable_name] = []

    # lambda functions handle 1-to-many join
    for row_number, lrow in enumerate(ldata_source):
        if join.op == '>':
            joined_rows = filter(lambda x: lrow[lindex] > x[rindex], rdata_source)
        elif join.op == '>=':
            joined_rows = filter(lambda x: lrow[lindex] >= x[rindex], rdata_source)
        elif join.op == '=':
            joined_rows = filter(lambda x: lrow[lindex] == x[rindex], rdata_source)
        elif join.op == '<':
            joined_rows = filter(lambda x: lrow[lindex] < x[rindex], rdata_source)
        elif join.op == '<=':
            joined_rows = filter(lambda x: lrow[lindex] <= x[rindex], rdata_source)
        if len(joined_rows) > 0:
            for rrow in joined_rows:
                if data is not None:
                    for table in rejoin_tables:
                        if table not in all_joined_rows:
                            all_joined_rows[table] = []
                        all_joined_rows[table].append(data[table][row_number])
                all_joined_rows[rtable_name].append(rrow)

                # create a left entry for every right entry to handle 1-to-many
                all_joined_rows[ltable_name].append(lrow)

    return all_joined_rows


def _join_data_(joins, filtered_data):
    all_joined_rows = {}

    if len(joins) == 0:
        return filtered_data
    else:
        for index, join in enumerate(joins):
            if len(all_joined_rows.keys()) == 0:
                joined_data = None
            else:
                joined_data = all_joined_rows
            for table, results in __join_data__(join, filtered_data, joined_data).iteritems():
                all_joined_rows[table] = results

        return all_joined_rows


def _pivot_results_(fj_data):
    results = []
    for i in range(len(fj_data.values()[0])):
        row = []
        headers = []
        for qc in query_columns:
            headers.append(qc.label)
            row.append(fj_data[qc.table][i][_find_index_(qc.table, qc.field)])
        results.append(row)
    return (headers, results)


def _output_(headers, data):
    print headers
    for row in data:
        print row


# Proceed through the steps
selectors = _load_selectors_(sql['select'])
froms = _load_froms_(sql['from'])
wheres = _load_wheres_(sql['where'])
tables = _load_tables_()
_validation_(tables, selectors)
fields = _generate_fields_(tables)
query_columns = _construct_query_columns_(selectors)
select_data = _select_columns_(query_columns)
(joins, filters) = _detect_joins_and_filters_(wheres)
filtered_data = _filter_data_(tables, filters)
filtered_and_joined_data = _join_data_(joins, filtered_data)
headers, results = _pivot_results_(filtered_and_joined_data)

_output_(headers, results)

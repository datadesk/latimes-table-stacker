#! /usr/bin/env python
"""
This is a Python version of Propublica's TableFu Ruby library.

TableFu parses, sorts and formats table-like streams, like CSVs,
and outputs tables in HTML. It's meant as a utility to make 
getting tabular on the web easier.
"""
__version__ = "0.3.0"
__author__ = "Chris Amico (eyeseast@gmail.com)"


import csv
import math
import urllib2
from table_fu.formatting import format


class TableFu(object):
    """
    A table, to be manipulated like a spreadsheet.
    
    TableFu reads in an open CSV file, parsing it 
    into a table property, Row and Datum objects.
    
    Usage:
    
    # test.csv
    
    Author,Best Book,Number of Pages,Style
    Samuel Beckett,Malone Muert,120,Modernism
    James Joyce,Ulysses,644,Modernism
    Nicholson Baker,Mezannine,150,Minimalism
    Vladimir Sorokin,The Queue,263,Satire
    
    >>> spreadsheet = TableFu(open('../tests/test.csv'))
    >>> len(spreadsheet.rows)
    4
    >>> spreadsheet.columns
    ['Author', 'Best Book', 'Number of Pages', 'Style']
    >>> spreadsheet.columns = ['Style', 'Author']
    >>> spreadsheet.columms
    ['Style', 'Author']
    
    """
    def __init__(self, table, **options):
        """
        Takes a table argument and optional keyword arguments.

        The 'table' argument should be a two-dimensional array,
        either a list or tuple, or an open file that can be
        parsed by Python's csv module (using csv.reader)
        """
        if hasattr(table, 'next'): # for file-like objects
            reader = csv.reader(table)
            self.table = [row for row in reader]
        else:
            self.table = table
        self.default_columns = self.table.pop(0)
        self._columns = options.get('columns', [])
        self.deleted_rows = []
        self.faceted_on = None
        self.totals = {}
        self.formatting = options.get('formatting', {})
        self.style = options.get('style', {})
        self.tags = options.get('tags', [])
        self.per_page = options.get("per_page", 20)
        self.options = options
        if options.has_key('sorted_by'):
            sort_opts = options.get("sorted_by")
            sort_column, sort_direction = sort_opts[0].items()[0]
            direction2reverse = {'ascending': False, 'descending': True}
            sort_reverse = direction2reverse.get(sort_direction, False)
            self.sort(column_name=sort_column, reverse=sort_reverse)
        else:
            self.sorted_by = None

    def __getitem__(self, row_num):
        """
        Return one row in the table
        """
        return Row(self.table[row_num], row_num, self)
    
    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.table)

    def add_rows(self, *rows):
        for row in rows:
            self.table.append(row)
    
    def count(self):
        return len(self)
    
    @property
    def rows(self):
        return [Row(row, i, self) for i, row in enumerate(self.table)]
    
    @property
    def headers(self):
        if self._columns:
            return [Header(col, i, self) for i, col in enumerate(self._columns)]
        else:
            return [Header(col, i, self) for i, col in enumerate(self.default_columns)]
    
    def _get_columns(self):
        if self._columns:
            return self._columns
        return self.default_columns
    
    def _set_columns(self, columns):
        self._columns = self.options['columns'] = list(columns)
    
    columns = property(_get_columns, _set_columns)
    
    def delete_row(self, row_num):
        self.deleted_rows.append(self.table.rows.pop(row_num))
    
    def sort(self, column_name=None, reverse=False):
        """
        Sort rows in this table, preserving a record of how that
        sorting is done in TableFu.options['sorted_by']
        """
        if not column_name and self.options.has_key('sorted_by'):
            column_name = self.options['sorted_by'].keys()[0]
        if column_name not in self.default_columns:
            raise ValueError("%s isn't a column in this table" % column_name)
        index = self.default_columns.index(column_name)
        self.table.sort(key = lambda row: row[index], reverse=reverse)
        self.options['sorted_by'] = {column_name: {'reverse': reverse}}
    
    def values(self, column_name):
        if column_name not in self.default_columns:
            raise ValueError("%s isn't a column in this table" % column_name)
        index = self.default_columns.index(column_name)
        return [row[index] for row in self.table]
    
    def total(self, column_name):
        if column_name not in self.default_columns:
            raise ValueError("%s isn't a column in this table" % column_name)
        try:
            values = [float(v) for v in self.values(column_name)]
        except ValueError:
            raise ValueError('Column %s contains non-numeric values' % column_name)
        return sum(values)
    
    def html(self):
        table = '<table>\n%s\n%s\n</table>'
        thead = '<thead>\n<tr>%s</tr>\n</thead>' % ''.join(['<th>%s</th>' % col for col in self.columns])
        tbody = '<tbody>\n%s\n</tbody>' % '\n'.join([row.as_tr() for row in self.rows])
        return table % (thead, tbody)
    
    def filter(self, func=None, **query):
        """
        Tables can be filtered in one of two ways:
         - Simple keyword arguments return rows where values match *exactly*
         - Pass in a function and return rows where that function evaluates to True
        
        In either case, a new TableFu instance is returned
        """
        if callable(func):
            result = filter(func, self)
            result.insert(0, self.default_columns)
            return TableFu(result, **self.options)
        else:
            result = self
            for column, value in query.items():
                result = result.filter(lambda r: r[column] == value)
            return result

    def facet_by(self, column):
        """
        Faceting creates new TableFu instances with rows matching
        each possible value.
        """
        faceted_spreadsheets = {}
        for row in self.rows:
            if row[column]:
                col = row[column].value
                if faceted_spreadsheets.has_key(col):
                    faceted_spreadsheets[col].append(row.cells)
                else:
                    faceted_spreadsheets[col] = []
                    faceted_spreadsheets[col].append(row.cells)

        # create a new TableFu instance for each facet
        tables = []
        for k, v in faceted_spreadsheets.items():
            v.insert(0, self.default_columns)
            table = TableFu(v)
            table.faceted_on = k
            table.formatting = self.formatting
            table.options = self.options
            tables.append(table)

        tables.sort(key=lambda t: t.faceted_on)
        return tables

    def sorted_by(self):
        """
        Returns an array of numbers that indicate the column and direction to
        sort the table by with the jQuery tablesorter plugin.

        Tablesorter docs:
            An array of instructions for per-column sorting and direction in the 
            format: [[columnIndex, sortDirection], ... ] where columnIndex is a 
            zero-based index for your columns left-to-right and sortDirection is 
            0 for Ascending and 1 for Descending. A valid argument that sorts 
            ascending first by column 1 and then column 2 looks like: [[0,0],[1,0]]

        Source:
            http://tablesorter.com/docs/
        """
        # If it's not sorted, don't worry.
        if not self.options.has_key('sorted_by'):
            return None
        # Otherwise, get the index of the column
        column_name = self.options.get('sorted_by').keys()[0]
        column_index = self.columns.index(column_name)
        # And the sort order
        descending = self.options.get("sorted_by").values()[0].get("reverse")
        if descending:
            sort_direction = 1
        else:
            sort_direction = 0
        # Then nest that in a list to the tablesorter standard
        return [[column_index, sort_direction]]
    
    @property
    def total_pages(self):
        """
        The number of pages the table will be broken into according to the
        `per_page` setting.
        """
        row_count = len(self.rows)
        return int(math.ceil(row_count / float(self.per_page)))
    
    @property
    def page_size_list(self):
        """
        Returns a list of page total choices for the jQuery table.
        """
        row_count = len(self.rows)
        page_size_list = []
        for i in range(1, 5):
            page_size = i * self.per_page
            page_size_list.append(page_size)
            if page_size > row_count:
                break
        return page_size_list


class Row(object):
    """
    A row in a table

    Rows act like dictionaries, but look more like lists.
    Calling row['column'] returns a column lookup based on
    the default set of columns.
    """
    def __init__(self, cells, row_num, table):
        self.table = table
        self.row_num = row_num
        self.cells = list(cells)

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        return self.cells == other.cells

    def __len__(self):
        return len(self.cells)
    
    def update(self, d):
        "Update multiple cell values in place"
        for k, v in d.items():
            self[k] = v
    
    def get(self, column_name, default=None):
        """
        Return the Datum for column_name, or default.
        """
        if column_name in self.table.default_columns:
            index = self.table.default_columns.index(column_name)
            return Datum(self.cells[index], self.row_num, column_name, self.table)
        return default
    
    def keys(self):
        return self.table.columns
    
    def values(self):
        return [d.value for d in self.data]
    
    def items(self):
        return zip(self.keys(), self.values())

    def __getitem__(self, column_name):
        "Get the value for a given cell, or raise KeyError if the column doesn't exist"
        datum = self.get(column_name)
        if datum is None:
            raise KeyError("%s isn't a column in this table" % column_name)
        else:
            return datum
    
    def __setitem__(self, column_name, value):
        """
        Set the value for a given cell
        """
        if not column_name in self.table.default_columns:
            raise KeyError("%s isn't a column in this table" % column_name)
        index = self.table.default_columns.index(column_name)
        self.cells[index] = value
    
    def __iter__(self):
        """
        Iterate over values, *not keys*. Keys are accessible
        as Row.table.columns or Row.keys()
        """
        return iter(self.values())
    
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__str__())

    def __str__(self):
        column_list = [self[column] for column in self.table.columns]
        column_list = map(unicode, column_list)
        column_list = [i.encode("utf-8") for i in column_list]
        return ', '.join(column_list)
    
    def as_tr(self):
        cells = ''.join([d.as_td() for d in self.data])
        return '<tr id="row%s" class="row %s">%s</tr>' % (self.row_num, odd_even(self.row_num), cells)
        
    @property
    def data(self):
        return [self[col] for col in self.table.columns]


class Datum(object):
    """
    A piece of data, with a table, row and column
    """
    def __init__(self, value, row_num, column_name, table):
        self.value = value
        self.row_num = row_num
        self.column_name = column_name
        self.table = table

    def __repr__(self):
        return "<%s: %s>" % (self.column_name, self.value)
        
    def __str__(self):
        """
        Calling str(datum) should check first for a formatted
        version of value, then fall back to the default value
        if there's no set formatting.
        """
        if self.table.formatting.has_key(self.column_name):
            func = self.table.formatting[self.column_name].get('method', None)
            args = self.table.formatting[self.column_name].get('arguments', [])
            kwargs = self.table.formatting[self.column_name].get('options', {})
            if func:
                row = self.table[self.row_num]
                args = [row[arg].value for arg in args]
                return format(self.value, func, *args, **kwargs)
        return self.value.encode('utf-8')
    
    def __eq__(self, other):
        if type(other) == type(self):
            return self.value == other.value
        else:
            return self.value == other
    
    def as_td(self):
        return '<td class="datum">%s</td>' % self.__str__()
    
    def _get_style(self):
        try:
            return self.table.style[self.column_name]
        except KeyError:
            return None
    style = property(_get_style)


class Header(object):
    """
    A header row on a column.
    """
    def __init__(self, name, col_num, table):
        self.name = name
        self.col_num = col_num
        self.table = table

    def __repr__(self):
        return "<Header: %s>" % (self.name)
        
    def __str__(self):
        return self.name.encode('utf-8')
    
    def _get_style(self):
        try:
            return self.table.style[self.name]
        except KeyError:
            return None
    style = property(_get_style)
    
    def as_th(self):
        return '<th class="header" style="%s">%s</th>' % (self.style or '', self.__str__())


def odd_even(num):
    if num % 2 == 0:
        return "even"
    else:
        return "odd"

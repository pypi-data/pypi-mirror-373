# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-06-16 13:49:33
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Table methods.
"""


from typing import Any, TypedDict, Literal, overload
from collections.abc import Collection, MutableMapping
from os.path import abspath as os_abspath
from sqlalchemy.engine.cursor import CursorResult, Row as CursorRow
from pandas import DataFrame, Series, ExcelWriter

from .rbase import Base, throw
from .rdata import to_json
from .ros import File
from .rtext import to_text
from .rtime import time_to


__all__ = (
    'is_row',
    'is_table',
    'Table'
)


type RowData = MutableMapping | CursorRow | Series
type TableData = Collection[MutableMapping] | RowData | CursorResult | DataFrame
SheetSet = TypedDict('SheetsSet', {'name': str, 'index': int, 'fields': str | list[str]})


@overload
def is_row(obj: RowData) -> Literal[True]: ...

@overload
def is_row(obj: Any) -> Literal[False]: ...

def is_row(obj: Any) -> bool:
    """
    Judge whether it is row format.

    Parameters
    ----------
    obj : Ojbect.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    result = isinstance(obj, (MutableMapping, CursorRow, Series))

    return result


@overload
def is_table(obj: TableData) -> bool: ...

@overload
def is_table(obj: Any) -> Literal[False]: ...

def is_table(obj: Any) -> bool:
    """
    Judge whether it is table format, and keys sort of the row are the same.

    Parameters
    ----------
    obj : Ojbect.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    if is_row(obj):
        return True
    if isinstance(obj, (CursorResult, DataFrame)):
        return True
    if isinstance(obj, Collection):
        keys_strs = []
        for row in obj:
            if not isinstance(row, MutableMapping):
                break
            keys_str = ':'.join(row)
            keys_strs.append(keys_str)
        keys_strs = set(keys_strs)
        if len(keys_strs) == 1:
            return True

    return False


class Table(Base):
    """
    Table type.
    """


    def __init__(self, data: TableData) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        data : Data.
        """

        # Set parameter.
        self.data = data


    def to_table(self) -> list[dict]:
        """
        Convert data to `list[dict]` format.

        Returns
        -------
        Converted data.
        """

        # Convert.
        match self.data:
            case MutableMapping():
                result = [dict(self.data)]
            case CursorRow():
                result = [dict(self.data._mapping)]
            case Series():
                result = [dict(self.data.items())]
            case CursorResult():
                result = [
                    dict(row)
                    for row in self.data.mappings()
                ]
            case DataFrame():
                result = self.data.to_dict('records')
            case Collection():
                if not is_table(self.data):
                    text = 'is not table format, or keys sort of the row are the not same'
                    throw(TypeError, text=text)
                result = [
                    dict(row)
                    for row in self.data
                ]

        return result


    @overload
    def to_dict(
        self,
        key_field: int | str = 0
    ) -> dict[Any, dict]: ...

    @overload
    def to_dict(
        self,
        key_field: int | str = 0,
        *,
        val_field: int | str
    ) -> dict: ...

    def to_dict(
        self,
        key_field: int | str = 0,
        val_field: int | str | None = None
    ) -> dict[Any, dict] | dict:
        """
        Convert data as dictionary.

        Parameters
        ----------
        key_field : Key field of dictionary.
            - `int`: Subscript index.
            - `str`: Name index.
        val_field : Value field of dictionary.
            - `None`: All fields except key.
            - `int`: Subscript index.
            - `str`: Name index.

        Returns
        -------
        Dictionary.
        """

        # Handle parameter.
        data = self.to_table()

        # Check.
        if len(data) == 0:
            return {}

        # Get fields.
        fields = list(data[0])
        if type(key_field) == int:
            key_field = fields[key_field]
        if type(val_field) == int:
            val_field = fields[val_field]

        # Convert.

        ## Value is all fields except key.
        if val_field is None:
            data_dict = {
                row[key_field]: {
                    key: value
                    for key, value in row.items()
                    if key != key_field
                }
                for row in data
            }

        ## Value is one field.
        else:
            data_dict = {
                row[key_field]: row[val_field]
                for row in data
            }

        return data_dict


    def to_list(self, field: int | str = 0) -> list:
        """
        Convert data as list.

        Parameters
        ----------
        field : Field of value.
            - `int`: Subscript index.
            - `str`: Name index.

        Returns
        -------
        List.
        """

        # Handle parameter.
        data = self.to_table()

        # Check.
        if len(data) == 0:
            return []

        # Get fields.
        fields = list(data[0])
        if type(field) == int:
            field = fields[field]

        # Convert.
        data_list = [
            row[field]
            for row in data
        ]

        return data_list


    def to_text(self, width: int | None = None) -> str:
        """
        Convert data to text.

        Parameters
        ----------
        width : Format width.
            - `None` : Use terminal display character size.

        Returns
        -------
        Formatted text.
        """

        # Handle parameter.
        data = self.to_table()

        # Convert.
        text = to_text(data, width)

        return text


    def to_json(self, compact: bool = True) -> str:
        """
        Convert data to JSON string.

        Parameters
        ----------
        compact : Whether compact content.

        Returns
        -------
        JSON string.
        """

        # Handle parameter.
        data = self.to_table()

        # Convert.
        string = to_json(data, compact)

        return string


    def to_sql(self) -> str:
        """
        Convert data to SQL string.

        Returns
        -------
        SQL string.
        """

        # Handle parameter.
        data = self.to_table()
        data = [
            {
                key : (
                    repr(time_to(value, raising=False))
                    if bool(value)
                    else 'NULL'
                )
                for key, value in row.items()
            }
            for row in data
        ]

        # Check.
        if len(data) == 0:
            throw(ValueError, data)

        # Generate SQL.
        sql_rows = [
            'SELECT ' + ','.join(row.values())
            for row in data[1:]
        ]
        sql_row_first = 'SELECT ' + ','.join(
            [
                f'{value} AS `{key}`'
                for key, value in data[0].items()
            ]
        )
        sql_rows.insert(0, sql_row_first)
        data_sql = ' UNION ALL '.join(sql_rows)

        return data_sql


    def to_df(self) -> DataFrame:
        """
        Convert data to table of `DataFrame` object.

        Returns
        -------
        DataFrame object.
        """

        # Check.
        if type(self.data) == DataFrame:
            return self.data

        # Handle parameter.
        data = self.to_table()

        # Convert.
        result = DataFrame(data)

        return result


    def to_html(self) -> str:
        """
        Convert data to HTML string.

        Returns
        -------
        HTML string.
        """

        # Handle parameter.
        data = self.to_df()

        # Convert.
        result = data.to_html(col_space=50, index=False, justify='center')

        return result


    def to_csv(self, path: str = 'data.csv') -> str:
        """
        Convert data to save CSV format file.
        When file exist, then append data.

        Parameters
        ----------
        path : File save path.

        Returns
        -------
        File absolute path.
        """

        # Handle parameter.
        data = self.to_df()
        file = File(path)
        if file:
            header = False
        else:
            header = True

        # Save file.
        data.to_csv(file.path, header=header, index=False, mode='a')

        return file.path


    def to_excel(
        self,
        path: str = 'data.xlsx',
        group_field: str | None = None,
        sheets_set: dict[str | int, SheetSet] = {}
    ) -> str:
        """
        Convert data to save Excel format file and return sheet name and sheet data.
        When file exist, then rebuild file.

        Parameters
        ----------
        path : File save path.
        group_field : Group filed.
        sheets_set : Set sheet new name and sort sheet and filter sheet fields,
            key is old name or index, value is set parameters.
            - Parameter `name` : Set sheet new name.
            - Parameter `index` : Sort sheet.
            - Parameter `fields` : Filter sheet fields.

        Returns
        -------
        File absolute path.

        Examples
        --------
        >>> data = [
        ...     {'id': 1, 'age': 21, 'group': 'one'},
        ...     {'id': 2, 'age': 22, 'group': 'one'},
        ...     {'id': 3, 'age': 23, 'group': 'two'}
        ... ]
        >>> sheets_set = {
        ...     'one': {'name': 'age', 'index': 2, 'fields': ['id', 'age']},
        ...     'two': {'name': 'id', 'index': 1, 'fields': 'id'}
        ... }
        >>> to_excel(data, 'file.xlsx', 'group', sheets_set)
        """

        # Handle parameter.
        data = self.to_df()
        path = os_abspath(path)

        # Generate sheets.
        if group_field is None:
            data_group = (('Sheet1', data),)
        else:
            data_group = data.groupby(group_field)
        sheets_table_before = []
        sheets_table_after = []
        for index, sheet_table in enumerate(data_group):
            sheet_name, sheet_df = sheet_table
            if group_field is not None:
                del sheet_df[group_field]
            if sheet_name in sheets_set:
                sheet_set = sheets_set[sheet_name]
            elif index in sheets_set:
                sheet_set = sheets_set[index]
            else:
                sheets_table_after.append((sheet_name, sheet_df))
                continue
            if 'name' in sheet_set:
                sheet_name = sheet_set['name']
            if 'fields' in sheet_set:
                sheet_df = sheet_df[sheet_set['fields']]
            if 'index' in sheet_set:
                sheets_table_before.append((sheet_set['index'], (sheet_name, sheet_df)))
            else:
                sheets_table_after.append((sheet_name, sheet_df))
        sort_func = lambda item: item[0]
        sheets_table_before.sort(key=sort_func)
        sheets_table = [sheet_table for sheet_index, sheet_table in sheets_table_before] + sheets_table_after

        # Save file.
        excel = ExcelWriter(path)
        for sheet_name, sheet_df in sheets_table:
            sheet_df.to_excel(excel, sheet_name, index=False)
        excel.close()

        return path

# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-03-19 19:36:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Monkey patch methods.
"""


from __future__ import annotations


__all__ = (
    'monkey_sqlalchemy_result_more_fetch',
    'monkey_sqlalchemy_row_index_field',
    'monkey_pprint_modify_width_judgment'
)


def monkey_sqlalchemy_result_more_fetch():
    """
    Monkey patch of package `sqlalchemy`, add more fetch methods to `CursorResult` object.

    Returns
    -------
    Modified type.

    Examples
    --------
    >>> result = connection.execute(sql)
    >>> result.to_table()
    >>> result.to_dict()
    >>> result.to_list()
    >>> result.to_df()
    >>> result.to_json()
    >>> result.to_text()
    >>> result.to_sql()
    >>> result.to_html()
    >>> result.to_csv()
    >>> result.to_excel()
    >>> result.show()
    >>> result.exist
    >>> result.empty
    """

    # Import.
    from typing import Self
    from types import MethodType
    from sqlalchemy.engine.cursor import CursorResult
    from pandas import DataFrame, NA, concat
    from .rbase import Base
    from .rstdout import echo
    from .rtable import Table
    from .rtime import time_to


    # Add.
    @property
    def method_data(self: Result) -> Self:
        """
        Get Data.

        Returns
        -------
        Self.
        """

        return self


    CursorResult.data = method_data
    CursorResult.to_table = Table.to_table
    CursorResult.to_dict = Table.to_dict
    CursorResult.to_list = Table.to_list
    CursorResult.to_text = Table.to_text
    CursorResult.to_json = Table.to_json
    CursorResult.to_sql = Table.to_sql
    CursorResult.to_df = Table.to_df
    CursorResult.to_html = Table.to_html
    CursorResult.to_csv = Table.to_csv
    CursorResult.to_excel = Table.to_excel


    def method_show(self: Result, limit: int | None = None) -> None:
        """
        Print result.

        Parameters
        ----------
        limit : Limit row.
            - `>0`: Limit first few row.
            - `<0`: Limit last few row.
        """

        # Handle parameter.
        limit = limit or 0

        # Convert.
        df: DataFrame = self.to_df()
        df = df.map(time_to, raising=False)
        df = df.astype(str)
        df.replace(['NaT', '<NA>'], 'None', inplace=True)
        row_len, column_len = df.shape

        # Create omit row.
        omit_row = (('...',) * column_len,)
        omit_row = DataFrame(
            omit_row,
            columns=df.columns
        )

        # Limit.
        if (
            limit > 0
            and limit < row_len
        ):
            df = df.head(limit)
            omit_row.index = (row_len - 1,)
            df = concat((df, omit_row))
        elif (
            limit < 0
            and -limit < row_len
        ):
            df = df.tail(-limit)
            omit_row.index = (0,)
            df = concat((omit_row, df))

        # Print.
        echo(df, title='Result')


    CursorResult.show = method_show


    @property
    def method_exist(self: Result) -> bool:
        """
        Judge whether is exist row.

        Returns
        -------
        Judge result.
        """

        # Judge.
        judge = self.rowcount != 0

        return judge


    CursorResult.exist = method_exist


    @property
    def method_empty(self: Result) -> bool:
        """
        Judge whether is empty row.

        Returns
        -------
        Judge result.
        """

        # Judge.
        judge = self.rowcount == 0

        return judge


    CursorResult.empty = method_empty


    # Update annotations.
    class Result(Base, CursorResult):
        """
        Update based on `CursorResult` object, for annotation return value.
        """

        # Inherit document.
        __doc__ = CursorResult.__doc__

        # Add method.
        to_table = Table.to_table
        to_dict = Table.to_dict
        to_list = Table.to_list
        to_text = Table.to_text
        to_json = Table.to_json
        to_sql = Table.to_sql
        to_df = Table.to_df
        to_html = Table.to_html
        to_csv = Table.to_csv
        to_excel = Table.to_excel
        show = method_show
        exist = method_exist
        empty = method_empty


    return Result


def monkey_sqlalchemy_row_index_field():
    """
    Monkey patch of package `sqlalchemy`, add index by field method to `Row` object.

    Examples
    --------
    >>> result = connection.execute(sql)
    >>> for row in result:
    ...     row['field']
    """

    # Import.
    from typing import Any, overload
    from sqlalchemy.engine.row import Row

    # Define.
    @overload
    def __getitem__(self, index: str | int) -> Any: ...

    @overload
    def __getitem__(self, index: slice) -> tuple: ...

    def __getitem__(self, index: str | int | slice) -> Any | tuple:
        """
        Index row value.

        Parameters
        ----------
        index : Field name or subscript or slice.

        Returns
        -------
        Index result.
        """

        # Index.
        if type(index) == str:
            value = self._mapping[index]
        else:
            value = self._data[index]

        return value


    # Add.
    Row.__getitem__ = __getitem__


def monkey_pprint_modify_width_judgment() -> None:
    """
    Monkey patch of package `pprint`, modify the chinese width judgment.
    """

    # Import.
    from pprint import PrettyPrinter, _recursion


    # Define.
    def __format(_self, obj, stream, indent, allowance, context, level):

        from .rtext import get_width

        objid = id(obj)
        if objid in context:
            stream.write(_recursion(obj))
            _self._recursive = True
            _self._readable = False
            return
        rep = _self._repr(obj, context, level)
        max_width = _self._width - indent - allowance
        width = get_width(rep)
        if width > max_width:
            p = _self._dispatch.get(type(obj).__repr__, None)
            if p is not None:
                context[objid] = 1
                p(_self, obj, stream, indent, allowance, context, level + 1)
                del context[objid]
                return
            elif isinstance(obj, dict):
                context[objid] = 1
                _self._pprint_dict(obj, stream, indent, allowance,
                                context, level + 1)
                del context[objid]
                return
        stream.write(rep)


    # Modify.
    PrettyPrinter.__format = __format


def monkey_path_pil_image_get_bytes():
    """
    Monkey patch of package `PIL`, add get bytes method to `Image` object.

    Returns
    -------
    Image object.

    Examples
    --------
    >>> image = to_pil_image(source)
    >>> image.get_bytes()
    """

    from PIL.Image import Image
    from io import BytesIO
    from .rbase import Base


    # Define.
    def method_get_bytes(self: Image) -> bytes:
        """
        Get image bytes data.

        Returns
        -------
        Image bytes data.
        """

        # Extract.
        bytes_io = BytesIO()
        self.save(bytes_io, 'JPEG')
        image_bytes = bytes_io.getvalue()

        return image_bytes


    # Add.
    Image.get_bytes = method_get_bytes


    # Update annotations.
    class Image(Base, Image):
        """
        Update based on `Image` object, for annotation return value.
        """

        # Inherit document.
        __doc__ = Image.__doc__

        # Add method.
        get_bytes = method_get_bytes


    return Image

from json import loads
from typing import Any, Union

from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is, Are
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


def _check_path(path):
    if path.get_label() == 'const' and not path.meta.startswith('$'):
        raise ValueError('json path must start with \'$\', e.g. \'$.A.B[1]\'')


class JsonFnAccessor(BaseFnAccessor):

    def __init__(self, column: Column):
        super().__init__('json', column, Is.any)

    def __assert_self_text(self, name):
        if not Is.text(self._column):
            raise AttributeError(f'To use {name} the column {Is.text.msg} type, but was {self._column.dtype.name}.')

    def format(self) -> Column:
        """Converts a string to cleaned-up JSON with whitespace removed. If it's not valid JSON the function will error.

        Notes:
            https://www.sqlite.org/json1.html#jmini

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.format()')
        fn = lambda x: f'json({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.json.array_len()')
    def array_len(self, path: Union[str, Column]) -> Column:
        """Computes the length of an array at the given path.

        Args:
            path (Union[str, Column]): the path within the json to find the array.

        Notes:
            https://www.sqlite.org/json1.html#jarraylen

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.array_len()')
        _check_path(path)
        fn = lambda x, y: f'json_array_length({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, path), dtype=DType.Int, label='func')

    @input_constraints(..., Is.text, name='.json[]')
    def __getitem__(self, path: Union[str, Column]) -> Column:
        self.__assert_self_text('.json[]')
        _check_path(path)
        fn = lambda x, y: f'json_extract({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, path), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, Is.any, name='.json.insert()')
    def insert(self, path: Union[str, Column], value: Any) -> Column:
        """Insert a value into the JSON at a given path.

        Args:
            path (Union[str, Column]): the path within the json to use.
            value (Any): the value to insert.

        Notes:
            https://www.sqlite.org/json1.html#jins

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.insert()')
        _check_path(path)
        fn = lambda x, y, z: f'json_insert({x.sql}, {y.sql}, {z.sql})'
        return Column(fn=fn, parents=(self._column, path, value), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.json.patch()')
    def patch(self, patch: Union[str, Column]) -> Column:
        """Applies a patch of json to an existing json.

        Args:
            patch (Union[str, Column]): json str to patch into the given json.

        Notes:
            https://www.sqlite.org/json1.html#jpatch

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.patch()')
        if patch.get_label() == 'const':
            # check string literal is valid json
            loads(patch.meta)
        fn = lambda x, y: f'json_patch({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, patch), dtype=DType.Text, label='func')

    def quote(self) -> Column:
        """Converts a SQL value to its json equivalent value.

        Notes:
            https://www.sqlite.org/json1.html#jquote

        Returns:
            Columns: the column instance representing the result of this function.

        """
        fn = lambda x: f'json_quote({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Text, label='func')

    @input_constraints(..., Are.all_text, name='.json.remove()')
    def remove(self, *paths: Union[str, Column]) -> Column:
        """Removes one or more paths from a given json.

        Args:
            *paths (Union[str, Column]): the paths within the json to remove.

        Notes:
            https://www.sqlite.org/json1.html#jrm

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.remove()')
        for path in paths:
            _check_path(path)
        fn = lambda *xs: f'json_remove({", ".join(x.sql for x in xs)})'
        return Column(fn=fn, parents=(self._column,) + paths, dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.json.type()')
    def type(self, path: Union[str, Column]) -> Column:
        """Returns the type of the element found at the given path in the json.

        Args:
            path (Union[str, Column]): the path within the json to find the type.

        Notes:
            https://www.sqlite.org/json1.html#jtype

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.type()')
        _check_path(path)
        fn = lambda x, y: f'json_type({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, path), dtype=DType.Text, label='func')

    def valid(self) -> Column:
        """Returns whether the column value is valid json.

        Notes:
            https://www.sqlite.org/json1.html#jvalid

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.valid()')
        fn = lambda x: f'json_valid({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Boolean, label='func')

    def group_array(self) -> Column:
        """Aggregates the values in a column into a single json array.

        Notes:
            https://www.sqlite.org/json1.html#jgrouparray

        Returns:
            Columns: the column instance representing the result of this function.

        """
        fn = lambda x: f'json_group_array({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Text, label='aggfunc')

    @input_constraints(..., Is.any, name='.json.group_object()')
    def group_object(self, values: Column) -> Column:
        """Aggregates a column of labels and another column into a json object where each label value is the key and
        each element of the other column is the value.

        Args:
            values (Column): the other column corresponding to the json object's field values.

        Notes:
            https://www.sqlite.org/json1.html#jgroupobject

        Returns:
            Columns: the column instance representing the result of this function.

        """
        self.__assert_self_text('.json.group_object()')
        fn = lambda x, y: f'json_group_object({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, values), dtype=DType.Text, label='aggfunc')


class JsonStatic:

    @input_constraints(..., Are.any, name='json.array()')
    def array(self, *args: Column) -> Column:
        """Assemble a collection of values and columns into a json array.

        Args:
            *args (Column): the values to put into the array.

        Notes:
            https://www.sqlite.org/json1.html#jarray

        Returns:
            Columns: the column instance representing the result of this function.

        """
        fn = lambda *xs: f'json_array({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=args, dtype=DType.Text, label='func')

    def object(self, **kwargs: Column) -> Column:
        """Assemble a collection of key-value pairs into a json object.

        Args:
            **kwargs (Column): Each keyword key is the name to be used and each arg is the associated value.

        Notes:
            https://www.sqlite.org/json1.html#jobj

        Returns:
            Columns: the column instance representing the result of this function.

        """

        inputs = []
        for k, v in kwargs.items():
            inputs.append(make(k))
            inputs.append(make(v))

        fn = lambda *xs: f'json_object({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=tuple(inputs), dtype=DType.Text, label='func')


json = JsonStatic()

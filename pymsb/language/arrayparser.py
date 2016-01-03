from collections import OrderedDict

# TODO: improve efficiency


class ArrayParser:
    def __init__(self):
        pass

    def array_to_ordered_dict(self, array, follow_nested=False):
        """
        Converts an MSB array string into a Python OrderedDict.
        :param array: The MSB array string.
        :param follow_nested: If set to False, then nested arrays will not be evaluated into nested OrderedDicts.
        :return: An OrderedDict representing the given array.
        """
        od = OrderedDict()
        for key, value in self.iter_items(array):
            if follow_nested and self.is_array(value):
                value = self.array_to_ordered_dict(self.__unescape(value))
            od[key] = value
        return od

    def ordered_dict_to_array(self, od):
        """Converts an OrderedDict into an MSB array string."""
        return self.__encode(od, 0)

    def list_to_array(self, lst):
        """Converts a Python list of strings/numbers into a one-dimensional MSB array with indices beginning from 1."""
        return self.ordered_dict_to_array(dict(enumerate(lst, start=1)))

    def contains_index(self, array, index):
        for key, _ in self.iter_items(array):
            if key == index:
                return True
        return False

    def contains_value(self, array, value):
        for _, val in self.iter_items(array):
            if val == value:
                return True
        return False

    def get_all_indices(self, array):
        return self.list_to_array(self.array_to_ordered_dict(array, follow_nested=False).keys())

    def get_length(self, array):
        return str(len(set(key for key, _ in self.iter_items(array))))

    def is_array(self, array):
        for _ in self.iter_items(array):
            return True
        return False

    def iter_items(self, array_string):
        """
        Returns a generator over the key-value pairs of the given MSB array.
        If a key appears multiple times in the array, then the key will appear multiple times in the iterator.
        Sub-arrays of the MSB array will appear as their string values, rather than being expanded.
        """
        index = 0
        try:
            while index < len(array_string):
                # Get a key, value pair.
                seek_index = index
                # Get key
                while True:
                    letter = array_string[seek_index]
                    if letter == "\\":
                        seek_index += 2
                    elif letter == "=" or letter == ";":
                        break
                    else:
                        seek_index += 1
                key = self.__unescape(array_string[index:seek_index])
                index = seek_index + 1
                seek_index = index
                # Get value
                while True:
                    letter = array_string[seek_index]
                    if letter == "\\":
                        seek_index += 2
                    elif letter == "=" or letter == ";":
                        break
                    else:
                        seek_index += 1
                value = self.__unescape(array_string[index:seek_index])
                yield (key, value)
        except IndexError:
            return

    def __encode(self, value, dimension):
        """
        :param value: A string or OrderedDict.
        :param dimension: The number of dimensions deep (e.g. 1 for a one-dimensional array)
        :return: The string representing the given value.
        """
        if isinstance(value, OrderedDict):
            items = ('{0}={1}'.format(self.__escape(k, dimension),
                                      self.__escape(self.__encode(v, dimension), dimension + 1))
                     for k, v in value.items())
            return ";".join(items) + ';'  # TODO: figure out how to efficiently append the comma

        if isinstance(value, str):
            return value

    def __escape(self, string, dimension):
        escape = "\\" * dimension
        return string.replace("\\", escape + "\\").replace("=", escape + "=").replace(";", escape + ";")

    def __unescape(self, string):
        lst = list(string)
        index = 0
        while index < len(lst):
            # If we find a backslash, remove it.  If a backslash immediately follows it, we include it.
            if lst[index] == "\\":
                lst.pop(index)
                if lst[index] == "\\":
                    index += 1
            else:
                index += 1
        return "".join(lst)

    def get_value(self, array_string, index_values):
        """
        Takes an array string, a list of zero or more index strings, and returns the value located at the specified
        location.  If the value cannot be found, then the empty string is returned.
        :param array_string: A string representing an MSB array.
        :param index_values: The index/indices being used to specify the location in the array.
        :return: The value at the specified location in the array.
        """

        value = ""
        for index_value in index_values:
            od = self.array_to_ordered_dict(array_string)
            value = od.get(index_value, None)
            if value is None:
                return ""
            array_string = value

        return value

    def set_value(self, array_string, index_values, value):
        """
        Takes an array string, a list of zero or more index strings, and a value, and returns the string representing
        the given array after it has been updated with the new value.

        If there are no indices, then this returns the value itself.

        If array_string does not represent a valid MSB array, then the previous contents of array_string will be
        removed.  Duplicate keys and invalid portions of the array string will only be removed if they are contained at
        depth 1 or in a sub-array that is accessed by index_values.

        :param array_string: A string representing an MSB array.
        :param index_values: The index/indices being used to specify the location in the array.
        :param value: The string representing the new value at the given location.
        :return: The string representing the MSB array updated with the new value.
        """
        new_array_dict = self.__set_value_recursion(array_string, index_values, value, 0)
        return self.ordered_dict_to_array(new_array_dict)

    def __set_value_recursion(self, array_string, index_values, value, index_number):
        if index_number >= len(index_values):
            return value

        od = self.array_to_ordered_dict(array_string)
        ind = index_values[index_number]
        od[ind] = self.__set_value_recursion(self.__unescape(od.get(ind, "")), index_values, value, index_number + 1)
        return self.ordered_dict_to_array(od)

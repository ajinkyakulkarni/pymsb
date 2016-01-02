# noinspection PyPep8Naming


class Array:
    '''
    The implementation of the MSB Array module.
    GetValue, RemoveValue and SetValue appear to be deprecated, in favour of using square-bracket arrays.
    The remaining methods in the Array module are separate from GetValue, RemoveValue, and SetValue and operate on
    square-bracket arrays.
    '''
    def __init__(self, array_parser):
        self.array_parser = array_parser

        # For GetValue, RemoveValue and SetValue.
        self.internal_arrays = {}

    def ContainsIndex(self, array, index):
        return str(self.array_parser.contains_index(array, index))

    def ContainsValue(self, array, value):
        return str(self.array_parser.contains_value(array, value))

    def GetAllindices(self, array):
        return self.array_parser.get_all_indices(array)

    def GetItemCount(self, array):
        return self.array_parser.get_item_count(array)

    def IsArray(self, array):
        return str(self.array_parser.is_array(array))

    # GetValue, RemoveValue and SetValue make use of internal mappings stored in the Array module itself,
    # are entirely separate from the methods that appear above, and do not use ArrayParser.

    def GetValue(self, array_name, index):
        arr = self.internal_arrays.get(array_name, None)
        if arr:
            return arr.get(index, "")

    def RemoveValue(self, array_name, index):
        arr = self.internal_arrays.get(array_name, None)
        if arr:
            arr.pop(index, None)

    def SetValue(self, array_name, index, value):
        self.internal_arrays.setdefault(array_name, {})[index] = value

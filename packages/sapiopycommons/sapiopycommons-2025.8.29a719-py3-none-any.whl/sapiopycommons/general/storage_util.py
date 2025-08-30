class StorageUtil:
    """
    A collection of utilities intended for converting to and from various forms of representing positions on a storage
    unit, such as character + integer (e.g. A1), two integers (e.g. (0, 0)), or a single integer index (e.g. 1).
    Integers are also sometimes zero-indexed and sometimes one-indexed, so both are supported.
    """
    @staticmethod
    def map_index_to_coordinate(index: int, size: int, fill_by_row: bool = True, zero_indexed_input: bool = False,
                                zero_indexed_output: bool = False, char_row_output: bool = True) \
            -> tuple[int | str, int]:
        """
        Convert an index representing a position on a plate/storage unit to a coordinate pair on that plate/storage
        unit, able to be used in row/column storage fields on records. This will output a value for any input index;
        it is up to the caller to determine if the output will actually fit on the plate/storage unit.
        (The index should be within the range [1 < index < rows * columns] for one-indexed values.)

        By default, expects the input to be a one-indexed integer filled row-by-row with the output being a
        character, integer pair where the output integer is one-indexed.

        :param index: The index to map to a coordinate position.
        :param size: The number of columns or rows in the plate/storage unit, depending on whether you are filling by
            row or by column.
        :param fill_by_row: If true, map positions row-by-row (A1, A2, A3... B1, B2...) and use the above size as the
            number of columns in the plate/storage unit. If false, map positions column-by-column (A1, B1, C1... A2,
            B2...) and use the above size as the number of rows.
        :param zero_indexed_input: If true, the input index is zero-indexed. If false, then they are one-indexed.
            This does not influence the output, only the function's understanding of the input.
        :param zero_indexed_output: If true, the output index is zero-indexed. If false, then it is one-indexed.
            Has no effect on the column output if the column is set to output as a character.
        :param char_row_output: If true, the output row value is converted to a character where 0 = A, 1 = B, 25 = Z,
            26 = AA, 27 = AB, etc. If false, then it is returned as an integer.
        :return: A tuple representing a coordinate pair (row value, column value). The row value may be either an
            integer or a string, while the column value is always an integer, influenced by the input parameters.
        """
        # If the given index isn't zero-indexed, then make it zero-indexed by subtracting one.
        if not zero_indexed_input:
            index -= 1

        row: int = index // size
        col: int = index % size

        # If fill by row is false, then the above calculations are flipped,
        # meaning the row is actually the column and vice versa.
        if not fill_by_row:
            temp = row
            row = col
            col = temp
        # The column and row are zero-indexed by default. If it should be one-indexed, add one.
        if not zero_indexed_output:
            col += 1
            # Only add one to the row if it won't be converted to a character.
            if not char_row_output:
                row += 1
        return StorageUtil.map_index_to_char(row, True) if char_row_output else row, col

    @staticmethod
    def map_coordinate_to_index(row: int | str, col: int | str, size: int, fill_by_row: bool = True,
                                zero_indexed_input: bool = False, zero_indexed_output: bool = False) -> int:
        """
        Map row and column coordinates on a plate/storage unit to the index of that position.

        By default, expects the input to be provided as a character, integer pair and outputs a single row-by-row
        one-indexed integer.

        :param row: The row coordinate of the position as a string of characters from A-Z or a zero-indexed integer.
        :param col: The column coordinate of the position as an integer which may be zero-indexed or one-indexed.
            (This integer may be in string form, such as is the case with column fields on storable records.)
        :param size: The number of columns or rows in the plate/storage unit, depending on whether you are filling by
            row or by column.
        :param fill_by_row: If true, map positions row-by-row (A1, A2, A3... B1, B2...) and use the above size as the
            number of columns in the plate/storage unit. If false, map positions column-by-column (A1, B1, C1... A2,
            B2...) and use the above size as the number of rows.
        :param zero_indexed_input: If true, the input coordinates for the row and column is zero-indexed. If false,
            then they are one-indexed. This does not influence the output, only the function's understanding of the
            input. This also has no effect if the input row is a string.
        :param zero_indexed_output: If true, the output index is zero-indexed. If false, then it is one-indexed.
        :return: The index of the storage position at the input row and column.
        """
        # If the column was provided as a string, cast it to an int.
        if isinstance(col, str):
            col: int = int(col)
        # If the input isn't zero-indexed, then make it zero-indexed.
        if not zero_indexed_input:
            col -= 1
            # Only subtract from the row if it's already in integer form.
            # If it's a string, it'll be converted to a zero-indexed integer.
            if isinstance(row, int):
                row -= 1
        # If the input row is a string, convert it to a zero-indexed integer.
        if isinstance(row, str):
            row: int = StorageUtil.map_char_to_index(row, True)

        # Convert the row and column indices to a singular index across the entire storage unit.
        index: int = row * size + col if fill_by_row else col * size + row

        # The index is zero-indexed by default. If it should be one-indexed, add one.
        if not zero_indexed_output:
            index += 1
        return index

    @staticmethod
    def map_index_to_char(index: int, zero_indexed_input: bool = False) -> str:
        """
        Map a given base-10 integer to a base-26 value where 0 = A, 1 = B, 25 = Z, 26 = AA, 27 = AB, etc.
        Useful for mapping the index of a row to the character(s) representing that row in a storage unit.
        May also be used for mapping the index to an Excel sheet's columns.

        By default, expects the input as a one-indexed value.

        :param index: The index to map to a character.
        :param zero_indexed_input: If true, the input index is zero-indexed. If false, then they are one-indexed.
            This does not influence the output, only the function's understanding of the input.
        :return: The input integer mapped to a string representing that integer's position.
        """
        # If the given index isn't zero-indexed, then make it zero-indexed by subtracting one.
        if not zero_indexed_input:
            index -= 1
        chars: str = ""
        while index >= 0:
            # Add new characters to the front of the string.
            chars = chr(ord("A") + index % 26) + chars
            # Reduce the index by the amount accounted for by the character that was just added.
            index = index // 26 - 1
        return chars

    @staticmethod
    def map_char_to_index(chars: str, zero_indexed_output: bool = False) -> int:
        """
        Map a given base-26 value of characters to a base-10 integer where A = 0, B = 1, Z = 25, AA = 26, AB = 27, etc.
        Useful for mapping the character(s) representing a row in a storage unit to that row's index.
        May also be used for mapping the index of an Excel sheet's columns.

        By default, provides the output as a one-indexed value.

        :param chars: A string of characters to be converted to an index. Characters are expected to be uppercase
            characters in the range A to Z.
        :param zero_indexed_output: If true, the output index is zero-indexed. If false, then it is one-indexed.
        :return: The input character(s) converted to an index.
        """
        # Reverse iterate over the characters of the string and determine the value of each individual character.
        # The value is multiplied by the base of the character given its digit position (26^0, 26^1, etc.)
        value: int = 0
        for i, c in enumerate(reversed(chars)):
            value += (ord(c) - ord("A") + 1) * (26 ** i)
        # The character value is one-indexed by default. If it should be zero-indexed, subtract one.
        if zero_indexed_output:
            value -= 1
        return value

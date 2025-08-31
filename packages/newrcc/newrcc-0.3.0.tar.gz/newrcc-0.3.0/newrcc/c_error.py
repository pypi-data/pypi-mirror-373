__all__ = [
    'CDColorUndefinedError',
    'CDUnexpectedColorInputError',
    'CDTableBlockCountMismatchedError'
]


class _CDError(Exception):
    def __init__(self, msg: str):
        super().__init__(f'[CDError]: {msg}')


class CDColorUndefinedError(_CDError):
    def __init__(self, undefined_color):
        super().__init__(f'This color is undefined in CD standard color set. -> [{str(undefined_color)}]')


class CDUnexpectedColorInputError(_CDError):
    def __init__(self, unexpected_color, input_func: str):
        super().__init__(
            f'This color is an unexpected input for this function. [{str(unexpected_color)}] -> [{input_func}]')


class CDTableBlockCountMismatchedError(_CDError):
    def __init__(self, wrong_row, right_length):
        super().__init__(f'This table row\'s block count mismatched with other rows. {wrong_row} -> {right_length}')

class ComplexItemDTO:
    type: str
    arg_offset: int
    n_args: int

    def __init__(self, type: str, arg_offset: int, n_args: int):
        self.type = type
        self.arg_offset = arg_offset
        self.n_args = n_args
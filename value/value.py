class Value:

    def __bytes__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

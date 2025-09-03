
class VarNameRecord:
    """Singleton for keeping track of and making variable names.

    """

    def __init__(self):
        self.records = {}

    def make_name(self, var_name, var):

        varh = hash(var)

        if var_name not in self.records:
            self.records[var_name] = {varh: 1}

        d = self.records[var_name]

        if varh not in d:
            self.records[var_name][varh] = len(d) + 1

        return f'{var_name}_{self.records[var_name][varh]}'


record = VarNameRecord()

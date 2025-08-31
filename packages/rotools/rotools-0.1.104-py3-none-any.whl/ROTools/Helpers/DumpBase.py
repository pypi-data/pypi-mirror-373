class DumpBase(object):

    def dump(self, indent_level=0):
        sp = "  " * indent_level

        for k, value in self.__dict__.items():
            if isinstance(value, DumpBase):
                print(f"{sp}{k}:")
                value.dump(indent_level + 1)
                continue

            if isinstance(value, list) and all([isinstance(a, DumpBase) for a in value]):
                print(f"{sp}{k}:")
                for sub_value in value:
                    sub_value.dump(indent_level + 1)  # todo fix it. list display
                continue

            print(f"{sp}{k:<22}: {value}")

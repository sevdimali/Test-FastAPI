class API_functools:

    @classmethod
    def get_or_default(cls, list_el, index, default):
        if len(list_el) <= index:
            return default

        return list_el[index]

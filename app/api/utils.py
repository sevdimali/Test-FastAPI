class API_functools:

    @classmethod
    def get_or_default(cls, list_el, index, default):
        if len(list_el) <= index:
            return default

        return list_el[index]

    @classmethod
    def instance_of(cls, el, class_expected):
        return el.__class__.__name__.lower() == class_expected.__name__.lower()

from collections import OrderedDict

class Results(object):
    def __init__(self):
        self.__dict__['_dict'] = OrderedDict()

    def __getattr__(self, key):
        return self._dict[key]

    def __setattr__(self, key, val):
        self._dict[key] = val

    def asdict(self):
        return self._dict

    def results(self):
        res = []
        for k, v in self._dict.items():
            res.append('%s: %s' % (k, v))
        return '\n'.join(res)



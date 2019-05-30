import json
import os


class Config:
    USER_DIR = os.path.expanduser('~')
    CONFIG_FILE = os.path.join(USER_DIR, '.bakker/config.json')

    def __init__(self):
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def _save(self):
        if not os.path.exists(os.path.dirname(self.CONFIG_FILE)):
            os.makedirs(os.path.dirname(self.CONFIG_FILE))
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def __setitem__(self, key, value):
        assert isinstance(value, str)

        keys = key.split('.')
        current = self.config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        self._save()

    def __getitem__(self, key):
        keys = key.split('.')
        current = self.config
        for key in keys:
            current = current[key]
        if not isinstance(current, str):
            raise KeyError()
        return current

    def __delitem__(self, key):
        def del_dict_item(d, keys):
            if len(keys) > 1:
                del_dict_item(d[keys[0]], keys[1:])
                if len(d[keys[0]]) == 0:
                    del d[keys[0]]
            else:
                del d[keys[0]]

        keys = key.split('.')
        del_dict_item(self.config, keys)

    def items(self):
        def build_items(d, prefix):
            for key, value in d.items():
                next_prefix = prefix + '.' + key if prefix is not None else key
                if isinstance(value, dict):
                    yield from build_items(value, next_prefix)
                elif isinstance(value, str):
                    yield next_prefix, value
        return build_items(self.config, None)

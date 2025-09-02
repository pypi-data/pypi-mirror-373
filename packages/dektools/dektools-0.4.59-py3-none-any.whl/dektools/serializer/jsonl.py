import json
from .base import SerializerBase
from ..file import iter_file_obj_lines


class Jsonl(SerializerBase):
    def _load_file(self, file, kwargs):
        result = []
        for line in iter_file_obj_lines(file):
            if line:
                if not line.startswith('//'):
                    result.append(json.loads(line))
        return result

    def _dump_file(self, obj, file, kwargs):
        kwargs.update({
            'ensure_ascii': False,
            'indent': None,
            'separators': (',', ':')
        })
        file.write('\n'.join(json.dumps(item, **kwargs) for item in obj))


jsonl = Jsonl()

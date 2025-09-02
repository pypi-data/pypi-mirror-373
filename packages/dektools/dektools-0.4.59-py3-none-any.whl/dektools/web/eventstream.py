import json


class EventStreamReaderException(Exception):
    pass


class EventStreamReader:
    def __init__(self):
        self._buffer = ''
        self._items = []

    async def put(self, s):
        self._buffer += s
        await self.on_put(False)

    async def on_put(self, end):
        raise NotImplementedError

    async def pop(self):
        items = self._items
        self._items = []
        for item in items:
            yield item

    async def end(self):
        if self._buffer:
            await self.on_put(True)
        async for item in self.pop():
            yield item
        if self._buffer:
            raise EventStreamReaderException(f'Expect empty buffer: {self._buffer}')
        async for item in self.on_end():
            yield item

    async def on_end(self):
        if False: yield  # noqa

    async def fail(self):
        if False: yield  # noqa


class EventStreamReaderGeneric(EventStreamReader):
    data_marker = 'data:'
    lines_sep = '\n\n'
    skip_value = object()

    async def on_put(self, end):
        s = self._buffer
        while s:
            index = s.find(self.lines_sep)
            if index == -1:
                if end:
                    index = len(s) + 1
                else:
                    break
            item = s[:index]
            data = json.loads(item[len(self.data_marker):])
            item = await self._translate_item(data)
            if item is not self.skip_value:
                self._items.append(item)
            s = s[index + len(self.lines_sep):]
        self._buffer = s

    async def _translate_item(self, item):
        return item

from collections import defaultdict

from harmonize.connection.cache.dll import DLL
from harmonize.connection.cache.nodes import DLLNode, DataNode
from harmonize.objects import MISSING

__all__ = (
    "LFUCache",
)


class LFUCache:
    def __init__(self, *, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[any, DataNode] = {}

        self._freq_map: defaultdict[int, DLL] = defaultdict(DLL)
        self._min: int = 1
        self._used: int = 0

    def __len__(self) -> int:
        return len(self._cache)

    def __getitem__(self, key: any) -> any:
        if key not in self._cache:
            raise KeyError(f'"{key}" could not be found in LFU.')

        return self.get(key)

    def __setitem__(self, key: any, value: any) -> None:
        return self.put(key, value)

    @property
    def capacity(self) -> int:
        return self._capacity

    def get(self, key: any, default: any = MISSING) -> any:
        if key not in self._cache:
            return default if default is not MISSING else NotFound

        data: DataNode = self._cache[key]
        self._freq_map[data.frequency].remove(data.node)
        self._freq_map[data.frequency + 1].append(data.node)

        self._cache[key] = DataNode(key=key, value=data.value, frequency=data.frequency + 1, node=data.node)
        self._min += self._min == data.frequency and not self._freq_map[data.frequency]

        return data.value

    def put(self, key: any, value: any) -> None:
        if self._capacity <= 0:
            raise ValueError("Unable to place item in LFU as capacity has been set to 0 or below.")

        if key in self._cache:
            self._cache[key].value = value
            self.get(key)
            return

        if self._used == self._capacity:
            least_freq: DLL = self._freq_map[self._min]
            least_freq_key: DLLNode | None = least_freq.popleft()

            if least_freq_key:
                self._cache.pop(least_freq_key.value)
                self._used -= 1

        data: DataNode = DataNode(key=key, value=value, frequency=1, node=DLLNode(key))
        self._freq_map[data.frequency].append(data.node)
        self._cache[key] = data

        self._used += 1
        self._min = 1

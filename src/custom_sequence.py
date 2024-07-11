from lightrag.core.container import Sequential
from lightrag.core.component import Component
from collections import OrderedDict
from typing import Any, overload, Dict


class CustomSequence(Sequential):
    _components: Dict[str, Component]  # type: ignore[assignment]

    @overload
    def __init__(self, *args: Component) -> None: ...

    @overload
    def __init__(self, arg: "OrderedDict[str, Component]") -> None: ...

    def __init__(self, *args):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], OrderedDict):
            for key, module in args[0].items():
                self.add_component(key, module)
        else:
            for idx, module in enumerate(args):
                self.add_component(str(idx), module)

    async def call(self, input: Any) -> Any:
        for component in self._components.values():
            input = await component(input)
        return input

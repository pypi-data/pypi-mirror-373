from typing import Dict, Any, List, Optional

from dataclasses import dataclass, field


@dataclass
class WrapperData:
    type: str
    data: Dict


@dataclass
class InputInfo:
    name: str
    shape: List[int]


@dataclass
class InputData:
    node: str
    output: str


@dataclass
class OutputData:
    node: str
    input: str


@dataclass
class ConnectionInput:
    connections: List[InputData]


@dataclass
class ConnectionOutput:
    connections: List[OutputData]


@dataclass
class Node:
    id: str
    name: str
    position: List[int]
    data: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, ConnectionInput] = field(default_factory=dict)
    outputs: Dict[str, ConnectionOutput] = field(default_factory=dict)
    pruning_plan_id: Optional[str] = None
    wrapper: Optional[WrapperData] = None

    def __key(self):
        return (self.id, self.name)

    def __hash__(self):
        return hash(self.__key())

    @property
    def type(self) -> Optional[str]:
        return self.data.get('type')


@dataclass
class ModelGraph:
    id: str
    nodes: Dict[str, Node] = field(default_factory=dict)
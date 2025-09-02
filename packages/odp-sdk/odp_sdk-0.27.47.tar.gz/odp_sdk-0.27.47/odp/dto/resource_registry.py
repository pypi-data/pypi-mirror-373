from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Generic, List, Optional, Set, Type, TypeVar

if TYPE_CHECKING:
    from odp.dto.resource import ResourceDto

T = TypeVar("T")


class TreeNode(Generic[T], ABC):
    def __init__(self, key: str):
        self.key = key
        self.data: Optional[T] = None
        self.children: Dict[str, TreeNode] = {}

    @abstractmethod
    def add_data(self, data: T) -> None:
        """Add a data to the node"""

    @abstractmethod
    def get_data(self, *args, **kwargs) -> T:
        """Get the resource"""

    def get_child(self, child: str) -> "TreeNode":
        return self.children.get(child)

    def add_child(self, child: str) -> "TreeNode":
        return self.children.setdefault(child, self.__class__(key=child))


class TreeStructure(Generic[T]):
    def __init__(self):
        self.root: Optional[ResourceNode] = None

    @classmethod
    @abstractmethod
    def add(cls, *args, **kwargs) -> None:
        """Add a new element to the tree"""

    @abstractmethod
    def get(self, *args, **kwargs) -> T:
        """Get the resource"""

    def add_leaf(self, levels) -> TreeNode:
        assert self.root is not None
        node: TreeNode = self.root
        for level in levels:
            node = node.add_child(level)
        return node

    def get_leaf(self, levels: List[str]) -> Optional[TreeNode]:
        node = self.root
        for level in levels:
            node = node.get_child(level)
            if node is None:
                return None
        return node


class ResourceNode(TreeNode[Dict[str, Type["ResourceDto"]]]):  # noqa: F821
    def __init__(self, key: str):
        super().__init__(key=key)
        self.data = {}

    def add_data(self, resource_type: Type["ResourceDto"]):  # noqa: F821
        if self.data.get(resource_type.get_version()):
            raise ValueError(f"Resource version '{resource_type.get_version()}' already exists")
        self.data[resource_type.get_version()] = resource_type

    def get_data(self, version: str) -> Optional[Type["ResourceDto"]]:  # noqa: F821
        return self.data.get(version)

    @property
    def versions(self) -> Set[str]:
        return set(self.data.keys())


class ResourceTypeRegistry(TreeStructure[Dict[str, Type["ResourceDto"]]]):  # noqa: F821
    def __init__(self) -> None:
        super().__init__()
        self.root = ResourceNode(key="")

    def add(self, resource_type: Type["ResourceDto"]) -> None:  # noqa: F821
        node = self.add_leaf(resource_type.get_kind().split("/"))
        node.add_data(resource_type)

    def get(
        self, kind: str, version: str, default: Optional[Type["ResourceDto"]] = None  # noqa: F821
    ) -> Optional[Type["ResourceDto"]]:  # noqa: F821
        node: Optional[ResourceNode] = self.get_leaf(kind.split("/"))
        if node is None:
            return default
        resource = node.get_data(version)
        if resource is None:
            raise ValueError(f"Version '{version}' not found for kind '{kind}'. Use a valid version: {node.versions}")
        return resource


DEFAULT_RESOURCE_TYPE_REGISTRY = ResourceTypeRegistry()

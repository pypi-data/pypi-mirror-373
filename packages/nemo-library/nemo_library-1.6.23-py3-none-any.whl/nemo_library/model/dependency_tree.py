from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class DependencyTree:
    """
    A class to represent a dependency tree node.

    Attributes:
    dependencies (list[Optional["DependencyTree"]]): List of child dependency nodes.
    dependencyType (Optional[str]): Type of the dependency.
    nodeConflictState (str): Conflict state of the node.
    nodeDisplayName (str): Display name of the node.
    nodeId (str): Unique identifier of the node.
    nodeInternalName (str): Internal name of the node.
    nodeType (str): Type of the node.
    """

    dependencies: list[Optional["DependencyTree"]] = field(default_factory=list)
    dependencyType: Optional[str] = None
    nodeConflictState: str = ""
    nodeDisplayName: str = ""
    nodeId: str = ""
    nodeInternalName: str = ""
    nodeType: str = ""

    @staticmethod
    def from_dict(data: dict) -> "DependencyTree":
        """
        Create a DependencyTree instance from a dictionary.

        Args:
        data (dict): A dictionary containing the dependency tree data.

        Returns:
        DependencyTree: An instance of DependencyTree.
        """
        dependencies = (
            [DependencyTree.from_dict(dep) for dep in data.get("dependencies", [])]
            if "dependencies" in data
            else []
        )
        return DependencyTree(
            dependencies=dependencies,
            dependencyType=data.get("dependencyType"),
            nodeConflictState=data.get("nodeConflictState", ""),
            nodeDisplayName=data.get("nodeDisplayName", ""),
            nodeId=data.get("nodeId", ""),
            nodeInternalName=data.get("nodeInternalName", ""),
            nodeType=data.get("nodeType", ""),
        )

    def to_dict(self):
        """
        Convert the DependencyTree instance to a dictionary.

        Returns:
        dict: A dictionary representation of the DependencyTree instance.
        """
        return asdict(self)

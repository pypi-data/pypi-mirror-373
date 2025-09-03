"""
Node definitions for deployment graph using Pydantic models.

This module defines the Node base class and specialized node types
(CoreStepNode, MethodNode, CommandNode) for the deployment graph.
"""

import uuid
from typing import List, Optional, TYPE_CHECKING, ClassVar, Type

from pydantic import BaseModel, Field

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    pass


class Node(BaseModel):
    """
    Base class for nodes in the deployment graph.

    All nodes have an ID, name, and can have children and a parent.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    children: List["Node"] = Field(default_factory=list)
    parent_id: Optional[str] = None
    succeeded: Optional[bool] = None
    output: Optional[str] = None
    error: Optional[str] = None

    # 类型标识符，用于替代 NodeType 枚举
    node_type_name: ClassVar[str] = "node"

    def add_child(self, child: "Node") -> "Node":
        """
        Add a child node to this node.

        Args:
            child: The child node to add

        Returns:
            The child node for chaining
        """
        self.children.append(child)
        child.parent_id = self.id
        return child

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        """获取允许作为子节点的类型列表"""
        return []

    def can_add_child(self, child: "Node") -> bool:
        """
        检查是否可以添加指定的子节点

        Args:
            child: 要添加的子节点

        Returns:
            如果可以添加则返回 True，否则返回 False
        """
        allowed_types = self.get_allowed_child_types()
        if not allowed_types:
            return False

        return any(isinstance(child, child_type) for child_type in allowed_types)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"


class RootNode(Node):
    """
    Root node for the deployment graph.
    can only have CoreStepNode children.
    """
    node_type_name: ClassVar[str] = "root"

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [CoreStepNode]


class CoreStepNode(Node):
    """
    Represents a major step in the deployment process.

    Core steps are the highest level nodes in the graph, representing
    major phases of the deployment like "Install Dependencies" or "Download Models".
    """
    node_type_name: ClassVar[str] = "core_step"

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [MethodNode]


class VerifyNode(Node):
    """
    Represents verification and dependency checking phase of a method.
    
    VerifyNode is created by MethodNode and contains commands to check and install
    necessary software, dependencies, and prerequisites. Should heavily utilize
    LogicCommandNode for conditional checks.
    """
    node_type_name: ClassVar[str] = "verify"

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [CommandNode, LogicCommandNode]


class ForwardNode(Node):
    """
    Represents the main execution phase of a method.
    
    ForwardNode is created by MethodNode and contains the actual command sequence
    to accomplish the method's goal. Should not include verification commands.
    """
    node_type_name: ClassVar[str] = "forward"

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [CommandNode, LogicCommandNode]


class MethodNode(Node):
    """
    Represents a specific method to accomplish a core step.

    Methods are alternative ways to complete a core step, like
    "Using pip" or "Using conda" for an "Install Dependencies" core step.
    Can only have VerifyNode and ForwardNode as children.
    """
    node_type_name: ClassVar[str] = "method"
    working_directory: Optional[str] = None  # Directory where this method operates
    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [VerifyNode, ForwardNode]


class FixNode(Node):
    """
    Represents a fix attempt for a failed command.
    
    FixNode can only have CommandNode as parent and can only have CommandNode children.
    Used to represent attempts to fix a failed command execution.
    """
    node_type_name: ClassVar[str] = "fix"
    target_command_id: str = Field(..., description="ID of the command this fix is targeting")
    fix_depth: int = Field(default=1, description="Depth level of this fix (1 = first level fix)")

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [CommandNode]


class CommandNode(Node):
    """
    Represents a specific shell command to execute.

    Commands are leaf nodes that perform actual operations like
    running "pip install -r requirements.txt".
    """
    node_type_name: ClassVar[str] = "command"
    command: str | None
    missing_info: bool = False  # True if command needs user-provided information
    interactive: bool = False   # True if command requires direct terminal interaction

    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [FixNode]


class LogicCommandNode(CommandNode):
    """
    Represents a logical command node that performs conditional execution.
    
    LogicCommandNode can only be created by MethodNode and can only have exactly two children:
    CommandNode or LogicCommandNode. Based on the execution result (True/False),
    it will execute either the left (True) or right (False) child node.
    """
    node_type_name: ClassVar[str] = "logic_command"
    
    def add_child(self, child: "Node") -> "Node":
        """
        Override add_child to enforce exactly two children constraint.
        
        Args:
            child: The child node to add
            
        Returns:
            The child node for chaining
            
        Raises:
            ValueError: If trying to add more than 2 children
        """
        if len(self.children) >= 2:
            raise ValueError("LogicCommandNode can only have exactly two children")
        
        return super().add_child(child)
    
    @classmethod
    def get_allowed_child_types(cls) -> List[Type["Node"]]:
        return [CommandNode, LogicCommandNode]
    
    def can_add_child(self, child: "Node") -> bool:
        """
        Check if a child can be added to this LogicCommandNode.
        
        Args:
            child: The child node to check
            
        Returns:
            True if child can be added, False otherwise
        """
        # Check if we already have 2 children
        if len(self.children) >= 2:
            return False
        
        # Check if child type is allowed
        return super().can_add_child(child)
    
    @property
    def true_child(self) -> Optional["Node"]:
        """Get the true child (executed when condition is True)."""
        return self.children[0] if len(self.children) > 0 else None
    
    @property
    def false_child(self) -> Optional["Node"]:
        """Get the false child (executed when condition is False)."""
        return self.children[1] if len(self.children) > 1 else None
    
    def is_complete(self) -> bool:
        """Check if this LogicCommandNode has both required children."""
        return len(self.children) == 2

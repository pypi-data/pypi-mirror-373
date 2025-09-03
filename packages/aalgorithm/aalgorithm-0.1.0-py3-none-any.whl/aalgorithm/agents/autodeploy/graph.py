"""
Graph structure for deployment flow control.

This module provides classes to represent and manipulate the deployment graph
with different types of nodes (core steps, solution methods, and commands).
It also handles Neo4j-based visualization of the graph.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from .log_config import logger, log_node, log_graph_visualization_status, log_node_details  # Import logging utilities
from .nodes import Node, CoreStepNode, MethodNode, CommandNode, RootNode, FixNode, LogicCommandNode, VerifyNode, \
    ForwardNode

# Check for Neo4j availability
try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j package not available. Install with: pip install neo4j")


class DeploymentGraph:
    """
    Represents the complete deployment graph with operations for traversal
    and manipulation. Can optionally visualize the graph in Neo4j.
    """

    def __init__(self, name: str, neo4j_config: Optional[Dict] = None):
        """
        Initialize a deployment graph.

        Args:
            name: Name of the deployment graph (e.g., project name)
            neo4j_config: Optional Neo4j configuration for visualization
                {
                    'enabled': bool,
                    'uri': str,
                    'user': str,
                    'password': str,
                    'database': str
                }
        """
        self.name = name
        self.root: Optional[RootNode] = None
        self.nodes: Dict[str, Node] = {}  # id -> node

        # Neo4j configuration
        self.neo4j_config = neo4j_config or self._get_neo4j_config_from_env()
        self.neo4j_enabled = self.neo4j_config.get('enabled', False) and NEO4J_AVAILABLE
        self.neo4j_driver = None
        self.session_id = self.name

        # Node type mappings for Neo4j labels
        self.node_type_mappings = {
            "root": "RootNode",
            "core_step": "CoreStepNode",
            "method": "MethodNode",
            "verify": "VerifyNode",
            "forward": "ForwardNode",
            "command": "CommandNode",
            "fix": "FixNode",
            "logic_command": "LogicCommandNode"
        }

        # Connect to Neo4j if enabled
        if self.neo4j_enabled:
            self._connect_to_neo4j()
            self._clear_neo4j_graph()



    def _get_neo4j_config_from_env(self) -> Dict:
        """Get Neo4j configuration from environment variables."""
        return {
            'enabled': os.getenv("ENABLE_NEO4J_VIZ", "false").lower() == "true",
            'uri': os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            'user': os.getenv("NEO4J_USER", "neo4j"),
            'password': os.getenv("NEO4J_PASSWORD", "password"),
            'database': os.getenv("NEO4J_DATABASE", "neo4j")
        }

    def _connect_to_neo4j(self) -> bool:
        """Connect to Neo4j database."""
        if not NEO4J_AVAILABLE:
            return False

        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_config['uri'],
                auth=(self.neo4j_config['user'], self.neo4j_config['password'])
            )

            # Test connection
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                session.run("RETURN 1")

            log_graph_visualization_status(True, self.neo4j_config['uri'])
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.neo4j_enabled = False
            return False

    def _disconnect_from_neo4j(self):
        """Disconnect from Neo4j database."""
        if self.neo4j_driver:
            try:
                self.neo4j_driver.close()
                self.neo4j_driver = None
                logger.info("Disconnected from Neo4j")
            except Exception as e:
                logger.error(f"Error disconnecting from Neo4j: {e}")

    def _clear_neo4j_graph(self):
        """Clear the current graph from Neo4j."""
        if not self.neo4j_enabled or not self.neo4j_driver:
            return

        try:
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                session.run(
                    "MATCH (n) WHERE n.session_id = $session_id "
                    "DETACH DELETE n",
                    session_id=self.session_id
                )

            logger.info(f"Cleared Neo4j graph for session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to clear Neo4j graph: {e}")

    def _get_node_properties(self, node: Node) -> Dict:
        """
        Get properties for a node to store in Neo4j.
        
        Args:
            node: Node to extract properties from
            
        Returns:
            Dictionary of node properties
        """
        properties = {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "node_type": node.node_type_name,
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "succeeded": node.succeeded,
            "output": node.output,
            "error": node.error,
            "parent_id": node.parent_id
        }

        # Add node-specific properties
        if isinstance(node, CommandNode):
            properties.update({
                "command": node.command,
                "missing_info": node.missing_info,
                "interactive": node.interactive
            })
        elif isinstance(node, FixNode):
            properties.update({
                "target_command_id": node.target_command_id,
                "fix_depth": node.fix_depth
            })
        elif isinstance(node, MethodNode):
            properties.update({
                "working_directory": node.working_directory
            })

        # Remove None values
        return {k: v for k, v in properties.items() if v is not None}

    def _create_neo4j_node(self, node: Node) -> bool:
        """Create a node in Neo4j."""
        if not self.neo4j_enabled or not self.neo4j_driver:
            return False

        try:
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                # Get node label
                label = self.node_type_mappings.get(node.node_type_name, "Node")

                # Get node properties
                properties = self._get_node_properties(node)

                # Create node
                session.run(
                    f"CREATE (n:{label} $properties)",
                    properties=properties
                )

                logger.debug(f"Created Neo4j {label} node: {node.name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create node in Neo4j: {e}")
            return False

    def _update_neo4j_node(self, node: Node) -> bool:
        """Update a node in Neo4j."""
        if not self.neo4j_enabled or not self.neo4j_driver:
            return False

        try:
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                # Get updated properties
                properties = self._get_node_properties(node)
                properties["updated_at"] = datetime.now().isoformat()

                # Update node
                session.run(
                    "MATCH (n) WHERE n.id = $node_id AND n.session_id = $session_id "
                    "SET n += $properties",
                    node_id=node.id,
                    session_id=self.session_id,
                    properties=properties
                )

                logger.debug(f"Updated Neo4j node: {node.name}")
                return True

        except Exception as e:
            logger.error(f"Failed to update node in Neo4j: {e}")
            return False

    def _create_neo4j_relationship(self, parent_node: Node, child_node: Node,
                                   relationship_type: str = "CONTAINS") -> bool:
        """Create a relationship between two nodes in Neo4j."""
        if not self.neo4j_enabled or not self.neo4j_driver:
            return False

        try:
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                # Create relationship
                session.run(
                    "MATCH (parent) WHERE parent.id = $parent_id AND parent.session_id = $session_id "
                    "MATCH (child) WHERE child.id = $child_id AND child.session_id = $session_id "
                    f"CREATE (parent)-[r:{relationship_type}]->(child) "
                    "SET r.created_at = $created_at",
                    parent_id=parent_node.id,
                    child_id=child_node.id,
                    session_id=self.session_id,
                    created_at=datetime.now().isoformat()
                )

                logger.debug(f"Created Neo4j {relationship_type} relationship: {parent_node.name} -> {child_node.name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create relationship in Neo4j: {e}")
            return False

    def _create_neo4j_core_step_sequence(self, core_steps: List[CoreStepNode]) -> bool:
        """Create sequential relationships between core steps in Neo4j."""
        if not self.neo4j_enabled or not self.neo4j_driver:
            return False

        try:
            with self.neo4j_driver.session(database=self.neo4j_config['database']) as session:
                # Create NEXT relationships between consecutive core steps
                for i in range(len(core_steps) - 1):
                    current_step = core_steps[i]
                    next_step = core_steps[i + 1]

                    session.run(
                        "MATCH (current) WHERE current.id = $current_id AND current.session_id = $session_id "
                        "MATCH (next) WHERE next.id = $next_id AND next.session_id = $session_id "
                        "CREATE (current)-[r:NEXT]->(next) "
                        "SET r.created_at = $created_at, r.sequence = $sequence",
                        current_id=current_step.id,
                        next_id=next_step.id,
                        session_id=self.session_id,
                        created_at=datetime.now().isoformat(),
                        sequence=i + 1
                    )

                    logger.debug(f"Created Neo4j NEXT relationship: {current_step.name} -> {next_step.name}")

                return True

        except Exception as e:
            logger.error(f"Failed to create core step sequence in Neo4j: {e}")
            return False

    def create_root(self, name: str, description: Optional[str] = None) -> RootNode:
        """
        Create a root node (typically represents the starting point).

        Args:
            name: Name of the root node
            description: Optional description

        Returns:
            The newly created root node
        """
        self.root = RootNode(name=name, description=description or "")
        self.nodes[self.root.id] = self.root

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(self.root)
            
        return self.root

    def add_core_step(self, parent_id: str, name: str,
                      description: Optional[str] = None) -> CoreStepNode:
        """
        Add a new core step node to the graph.

        Args:
            parent_id: ID of the parent node
            name: Name of the core step
            description: Optional description

        Returns:
            The newly created core step node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        node = CoreStepNode(name=name, description=description or "")
        parent = self.nodes[parent_id]

        # 检查父节点是否允许添加 CoreStepNode 类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' of type {parent.__class__.__name__} "
                            f"cannot have a child of type {node.__class__.__name__}")

        self.nodes[node.id] = node
        self.nodes[parent_id].add_child(node)

        # Log detailed node information when node is created
        log_node_details(node, "created", f"Core step node '{name}' created")

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_method(self, parent_id: str, name: str,
                   description: Optional[str] = None) -> MethodNode:
        """
        Add a new method node to the graph.

        Args:
            parent_id: ID of the parent node (should be a core step)
            name: Name of the method
            description: Optional description

        Returns:
            The newly created method node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        parent = self.nodes[parent_id]

        # 确保父节点是 CoreStepNode 类型
        if not isinstance(parent, CoreStepNode):
            raise TypeError(f"Parent node must be a CoreStepNode, got {parent.__class__.__name__}")

        node = MethodNode(name=name, description=description or "")

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type MethodNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Log detailed node information when node is created
        log_node_details(node, "created", f"Method node '{name}' created")

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_verify_node(self, parent_id: str, name: str,
                        description: Optional[str] = None) -> VerifyNode:
        """
        Add a new verify node to the graph.

        Args:
            parent_id: ID of the parent node (should be a method)
            name: Name of the verify node
            description: Optional description

        Returns:
            The newly created verify node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        parent = self.nodes[parent_id]

        # 确保父节点是 MethodNode 类型
        if not isinstance(parent, MethodNode):
            raise TypeError(f"Parent node must be a MethodNode, got {parent.__class__.__name__}")

        node = VerifyNode(name=name, description=description or "")

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type VerifyNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_forward_node(self, parent_id: str, name: str,
                         description: Optional[str] = None) -> ForwardNode:
        """
        Add a new forward node to the graph.

        Args:
            parent_id: ID of the parent node (should be a method)
            name: Name of the forward node
            description: Optional description

        Returns:
            The newly created forward node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        parent = self.nodes[parent_id]

        # 确保父节点是 MethodNode 类型
        if not isinstance(parent, MethodNode):
            raise TypeError(f"Parent node must be a MethodNode, got {parent.__class__.__name__}")

        node = ForwardNode(name=name, description=description or "")

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type ForwardNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_command(self, parent_id: str, name: str, command: str,
                    missing_info: bool, interactive: bool,
                    description: Optional[str] = None) -> CommandNode:
        """
        Add a new command node to the graph.

        Args:
            parent_id: ID of the parent node (should be a VerifyNode or ForwardNode)
            name: Name of the command
            command: The shell command to execute
            missing_info: Whether the command needs user-provided information
            interactive: Whether the command requires direct terminal interaction
            description: Optional description

        Returns:
            The newly created command node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        parent = self.nodes[parent_id]

        # 确保父节点是 VerifyNode 或 ForwardNode 类型
        if not isinstance(parent, (VerifyNode, ForwardNode)):
            raise TypeError(f"Parent node must be a VerifyNode or ForwardNode, got {parent.__class__.__name__}")

        node = CommandNode(
            name=name,
            command=command,
            description=description or "",
            missing_info=missing_info,
            interactive=interactive
        )

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type CommandNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Log detailed node information when node is created
        log_node_details(node, "created", f"Command node '{name}' created")

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_fix_node(self, parent_command_id: str, name: str,
                     fix_depth: int = 1, description: Optional[str] = None) -> FixNode:
        """
        Add a new fix node to the graph.

        Args:
            parent_command_id: ID of the parent CommandNode
            name: Name of the fix attempt
            fix_depth: Depth level of this fix
            description: Optional description

        Returns:
            The newly created fix node
        """
        if parent_command_id not in self.nodes:
            raise ValueError(f"Parent command with ID {parent_command_id} not found")

        parent = self.nodes[parent_command_id]

        # 确保父节点是 CommandNode 类型
        if not isinstance(parent, CommandNode):
            raise TypeError(f"Parent node must be a CommandNode, got {parent.__class__.__name__}")

        node = FixNode(
            name=name,
            description=description or "",
            target_command_id=parent_command_id,
            fix_depth=fix_depth
        )

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type FixNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Log detailed node information when node is created
        log_node_details(node, "created", f"Fix node '{name}' created")

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_fix_command(self, parent_fix_id: str, name: str, command: str,
                        missing_info: bool, interactive: bool,
                        description: Optional[str] = None) -> CommandNode:
        """
        Add a new command node under a FixNode.

        Args:
            parent_fix_id: ID of the parent FixNode
            name: Name of the fix command
            command: The shell command to execute
            missing_info: Whether the command needs user-provided information
            interactive: Whether the command requires direct terminal interaction
            description: Optional description

        Returns:
            The newly created command node
        """
        if parent_fix_id not in self.nodes:
            raise ValueError(f"Parent fix node with ID {parent_fix_id} not found")

        parent = self.nodes[parent_fix_id]

        # 确保父节点是 FixNode 类型
        if not isinstance(parent, FixNode):
            raise TypeError(f"Parent node must be a FixNode, got {parent.__class__.__name__}")

        node = CommandNode(
            name=name,
            command=command,
            description=description or "",
            missing_info=missing_info,
            interactive=interactive
        )

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type CommandNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_logic_command(self, parent_id: str, name: str, command: str,
                          missing_info: bool, interactive: bool,
                          description: Optional[str] = None) -> LogicCommandNode:
        """
        Add a new logic command node to the graph.

        Args:
            parent_id: ID of the parent node (should be a VerifyNode or ForwardNode)
            name: Name of the logic command
            command: The shell command to execute for logical evaluation
            missing_info: Whether the command needs user-provided information
            interactive: Whether the command requires direct terminal interaction
            description: Optional description

        Returns:
            The newly created logic command node
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        parent = self.nodes[parent_id]

        # 确保父节点是 VerifyNode 或 ForwardNode 类型
        if not isinstance(parent, (VerifyNode, ForwardNode)):
            raise TypeError(f"Parent node must be a VerifyNode or ForwardNode, got {parent.__class__.__name__}")

        node = LogicCommandNode(
            name=name,
            command=command,
            description=description or "",
            missing_info=missing_info,
            interactive=interactive
        )

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type LogicCommandNode")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Log detailed node information when node is created
        log_node_details(node, "created", f"Logic command node '{name}' created")

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def add_logic_command_child(self, parent_logic_id: str, name: str, command: str | None,
                                missing_info: bool, interactive: bool,
                                description: Optional[str] = None,
                                is_command_node: bool = True, is_true_branch: bool = True) -> Union[
        CommandNode, LogicCommandNode]:
        """
        Add a child node to a LogicCommandNode.

        Args:
            parent_logic_id: ID of the parent LogicCommandNode
            name: Name of the child node
            command: The shell command to execute
            missing_info: Whether the command needs user-provided information
            interactive: Whether the command requires direct terminal interaction
            description: Optional description
            is_command_node: If True, creates CommandNode; if False, creates LogicCommandNode
            is_true_branch: If True, adds as true branch (first child); if False, adds as false branch (second child)

        Returns:
            The newly created child node
        """
        if parent_logic_id not in self.nodes:
            raise ValueError(f"Parent logic command with ID {parent_logic_id} not found")

        parent = self.nodes[parent_logic_id]

        # 确保父节点是 LogicCommandNode 类型
        if not isinstance(parent, LogicCommandNode):
            raise TypeError(f"Parent node must be a LogicCommandNode, got {parent.__class__.__name__}")

        # 检查是否已经有对应位置的子节点
        if is_true_branch and parent.true_child:
            raise ValueError(f"LogicCommandNode '{parent.name}' already has a true branch (first child)")
        elif not is_true_branch and parent.false_child:
            raise ValueError(f"LogicCommandNode '{parent.name}' already has a false branch (second child)")
        elif not is_true_branch and not parent.true_child:
            raise ValueError(f"Must add true branch before false branch in LogicCommandNode '{parent.name}'")

        if is_command_node:
            node = CommandNode(
                name=name,
                command=command,
                description=description or "",
                missing_info=missing_info,
                interactive=interactive
            )
        else:
            node = LogicCommandNode(
                name=name,
                command=command,
                description=description or "",
                missing_info=missing_info,
                interactive=interactive
            )

        # 验证父节点是否允许添加此类型的子节点
        if not parent.can_add_child(node):
            node_type = "CommandNode" if is_command_node else "LogicCommandNode"
            raise TypeError(f"Parent node '{parent.name}' cannot have a child of type {node_type}")

        self.nodes[node.id] = node
        parent.add_child(node)

        # Add to Neo4j if enabled
        if self.neo4j_enabled:
            self._create_neo4j_node(node)
            self._create_neo4j_relationship(parent, node)
            
        return node

    def update_node_status(self, node_id: str, succeeded: bool | None, output: Optional[str] = None,
                           error: Optional[str] = None):
        """
        Update a node's status and output information.
        
        Args:
            node_id: ID of the node to update
            succeeded: Whether the node executed successfully
            output: Optional output from execution
            error: Optional error message
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID {node_id} not found")

        node = self.nodes[node_id]
        node.succeeded = succeeded

        if output is not None:
            node.output = output

        if error is not None:
            node.error = error

        # Update in Neo4j if enabled
        if self.neo4j_enabled:
            self._update_neo4j_node(node)

    def get_node(self, node_id: str) -> Node:
        """Get a node by its ID."""
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID {node_id} not found")
        return self.nodes[node_id]

    def get_leaf_nodes(self) -> List[Node]:
        """
        Get all leaf nodes (nodes without children) in order of traversal.

        Returns:
            List of leaf nodes
        """
        leaves = []

        def collect_leaves(node: Node):
            if not node.children:
                leaves.append(node)
            else:
                for child in node.children:
                    collect_leaves(child)

        if self.root:
            collect_leaves(self.root)

        return leaves

    def get_execution_path(self) -> List[CommandNode]:
        """
        Get ordered list of COMMAND nodes forming the execution path.

        Returns:
            List of command nodes in execution order
        """
        commands = []

        def collect_commands(node: Node):
            if isinstance(node, CommandNode):
                commands.append(node)
            for child in node.children:
                collect_commands(child)

        if self.root:
            collect_commands(self.root)

        return commands

    def create_core_step_sequence(self, core_steps: List[CoreStepNode]):
        """
        Create sequential relationships between core steps.
        
        Args:
            core_steps: List of core steps in execution order
        """
        if self.neo4j_enabled:
            self._create_neo4j_core_step_sequence(core_steps)

    def to_graphml(self) -> str:
        """
        Generate a GraphML representation of the deployment graph.

        Returns:
            GraphML XML string
        """
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        # Create root GraphML element
        graphml = ET.Element("graphml")
        graphml.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
        graphml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        graphml.set("xsi:schemaLocation",
                    "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")

        # Define node attributes
        node_name_key = ET.SubElement(graphml, "key")
        node_name_key.set("id", "node_name")
        node_name_key.set("for", "node")
        node_name_key.set("attr.name", "name")
        node_name_key.set("attr.type", "string")

        node_type_key = ET.SubElement(graphml, "key")
        node_type_key.set("id", "node_type")
        node_type_key.set("for", "node")
        node_type_key.set("attr.name", "type")
        node_type_key.set("attr.type", "string")

        node_desc_key = ET.SubElement(graphml, "key")
        node_desc_key.set("id", "node_desc")
        node_desc_key.set("for", "node")
        node_desc_key.set("attr.name", "description")
        node_desc_key.set("attr.type", "string")

        # Create graph element
        graph = ET.SubElement(graphml, "graph")
        graph.set("id", "DeploymentGraph")
        graph.set("edgedefault", "directed")

        def get_node_type(node: Node) -> str:
            if isinstance(node, CoreStepNode):
                return "core_step"
            elif isinstance(node, MethodNode):
                return "method"
            elif isinstance(node, VerifyNode):
                return "verify"
            elif isinstance(node, ForwardNode):
                return "forward"
            elif isinstance(node, FixNode):
                return "fix"
            elif isinstance(node, CommandNode):
                return "command"
            else:
                return "unknown"

        def add_node_to_graph(node: Node) -> None:
            node_elem = ET.SubElement(graph, "node")
            node_elem.set("id", node.id)

            # Add node name
            name_data = ET.SubElement(node_elem, "data")
            name_data.set("key", "node_name")
            name_data.text = node.name

            # Add node type
            type_data = ET.SubElement(node_elem, "data")
            type_data.set("key", "node_type")
            type_data.text = get_node_type(node)

            # Add node description
            desc_data = ET.SubElement(node_elem, "data")
            desc_data.set("key", "node_desc")
            desc_data.text = node.description or ""

        def add_edge_to_graph(parent_id: str, child_id: str) -> None:
            edge_elem = ET.SubElement(graph, "edge")
            edge_elem.set("source", parent_id)
            edge_elem.set("target", child_id)

        def traverse(node: Node) -> None:
            add_node_to_graph(node)
            
            for child in node.children:
                traverse(child)
                add_edge_to_graph(node.id, child.id)
        
        if self.root:
            traverse(self.root)

        # Pretty print the XML
        rough_string = ET.tostring(graphml, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


    def log_node(self, node: Node, message: str, level: str = "info"):
        """
        Log a message with node context.
        
        Args:
            node: The node being executed
            message: The log message
            level: Log level (info, warning, error, debug)
        """
        log_node(node, message, level)


    def print_graph(self) -> str:
        """
        Generate a human-readable representation of the graph with indentation.

        Returns:
            String representation of the graph
        """
        if not self.root:
            return "Empty graph (no root node)"

        result = [f"DeploymentGraph: {self.name}"]

        def _print_node(node: Node, depth: int = 0):
            indent = "  " * depth
            node_type = node.__class__.__name__

            # Basic information for all nodes
            line = f"{indent}└─ [{node_type}] {node.name} (id: {node.id})"
            if node.description:
                line += f"\n{indent}   Description: {node.description}"
            result.append(line)

            # Node-specific details
            if isinstance(node, CommandNode):
                result.append(f"{indent}   Command: {node.command}")
                result.append(f"{indent}   Interactive: {node.interactive}")
            # Process children
            for child in node.children:
                _print_node(child, depth + 1)

        _print_node(self.root)
        return "\n".join(result)

    def __str__(self) -> str:
        """Return string representation of the graph."""
        return self.print_graph()

    def __repr__(self) -> str:
        return f"<DeploymentGraph {self.name} with {len(self.nodes)} nodes>"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.neo4j_enabled:
            self._disconnect_from_neo4j()

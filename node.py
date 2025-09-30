"""
Node class for encapsulating distributed SQLite ledger functionality.

This module provides a Node class that encapsulates all the functionality
needed to manage a distributed SQLite ledger, including database operations,
Merkle root computation, and peer comparison.
"""

import sqlite3
from typing import Optional, Dict, Any

from ledger import init_db, add_record, get_all_records, get_record_count
from merkle import merkle_root, compare_merkle_roots


class Node:
    """
    Represents a single node in a distributed SQLite ledger network.
    
    Each node maintains its own SQLite database as an immutable ledger
    and can compute Merkle roots for comparison with other nodes.
    """
    
    def __init__(self, name: str, db_file: str):
        """
        Initialize a new node.
        
        Args:
            name: Human-readable name for this node
            db_file: Path to the SQLite database file
        """
        self.name = name
        self.db_file = db_file
        self.connection: Optional[sqlite3.Connection] = None
        self._is_initialized = False
    
    def initialize(self) -> 'Node':
        """
        Initialize the node's database connection and ledger.
        
        Returns:
            Node: Returns self for method chaining
        """
        if self._is_initialized:
            return self
            
        self.connection = init_db(self.db_file)
        self._is_initialized = True
        return self
    
    def add_event(self, data: str) -> int:
        """
        Add a new event to this node's ledger.
        
        Args:
            data: The event data to record
            
        Returns:
            int: The ID of the inserted record
            
        Raises:
            RuntimeError: If node is not initialized
        """
        if not self._is_initialized:
            raise RuntimeError(f"Node {self.name} is not initialized. Call initialize() first.")
        
        return add_record(self.connection, data)
    
    def get_merkle_root(self) -> str:
        """
        Compute the Merkle root for this node's ledger.
        
        Returns:
            str: The Merkle root hash
            
        Raises:
            RuntimeError: If node is not initialized
        """
        if not self._is_initialized:
            raise RuntimeError(f"Node {self.name} is not initialized. Call initialize() first.")
        
        return merkle_root(self.connection)
    
    def get_record_count(self) -> int:
        """
        Get the number of records in this node's ledger.
        
        Returns:
            int: Number of records
            
        Raises:
            RuntimeError: If node is not initialized
        """
        if not self._is_initialized:
            raise RuntimeError(f"Node {self.name} is not initialized. Call initialize() first.")
        
        return get_record_count(self.connection)
    
    def get_all_records(self) -> list[tuple]:
        """
        Get all records from this node's ledger.
        
        Returns:
            list[tuple]: List of (id, timestamp, data, hash) tuples
            
        Raises:
            RuntimeError: If node is not initialized
        """
        if not self._is_initialized:
            raise RuntimeError(f"Node {self.name} is not initialized. Call initialize() first.")
        
        return get_all_records(self.connection)
    
    def compare(self, other: 'Node') -> Dict[str, Any]:
        """
        Compare this node with another node.
        
        Args:
            other: Another Node instance to compare with
            
        Returns:
            Dict containing comparison results:
            - 'identical': bool - Whether the nodes are identical
            - 'root_self': str - This node's Merkle root
            - 'root_other': str - Other node's Merkle root
            - 'records_self': int - Number of records in this node
            - 'records_other': int - Number of records in other node
            - 'divergence_type': str - Description of divergence type
        """
        if not self._is_initialized:
            raise RuntimeError(f"Node {self.name} is not initialized. Call initialize() first.")
        if not other._is_initialized:  # pylint: disable=protected-access
            raise RuntimeError(f"Node {other.name} is not initialized. Call initialize() first.")
        
        root_self = self.get_merkle_root()
        root_other = other.get_merkle_root()
        records_self = self.get_record_count()
        records_other = other.get_record_count()
        
        identical = compare_merkle_roots(root_self, root_other)
        
        # Determine divergence type
        if identical:
            divergence_type = "None - nodes are identical"
        elif records_self == records_other:
            divergence_type = "Content divergence - same number of records but different content"
        elif records_self > records_other:
            divergence_type = f"Node {self.name} has {records_self - records_other} more records"
        else:
            divergence_type = f"Node {other.name} has {records_other - records_self} more records"
        
        return {
            'identical': identical,
            'root_self': root_self,
            'root_other': root_other,
            'records_self': records_self,
            'records_other': records_other,
            'divergence_type': divergence_type
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of this node.
        
        Returns:
            Dict containing node status information
        """
        if not self._is_initialized:
            return {
                'name': self.name,
                'db_file': self.db_file,
                'initialized': False,
                'status': 'Not initialized'
            }
        
        records = self.get_all_records()
        merkle_root_hash = self.get_merkle_root()
        
        return {
            'name': self.name,
            'db_file': self.db_file,
            'initialized': True,
            'record_count': len(records),
            'merkle_root': merkle_root_hash,
            'latest_records': [record[2] for record in records[-3:]],  # Last 3 record data
            'status': 'Active'
        }
    
    def print_status(self):
        """Print a formatted status report for this node."""
        status = self.get_status()
        
        print(f"📊 Node: {status['name']}")
        print(f"   Database: {status['db_file']}")
        print(f"   Status: {status['status']}")
        
        if status['initialized']:
            print(f"   Records: {status['record_count']}")
            print(f"   Merkle Root: {status['merkle_root'][:16]}...{status['merkle_root'][-16:]}")
            
            if status['latest_records']:
                print("   Recent Records:")
                for record in status['latest_records']:
                    print(f"     • {record[:50]}{'...' if len(record) > 50 else ''}")
        
        print()
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self._is_initialized = False
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self):
        """String representation of the node."""
        status = "initialized" if self._is_initialized else "not initialized"
        return f"Node(name='{self.name}', db_file='{self.db_file}', status='{status}')"


def create_node_network(node_configs: list[tuple[str, str]]) -> list[Node]:
    """
    Create a network of nodes from configuration.
    
    Args:
        node_configs: List of (name, db_file) tuples
        
    Returns:
        list[Node]: List of initialized Node instances
    """
    nodes = []
    for name, db_file in node_configs:
        node = Node(name, db_file)
        node.initialize()
        nodes.append(node)
    return nodes


def compare_network(nodes: list[Node]) -> Dict[str, Any]:
    """
    Compare all nodes in a network and find sync groups.
    
    Args:
        nodes: List of Node instances
        
    Returns:
        Dict containing network comparison results
    """
    if len(nodes) < 2:
        return {'error': 'Need at least 2 nodes to compare'}
    
    # Get Merkle roots for all nodes
    roots = {}
    for node in nodes:
        roots[node.name] = node.get_merkle_root()
    
    # Find sync groups
    sync_groups = []
    processed_nodes = set()
    
    for node_name, root in roots.items():
        if node_name in processed_nodes:
            continue
            
        # Find all nodes with the same root
        sync_group = [node_name]
        for other_node, other_root in roots.items():
            if other_node != node_name and other_root == root:
                sync_group.append(other_node)
                processed_nodes.add(other_node)
        
        processed_nodes.add(node_name)
        sync_groups.append(sync_group)
    
    # Calculate statistics
    total_nodes = len(nodes)
    synced_nodes = sum(len(group) for group in sync_groups if len(group) > 1)
    sync_percentage = (synced_nodes / total_nodes) * 100 if total_nodes > 0 else 0
    
    return {
        'sync_groups': sync_groups,
        'roots': roots,
        'total_nodes': total_nodes,
        'synced_nodes': synced_nodes,
        'sync_percentage': sync_percentage,
        'network_healthy': sync_percentage >= 80  # 80% threshold for "healthy"
    }



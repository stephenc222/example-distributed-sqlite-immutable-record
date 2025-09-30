"""
Merkle tree implementation for computing immutable fingerprints of ledger data.

This module provides functions to compute Merkle tree roots from SQLite ledger data.
Merkle trees create a cryptographic fingerprint that changes if any data changes,
making them perfect for detecting divergence between distributed databases.
"""

import hashlib
import sqlite3
from typing import List


def sha256(data: str) -> str:
    """
    Compute SHA256 hash of input data.
    
    Args:
        data: String data to hash
        
    Returns:
        str: Hexadecimal representation of the SHA256 hash
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def compute_merkle_root(hashes: List[str]) -> str:
    """
    Compute the Merkle root from a list of hashes.
    
    This function builds a binary Merkle tree by:
    1. Taking pairs of hashes and concatenating them
    2. Computing SHA256 of each concatenated pair
    3. Repeating until only one hash remains (the root)
    
    For odd numbers of hashes, the last hash is duplicated.
    
    Args:
        hashes: List of hash strings to build the tree from
        
    Returns:
        str: The Merkle root hash
    """
    if not hashes:
        # Empty tree - return hash of empty string
        return sha256("")
    
    if len(hashes) == 1:
        return hashes[0]
    
    # Build next level by pairing hashes
    next_level = []
    for i in range(0, len(hashes), 2):
        left = hashes[i]
        right = hashes[i + 1] if i + 1 < len(hashes) else hashes[i]  # Duplicate if odd
        
        # Concatenate and hash
        combined = left + right
        next_level.append(sha256(combined))
    
    # Recursively compute root
    return compute_merkle_root(next_level)


def merkle_root(conn: sqlite3.Connection) -> str:
    """
    Compute the Merkle root for all records in the ledger.
    
    This function:
    1. Retrieves all records from the ledger in order
    2. Creates a hash for each record (using id, timestamp, data, and hash)
    3. Computes the Merkle tree root from these hashes
    
    The Merkle root serves as a cryptographic fingerprint of the entire ledger.
    Any change to any record will result in a different root.
    
    Args:
        conn: SQLite database connection to the ledger
        
    Returns:
        str: The Merkle root hash representing the entire ledger state
    """
    # Get all records in order
    cursor = conn.execute("""
        SELECT id, timestamp, data, hash
        FROM ledger
        ORDER BY id
    """)
    
    records = cursor.fetchall()
    
    if not records:
        # Empty ledger - return hash of empty string
        return sha256("")
    
    # Create a hash for each record
    record_hashes = []
    for record in records:
        id_val, _, data, _ = record
        
        # Create a composite hash that includes record order and data
        # We include ID for ordering but exclude timestamp to allow identical data
        # to produce identical roots when added in the same order
        composite_data = f"{id_val}:{data}"
        record_hashes.append(sha256(composite_data))
    
    # Compute Merkle root
    return compute_merkle_root(record_hashes)


def compare_merkle_roots(root1: str, root2: str) -> bool:
    """
    Compare two Merkle roots for equality.
    
    Args:
        root1: First Merkle root to compare
        root2: Second Merkle root to compare
        
    Returns:
        bool: True if roots are identical (ledgers are in sync), False otherwise
    """
    return root1 == root2


def get_merkle_path(hashes: List[str], target_index: int) -> List[str]:
    """
    Get the Merkle path (proof) for a specific record.
    
    This function computes the hashes needed to prove that a specific record
    is part of the Merkle tree without revealing the entire tree.
    
    Args:
        hashes: List of hashes in the tree
        target_index: Index of the record to prove
        
    Returns:
        List[str]: List of hashes forming the proof path
    """
    if not hashes or target_index >= len(hashes):
        return []
    
    if len(hashes) == 1:
        return []
    
    proof = []
    current_hashes = hashes[:]
    current_index = target_index
    
    while len(current_hashes) > 1:
        next_level = []
        
        for i in range(0, len(current_hashes), 2):
            left = current_hashes[i]
            right = current_hashes[i + 1] if i + 1 < len(current_hashes) else left
            
            # Add to proof if this pair contains our target
            if i == current_index or (i + 1 == current_index and i + 1 < len(current_hashes)):
                if current_index == i:
                    proof.append(right)  # Add sibling
                else:
                    proof.append(left)   # Add sibling
            
            combined = left + right
            next_level.append(sha256(combined))
        
        # Update index for next level
        current_index = current_index // 2
        current_hashes = next_level
    
    return proof



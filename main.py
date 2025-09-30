"""
Main entry point for the distributed SQLite ledger demonstration.

This module consolidates all the example code from ledger.py, merkle.py, and node.py
to demonstrate the complete functionality of the distributed immutable ledger system.
"""

import os
import sqlite3
from ledger import init_db, add_record, get_all_records, get_record_count
from merkle import sha256, compute_merkle_root, merkle_root, get_merkle_path
from node import Node, compare_network


def demo_ledger_operations():
    """Demonstrate basic ledger operations."""
    print("=== Ledger Module Demo ===")
    
    # Initialize a database
    db_file = "demo_ledger.db"
    conn = init_db(db_file)
    print(f"✅ Initialized ledger database: {db_file}")
    
    # Add some records
    records = [
        "User login: alice@example.com",
        "Transaction: $100 transfer to bob",
        "System event: backup completed",
        "User action: profile updated"
    ]
    
    print("\n📝 Adding records to ledger:")
    for i, data in enumerate(records, 1):
        record_id = add_record(conn, data)
        print(f"   {i}. Added record {record_id}: {data}")
    
    # Display all records
    print(f"\n📊 Total records in ledger: {get_record_count(conn)}")
    print("\n📋 All records:")
    all_records = get_all_records(conn)
    for record in all_records:
        record_id, timestamp, data, record_hash = record
        print(f"   ID {record_id}: {data}")
        print(f"      Timestamp: {timestamp}")
        print(f"      Hash: {record_hash[:16]}...{record_hash[-16:]}")
    
    # Clean up
    conn.close()
    print(f"\n🧹 Closed database connection")
    
    # Clean up the demo database file
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️  Removed demo database: {db_file}")


def demo_merkle_operations():
    """Demonstrate Merkle tree operations."""
    print("\n=== Merkle Tree Module Demo ===")
    
    # Example 1: Basic Merkle root computation
    print("\n🌳 Example 1: Computing Merkle root from hash list")
    test_hashes = [
        sha256("record1"),
        sha256("record2"), 
        sha256("record3"),
        sha256("record4")
    ]
    
    print(f"Input hashes ({len(test_hashes)}):")
    for i, h in enumerate(test_hashes):
        print(f"   {i}: {h[:16]}...{h[-16:]}")
    
    merkle_root_hash = compute_merkle_root(test_hashes)
    print(f"\nMerkle root: {merkle_root_hash}")
    
    # Example 2: Merkle path (proof) generation
    print(f"\n🔍 Example 2: Generating Merkle proof for record at index 1")
    proof = get_merkle_path(test_hashes, 1)
    print(f"Proof path ({len(proof)} hashes):")
    for i, hash_val in enumerate(proof):
        print(f"   {i}: {hash_val[:16]}...{hash_val[-16:]}")
    
    # Example 3: Working with a SQLite ledger
    print(f"\n💾 Example 3: Computing Merkle root from SQLite ledger")
    
    # Create a temporary ledger
    db_file = "demo_merkle.db"
    conn = init_db(db_file)
    
    # Add some test records
    test_data = [
        "Transaction: Alice pays Bob $50",
        "Transaction: Bob pays Charlie $25", 
        "Transaction: Charlie pays Alice $10"
    ]
    
    print("Adding records to ledger:")
    for data in test_data:
        record_id = add_record(conn, data)
        print(f"   Added record {record_id}: {data}")
    
    # Compute Merkle root from the ledger
    ledger_root = merkle_root(conn)
    print(f"\nLedger Merkle root: {ledger_root}")
    
    # Add another record and see how the root changes
    print(f"\nAdding another record...")
    add_record(conn, "Transaction: Alice pays Dave $5")
    new_root = merkle_root(conn)
    print(f"New Merkle root: {new_root}")
    print(f"Root changed: {ledger_root != new_root}")
    
    # Clean up
    conn.close()
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"\n🗑️  Cleaned up demo database: {db_file}")


def demo_node_operations():
    """Demonstrate node operations and network comparison."""
    print("\n=== Node Module Demo ===")
    
    # Example 1: Single node operations
    print("\n🖥️  Example 1: Single node operations")
    
    # Create and initialize a node
    node1 = Node("Node-Alice", "alice_ledger.db")
    node1.initialize()
    print(f"✅ Created and initialized: {node1}")
    
    # Add some events
    events = [
        "User login: alice@example.com",
        "Transaction: Alice pays Bob $100",
        "System: Backup completed",
        "User: Profile updated"
    ]
    
    print("\n📝 Adding events to node:")
    for event in events:
        record_id = node1.add_event(event)
        print(f"   Added event {record_id}: {event}")
    
    # Show node status
    print(f"\n📊 Node status:")
    node1.print_status()
    
    # Example 2: Multiple nodes comparison
    print("\n🔄 Example 2: Multiple nodes comparison")
    
    # Create second node with same data
    node2 = Node("Node-Bob", "bob_ledger.db")
    node2.initialize()
    
    # Add same events to second node
    for event in events:
        node2.add_event(event)
    
    print("Created second node with identical data")
    
    # Compare the nodes
    comparison = node1.compare(node2)
    print(f"\n🔍 Node comparison results:")
    print(f"   Identical: {comparison['identical']}")
    print(f"   Node 1 records: {comparison['records_self']}")
    print(f"   Node 2 records: {comparison['records_other']}")
    print(f"   Divergence: {comparison['divergence_type']}")
    print(f"   Node 1 root: {comparison['root_self'][:16]}...{comparison['root_self'][-16:]}")
    print(f"   Node 2 root: {comparison['root_other'][:16]}...{comparison['root_other'][-16:]}")
    
    # Example 3: Network with diverged nodes
    print(f"\n🌐 Example 3: Network with diverged nodes")
    
    # Create third node with different data
    node3 = Node("Node-Charlie", "charlie_ledger.db")
    node3.initialize()
    
    # Add different events
    different_events = [
        "User login: charlie@example.com",
        "Transaction: Charlie pays Alice $50",
        "System: Cache cleared"
    ]
    
    for event in different_events:
        node3.add_event(event)
    
    print("Created third node with different data")
    
    # Compare network
    network = [node1, node2, node3]
    network_analysis = compare_network(network)
    
    print(f"\n📈 Network analysis:")
    print(f"   Total nodes: {network_analysis['total_nodes']}")
    print(f"   Synced nodes: {network_analysis['synced_nodes']}")
    print(f"   Sync percentage: {network_analysis['sync_percentage']:.1f}%")
    print(f"   Network healthy: {network_analysis['network_healthy']}")
    print(f"   Sync groups: {network_analysis['sync_groups']}")
    
    # Show individual node statuses
    print(f"\n📋 Individual node statuses:")
    for node in network:
        node.print_status()
    
    # Example 4: Context manager usage
    print(f"\n🔧 Example 4: Context manager usage")
    
    with Node("Node-Dave", "dave_ledger.db") as node4:
        node4.add_event("Context manager test event")
        print(f"Node 4 record count: {node4.get_record_count()}")
        print(f"Node 4 Merkle root: {node4.get_merkle_root()[:16]}...{node4.get_merkle_root()[-16:]}")
    print("Node 4 automatically closed via context manager")
    
    # Clean up example databases
    print(f"\n🧹 Cleaning up example databases...")
    db_files = ["alice_ledger.db", "bob_ledger.db", "charlie_ledger.db", "dave_ledger.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"   Removed: {db_file}")


def main():
    """Main entry point that runs all demonstrations."""
    print("🚀 Distributed SQLite Immutable Ledger Demo")
    print("=" * 50)
    
    try:
        # Run all demonstrations
        demo_ledger_operations()
        demo_merkle_operations()
        demo_node_operations()
        
        print("\n✅ All demonstrations completed successfully!")
        print("\nThis system demonstrates:")
        print("  • Immutable record storage in SQLite")
        print("  • Merkle tree cryptographic fingerprints")
        print("  • Distributed node comparison and sync detection")
        print("  • Network health analysis")
        
    except (OSError, sqlite3.Error, RuntimeError) as e:
        print(f"\n❌ Error during demonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

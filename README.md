# Distributed SQLite as an Immutable Record

> **Blog Post**: [Distributed SQLite as an Immutable Record](https://stephencollins.tech/posts/how-to-use-distributed-sqlite-and-merkle-trees-to-detect-divergence)

This repository demonstrates how to use SQLite databases as distributed, immutable ledgers with Merkle tree fingerprints for detecting divergence across peers. It's a practical implementation showing concepts used in Git, blockchain networks, and distributed databases.

## 🎯 What This Demo Shows

This project simulates multiple SQLite databases (peers) each maintaining an append-only ledger, and demonstrates how to compute and compare Merkle roots across peers to detect divergence. Key concepts include:

- **Immutable Records**: Once written, ledger entries cannot be modified
- **Merkle Trees**: Cryptographic fingerprints that change if any data changes
- **Divergence Detection**: Efficient comparison of ledger states across peers
- **Distributed Consensus**: How peers can detect when they're out of sync

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (optional, for easier execution)

### Installation

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone this repository
git clone git@github.com:stephenc222/example-distributed-sqlite-immutable-record.git
cd example-distributed-sqlite-immutable-record

# No external dependencies needed - uses only Python standard library!

# Database files will be created in the db/ directory when you run examples
```

### Running the Demo

**Quick Start:**
```bash
# Run the complete demonstration
uv run main.py
```

## 📋 What the Demo Shows

The `main.py` demonstration includes three comprehensive sections:

### 📝 **Ledger Operations Demo**
- **Purpose**: Basic immutable record storage and retrieval
- **Shows**: SQLite database initialization, record addition, data integrity
- **Best for**: Understanding the foundation layer
- **Duration**: ~10 seconds

### 🌳 **Merkle Tree Demo**
- **Purpose**: Cryptographic fingerprint computation and comparison
- **Shows**: Merkle root calculation, proof generation, change detection
- **Best for**: Understanding cryptographic verification
- **Duration**: ~15 seconds

### 🖥️ **Node Network Demo**
- **Purpose**: Distributed node simulation and network analysis
- **Shows**: Node comparison, divergence detection, sync group analysis
- **Best for**: Understanding distributed systems concepts
- **Duration**: ~30 seconds

### 🎯 **Complete Demo**
- **Purpose**: Run all demonstrations in sequence
- **Shows**: Complete feature overview from basic operations to network analysis
- **Best for**: Comprehensive understanding of all capabilities
- **Duration**: ~1 minute

## 📊 Example Output

### Complete Demo Output

```
🚀 Distributed SQLite Immutable Ledger Demo
==================================================
=== Ledger Module Demo ===
✅ Initialized ledger database: demo_ledger.db

📝 Adding records to ledger:
   1. Added record 1: User login: alice@example.com
   2. Added record 2: Transaction: $100 transfer to bob
   3. Added record 3: System event: backup completed
   4. Added record 4: User action: profile updated

📊 Total records in ledger: 4

📋 All records:
   ID 1: User login: alice@example.com
      Timestamp: 1759157370.696806
      Hash: 70a63d0d2a762b4d...f4d64b4ee1c830fa
   ID 2: Transaction: $100 transfer to bob
      Timestamp: 1759157370.6971421
      Hash: 3616449607f47c84...7b402083766f4651

=== Merkle Tree Module Demo ===

🌳 Example 1: Computing Merkle root from hash list
Input hashes (4):
   0: ed003a8f4ae177a3...2d7b7c138a2fa850
   1: 9204d2298aa78feb...8f7a4c8c6807f02b

Merkle root: 351f9945032c9bbcae2b54fe31a7414c5e7c39ee5fbd959df43946cab706fd38

🔍 Example 2: Generating Merkle proof for record at index 1
Proof path (2 hashes):
   0: ed003a8f4ae177a3...2d7b7c138a2fa850
   1: 7ab54753837ac043...0c185c0984b33492

=== Node Module Demo ===

🖥️  Example 1: Single node operations
✅ Created and initialized: Node(name='Node-Alice', db_file='alice_ledger.db', status='initialized')

📝 Adding events to node:
   Added event 1: User login: alice@example.com
   Added event 2: Transaction: Alice pays Bob $100

📊 Node status:
📊 Node: Node-Alice
   Database: alice_ledger.db
   Status: Active
   Records: 4
   Merkle Root: be40c26d7ed98dd9...5ab5fe2549a47dfb

🔄 Example 2: Multiple nodes comparison
🔍 Node comparison results:
   Identical: True
   Node 1 records: 4
   Node 2 records: 4
   Divergence: None - nodes are identical

🌐 Example 3: Network with diverged nodes
📈 Network analysis:
   Total nodes: 3
   Synced nodes: 2
   Sync percentage: 66.7%
   Network healthy: False
   Sync groups: [['Node-Alice', 'Node-Bob'], ['Node-Charlie']]

✅ All demonstrations completed successfully!

This system demonstrates:
  • Immutable record storage in SQLite
  • Merkle tree cryptographic fingerprints
  • Distributed node comparison and sync detection
  • Network health analysis
```

## 🏗️ Architecture

### Core Modules

- **`ledger.py`**: SQLite database management and record operations
- **`merkle.py`**: Merkle tree computation and root comparison  
- **`node.py`**: Object-oriented Node class for clean encapsulation
- **`main.py`**: Consolidated demonstration script showing all functionality

### Key Functions

**Basic Usage:**
```python
# Initialize a new ledger database
conn = init_db("db/mynode.db")

# Add a record to the ledger
record_id = add_record(conn, "User logged in: alice@example.com")

# Compute Merkle root for divergence detection
root = merkle_root(conn)

# Compare two ledger states
are_identical = compare_merkle_roots(root1, root2)
```

**Object-Oriented Usage:**
```python
# Using the Node class (recommended)
with Node("Alice", "db/alice.db") as node:
    node.add_event("User logged in: alice@example.com")
    root = node.get_merkle_root()
    
    # Compare with another node
    comparison = node.compare(other_node)
    print(f"Nodes identical: {comparison['identical']}")
```

## 🔬 How Merkle Trees Work

Merkle trees create cryptographic fingerprints of data that have these key properties:

1. **Deterministic**: Same data always produces the same root
2. **Avalanche Effect**: Any change anywhere produces a completely different root
3. **Efficient**: Only need to compare roots, not entire datasets
4. **Tamper-Proof**: Cannot change data without changing the root

```
Data: [A, B, C, D]           Merkle Tree:
                          Root = Hash(H1 + H2)
A ──→ Hash(A) ──┐         /              \
B ──→ Hash(B) ──┼── H1    H1              H2
C ──→ Hash(C) ──┘    = Hash(H(A)+H(B))  = Hash(H(C)+H(D))
D ──→ Hash(D) ────── H2
```

## 🌐 Real-World Connections

This demo illustrates concepts used in:

### Git Version Control
- Each commit is a Merkle tree root
- Branches diverge when they have different roots
- `git merge` detects conflicts by comparing trees

### Blockchain Networks
- Each block contains a Merkle root of transactions
- Nodes sync by comparing block hashes
- Consensus algorithms use Merkle proofs

### Distributed Databases
- Replicas detect divergence through checksums
- Conflict resolution uses data fingerprints
- Event sourcing maintains immutable logs

## 📁 Project Structure

```
├── README.md                 # This file
├── pyproject.toml           # Project configuration
├── main.py                  # Consolidated demonstration script
├── ledger.py                # Core ledger functionality
├── merkle.py                # Merkle tree implementation
├── node.py                  # Node class for object-oriented approach
├── tests/                   # Test files (if present)
│   ├── test_ledger.py       # Ledger functionality tests
│   ├── test_merkle.py       # Merkle tree tests
│   └── test_node.py         # Node class tests
├── db/                      # Database files (created by demo)
└── TASKS.md                 # Development roadmap
```

## 🧪 Testing

Run the demonstration to verify everything works:

```bash
# Run the complete demo
uv run main.py

# Or run directly with Python
python3 main.py

# Run tests (if you have pytest installed)
uv run pytest tests/ -v
```

**What the Demo Verifies:**
- ✅ Initialize databases successfully
- ✅ Show identical Merkle roots for identical data
- ✅ Detect divergence when data differs
- ✅ Handle node comparison and network analysis
- ✅ Clean up database files automatically
- ✅ Demonstrate all core functionality in sequence

## 🔧 Development

This project is designed to be lightweight and educational:

- **No external dependencies** - uses only Python standard library (except pytest for testing)
- **Self-contained** - each example is runnable independently  
- **Well-commented** - code explains concepts clearly
- **Thread-safe** - supports concurrent operations with proper SQLite handling
- **Extensible** - easy to add new examples or modify behavior
- **Well-tested** - comprehensive test suite with 50 tests

### Project Features

**Core Capabilities:**
- Immutable SQLite ledgers with append-only records
- Merkle tree computation for cryptographic fingerprints
- Divergence detection across distributed peers
- Thread-safe concurrent operations
- Object-oriented Node class for clean encapsulation
- Network-wide analysis and comparison

**Easy Execution:**
- Single `main.py` script with all demonstrations
- No external dependencies required
- Database files created and cleaned up automatically
- Comprehensive output showing all functionality

### Adding New Examples

1. Import the core modules: `from ledger import ...`, `from merkle import ...`, and `from node import ...`
2. Follow the pattern in `main.py` for creating demonstrations
3. Add your new demo function to `main.py` and call it from the `main()` function
4. Test your example by running `uv run main.py`

## 📚 Further Reading

- [Merkle Trees Explained](https://en.wikipedia.org/wiki/Merkle_tree)
- [Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Blockchain Merkle Trees](https://www.investopedia.com/news/how-merkle-trees-make-blockchain-more-secure/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 🤝 Contributing

This is a demonstration project, but suggestions and improvements are welcome! The goal is to make distributed systems concepts accessible through clear, runnable code.

## 📄 License

This project is open source and available under the MIT License.

---

*Built with ❤️ to make distributed systems concepts accessible through practical examples.*

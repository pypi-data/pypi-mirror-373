# Velocity.DB

A modern Python database abstraction library that simplifies database operations across multiple database engines. Velocity.DB provides a unified interface for PostgreSQL, MySQL, SQLite, and SQL Server, with features like transaction management, automatic connection pooling, and database-agnostic query building.

## Core Design Philosophy

Velocity.DB is built around two fundamental concepts that make database programming intuitive and safe:

### 1. One Transaction Per Function Block

Every database operation must be wrapped in a single transaction using the `@engine.transaction` decorator. This ensures:

- **Atomicity**: All operations in a function either succeed together or fail together
- **Consistency**: Database state remains valid even if errors occur
- **Isolation**: Concurrent operations don't interfere with each other
- **Automatic cleanup**: Transactions commit on success, rollback on any exception

```python
@engine.transaction  # This entire function is one atomic operation
def transfer_money(tx, from_account_id, to_account_id, amount):
    # If ANY operation fails, ALL changes are automatically rolled back
    from_account = tx.table('accounts').find(from_account_id)
    to_account = tx.table('accounts').find(to_account_id)
    
    from_account['balance'] -= amount  # This change...
    to_account['balance'] += amount    # ...and this change happen together or not at all
    
    # No need to manually commit - happens automatically when function completes
```

### 2. Rows as Python Dictionaries

Database rows behave exactly like Python dictionaries, using familiar syntax:

```python
@engine.transaction
def work_with_user(tx):
    user = tx.table('users').find(123)
    
    # Read like a dictionary
    name = user['name']
    email = user['email']
    
    # Update like a dictionary  
    user['name'] = 'New Name'
    user['status'] = 'active'
    
    # Check existence like a dictionary
    if 'phone' in user:
        phone = user['phone']
    
    # Get all data like a dictionary
    user_data = dict(user)  # or user.to_dict()
```

This design eliminates the need to learn ORM-specific syntax while maintaining the power and flexibility of direct database access.

## Features

- **Multi-database support**: PostgreSQL, MySQL, SQLite, SQL Server
- **Transaction management**: Decorator-based transaction handling with automatic rollback
- **Query builder**: Database-agnostic SQL generation with foreign key expansion
- **Connection pooling**: Automatic connection management and pooling
- **Type safety**: Comprehensive type hints and validation
- **Modern Python**: Built for Python 3.8+ with modern packaging

## Supported Databases

- **PostgreSQL** (via psycopg2)
- **MySQL** (via mysqlclient)
- **SQLite** (built-in sqlite3)
- **SQL Server** (via pytds)

## Installation

Install the base package:

```bash
pip install velocity-python
```

Install with database-specific dependencies:

```bash
# For PostgreSQL
pip install velocity-python[postgres]

# For MySQL  
pip install velocity-python[mysql]

# For SQL Server
pip install velocity-python[sqlserver]

# For all databases
pip install velocity-python[all]
```

## Project Structure

```
velocity-python/
├── src/velocity/           # Main package source code
├── tests/                  # Test suite
├── scripts/                # Utility scripts and demos
│   ├── run_tests.py       # Test runner script
│   ├── bump.py            # Version management
│   ├── demo_*.py          # Demo scripts
│   └── README.md          # Script documentation
├── docs/                   # Documentation
│   ├── TESTING.md         # Testing guide
│   ├── DUAL_FORMAT_DOCUMENTATION.md
│   ├── ERROR_HANDLING_IMPROVEMENTS.md
│   └── sample_error_email.html
├── Makefile               # Development commands
├── pyproject.toml         # Package configuration
└── README.md              # This file
```

## Development

### Running Tests

```bash
# Run unit tests (fast, no database required)
make test-unit

# Run integration tests (requires database)
make test-integration

# Run with coverage
make coverage

# Clean cache files
make clean
```

### Using Scripts

```bash
# Run the test runner directly
python scripts/run_tests.py --unit --verbose

# Version management
python scripts/bump.py

# See all available demo scripts
ls scripts/demo_*.py
```

## Quick Start

### Database Connection

```python
import velocity.db

# PostgreSQL
engine = velocity.db.postgres(
    host="localhost",
    port=5432,
    database="mydb",
    user="username",
    password="password"
)

# MySQL
engine = velocity.db.mysql(
    host="localhost",
    port=3306,
    database="mydb",
    user="username", 
    password="password"
)

# SQLite
engine = velocity.db.sqlite("path/to/database.db")

# SQL Server
engine = velocity.db.sqlserver(
    host="localhost",
    port=1433,
    database="mydb",
    user="username",
    password="password"
### Transaction Management

Velocity.DB enforces a "one transaction per function" pattern using the `@engine.transaction` decorator. The decorator intelligently handles transaction injection:

#### How Transaction Injection Works

The `@engine.transaction` decorator automatically provides a transaction object, but **you must declare `tx` as a parameter** in your function signature:

```python
@engine.transaction
def create_user_with_profile(tx):  # ← You MUST declare 'tx' parameter
    # The engine automatically creates and injects a Transaction object here
    # 'tx' is provided by the decorator, not by the caller
    
    user = tx.table('users').new()
    user['name'] = 'John Doe'
    user['email'] = 'john@example.com'
    
    profile = tx.table('profiles').new()
    profile['user_id'] = user['sys_id']
    profile['bio'] = 'Software developer'
    
    return user['sys_id']

# When you call the function, you DON'T pass the tx argument:
user_id = create_user_with_profile()  # ← No 'tx' argument needed
```

#### The Magic Behind the Scenes

The decorator uses Python's `inspect` module to:

1. **Check the function signature** - Looks for a parameter named `tx`
2. **Automatic injection** - If `tx` is declared but not provided by caller, creates a new Transaction
3. **Parameter positioning** - Inserts the transaction object at the correct position in the argument list
4. **Transaction lifecycle** - Automatically commits on success or rolls back on exceptions

```python
@engine.transaction
def update_user_settings(tx, user_id, settings):  # ← 'tx' must be declared
    # Engine finds 'tx' in position 0, creates Transaction, and injects it
    user = tx.table('users').find(user_id)
    user['settings'] = settings
    user['last_updated'] = datetime.now()

# Call without providing 'tx' - the decorator handles it:
update_user_settings(123, {'theme': 'dark'})  # ← Only pass your parameters
```

#### Advanced: Transaction Reuse

If you want multiple function calls to be part of the same transaction, **explicitly pass the `tx` object** to chain operations together:

```python
@engine.transaction
def create_user(tx, name, email):
    user = tx.table('users').new()
    user['name'] = name
    user['email'] = email
    return user['sys_id']

@engine.transaction
def create_profile(tx, user_id, bio):
    profile = tx.table('profiles').new()
    profile['user_id'] = user_id
    profile['bio'] = bio
    return profile['sys_id']

@engine.transaction
def create_user_with_profile(tx, name, email, bio):
    # All operations in this function use the SAME transaction
    
    # Pass 'tx' to keep this call in the same transaction
    user_id = create_user(tx, name, email)  # ← Pass 'tx' explicitly
    
    # Pass 'tx' to keep this call in the same transaction too
    profile_id = create_profile(tx, user_id, bio)  # ← Pass 'tx' explicitly
    
    # If ANY operation fails, ALL changes are rolled back together
    return user_id

# When you call the main function, don't pass tx - let the decorator provide it:
user_id = create_user_with_profile('John', 'john@example.com', 'Developer')
```

#### Two Different Transaction Behaviors

```python
# Scenario 1: SAME transaction (pass tx through)
@engine.transaction
def atomic_operation(tx):
    create_user(tx, 'John', 'john@example.com')     # ← Part of same transaction
    create_profile(tx, user_id, 'Developer')        # ← Part of same transaction
    # If profile creation fails, user creation is also rolled back

# Scenario 2: SEPARATE transactions (don't pass tx)
@engine.transaction  
def separate_operations(tx):
    create_user('John', 'john@example.com')         # ← Creates its own transaction
    create_profile(user_id, 'Developer')           # ← Creates its own transaction  
    # If profile creation fails, user creation is NOT rolled back
```

**Key Rule**: To include function calls in the same transaction, **always pass the `tx` parameter explicitly**. If you don't pass `tx`, each decorated function creates its own separate transaction.

#### Class-Level Transaction Decoration

You can also apply `@engine.transaction` to an entire class, which automatically wraps **all methods** that have `tx` in their signature:

```python
@engine.transaction
class UserService:
    """All methods with 'tx' parameter get automatic transaction injection"""
    
    def create_user(self, tx, name, email):
        # This method gets automatic transaction injection
        user = tx.table('users').new()
        user['name'] = name
        user['email'] = email
        return user['sys_id']
    
    def update_user(self, tx, user_id, **kwargs):
        # This method also gets automatic transaction injection
        user = tx.table('users').find(user_id)
        for key, value in kwargs.items():
            user[key] = value
        return user.to_dict()
    
    def get_user_count(self):
        # This method is NOT wrapped (no 'tx' parameter)
        return "This method runs normally without transaction injection"
    
    def some_utility_method(self, data):
        # This method is NOT wrapped (no 'tx' parameter)
        return data.upper()

# Usage - each method call gets its own transaction automatically:
service = UserService()

# Each call creates its own transaction:
user_id = service.create_user('John', 'john@example.com')  # ← Own transaction
user_data = service.update_user(user_id, status='active')  # ← Own transaction

# Methods without 'tx' work normally:
count = service.get_user_count()  # ← No transaction injection
```

#### Combining Class and Method Transactions

```python
@engine.transaction
class UserService:
    
    def create_user(self, tx, name, email):
        user = tx.table('users').new()
        user['name'] = name
        user['email'] = email
        return user['sys_id']
    
    def create_profile(self, tx, user_id, bio):
        profile = tx.table('profiles').new()
        profile['user_id'] = user_id
        profile['bio'] = bio
        return profile['sys_id']
    
    def create_user_with_profile(self, tx, name, email, bio):
        # Share transaction across method calls within the same class
        user_id = self.create_user(tx, name, email)      # ← Pass tx to share transaction
        profile_id = self.create_profile(tx, user_id, bio)  # ← Pass tx to share transaction
        return user_id

# Usage:
service = UserService()
# This creates ONE transaction for all operations:
user_id = service.create_user_with_profile('John', 'john@example.com', 'Developer')
```

**Key Benefits:**
- **Automatic transaction management**: No need to call `begin()`, `commit()`, or `rollback()`
- **Intelligent injection**: Engine inspects your function and provides `tx` automatically
- **Parameter flexibility**: `tx` can be in any position in your function signature
- **Transaction reuse**: Pass existing transactions to chain operations together
- **Clear boundaries**: Each function represents a complete business operation
- **Testable**: Easy to test since each function is a complete unit of work

**Important Rules:**
- **Must declare `tx` parameter**: The function signature must include `tx` as a parameter
- **Don't pass `tx` when calling from outside**: Let the decorator provide it automatically for new transactions
- **DO pass `tx` for same transaction**: To include function calls in the same transaction, explicitly pass the `tx` parameter
- **Class decoration**: `@engine.transaction` on a class wraps all methods that have `tx` in their signature
- **Selective wrapping**: Methods without `tx` parameter are not affected by class-level decoration
- **No `_tx` parameter**: Using `_tx` as a parameter name is forbidden (reserved)
- **Position matters**: The decorator injects `tx` at the exact position declared in your signature

### Table Operations

#### Creating Tables

```python
@engine.transaction
def create_tables(tx):
    # Create a users table
    users = tx.table('users')
    users.create()
    
    # Add columns by treating the row like a dictionary
    user = users.new()  # Creates a new row object
    user['name'] = 'Sample User'        # Sets column values using dict syntax
    user['email'] = 'user@example.com'  # No need for setters/getters
    user['created_at'] = datetime.now() # Python types automatically handled
    
    # The row is automatically saved when the transaction completes
```

#### Selecting Data

```python
@engine.transaction
def query_users(tx):
    users = tx.table('users')
    
    # Select all users - returns list of dict-like row objects
    all_users = users.select().all()
    for user in all_users:
        print(f"User: {user['name']} ({user['email']})")  # Dict syntax
    
    # Select with conditions
    active_users = users.select(where={'status': 'active'}).all()
    
    # Select specific columns
    names = users.select(columns=['name', 'email']).all()
    
    # Select with ordering and limits
    recent = users.select(
        orderby='created_at DESC',
        qty=10
    ).all()
    
    # Find single record - returns dict-like row object
    user = users.find({'email': 'john@example.com'})
    if user:
        # Access like dictionary
        user_name = user['name']
        user_id = user['sys_id']
        
        # Check existence like dictionary
        has_phone = 'phone' in user
        
        # Convert to regular dict if needed
        user_dict = user.to_dict()
    
    # Get by primary key
    user = users.find(123)  # Returns dict-like row object or None
```

#### Updating Data

```python
@engine.transaction
def update_user(tx):
    users = tx.table('users')
    
    # Find and update using dictionary syntax
    user = users.find(123)  # Returns a row that behaves like a dict
    user['name'] = 'Updated Name'         # Direct assignment like a dict
    user['updated_at'] = datetime.now()   # No special methods needed
    
    # Check if columns exist before updating
    if 'phone' in user:
        user['phone'] = '+1-555-0123'
    
    # Get current values like a dictionary
    current_status = user.get('status', 'unknown')
    
    # Bulk update using where conditions
    users.update(
        {'status': 'inactive'},           # What to update (dict format)
        where={'<last_login': '2023-01-01'}  # Condition using operator prefix
    )
```

#### Inserting Data

```python
@engine.transaction
def create_users(tx):
    users = tx.table('users')
    
    # Method 1: Create new row and populate like a dictionary
    user = users.new()  # Creates empty row object
    user['name'] = 'New User'           # Assign values using dict syntax
    user['email'] = 'new@example.com'   # 
    # Row automatically saved when transaction completes
    
    # Method 2: Insert with dictionary data directly
    user_id = users.insert({
        'name': 'Another User',
        'email': 'another@example.com'
    })
    
    # Method 3: Upsert (insert or update) using dictionary syntax
    users.upsert(
        {'name': 'John Doe', 'status': 'active'},  # Data to insert/update
        {'email': 'john@example.com'}              # Matching condition
    )
```

#### Deleting Data

```python
@engine.transaction
def delete_users(tx):
    users = tx.table('users')
    
    # Delete single record
    user = users.find(123)
    user.delete()
    
    # Delete with conditions
    users.delete(where={'status': 'inactive'})
    
    # Truncate table
    users.truncate()
    
    # Drop table
    users.drop()
```

### Advanced Queries

#### Foreign Key Navigation

Velocity.DB supports automatic foreign key expansion using pointer syntax:

```python
@engine.transaction  
def get_user_with_profile(tx):
    users = tx.table('users')
    
    # Automatic join via foreign key
    users_with_profiles = users.select(
        columns=['name', 'email', 'profile_id>bio', 'profile_id>avatar_url'],
        where={'status': 'active'}
    ).all()
```

#### Complex Conditions

Velocity.DB supports various where clause formats:

```python
@engine.transaction
def complex_queries(tx):
    users = tx.table('users')
    
    # Dictionary format with operator prefixes
    results = users.select(where={
        'status': 'active',          # Equals (default)
        '>=created_at': '2023-01-01',  # Greater than or equal
        '><age': [18, 65],           # Between
        '%email': '@company.com',    # Like
        '!status': 'deleted'         # Not equal
    }).all()
    
    # List of tuples format for complex predicates
    results = users.select(where=[
        ('status = %s', 'active'),
        ('priority = %s OR urgency = %s', ('high', 'critical'))
    ]).all()
    
    # Raw string format
    results = users.select(where="status = 'active' AND age >= 18").all()
```

**Available Operators:**

| Operator | SQL Equivalent | Example Usage | Description |
|----------|----------------|---------------|-------------|
| `=` (default) | `=` | `{'name': 'John'}` | Equals (default when no operator specified) |
| `>` | `>` | `{'>age': 18}` | Greater than |
| `<` | `<` | `{'<score': 100}` | Less than |
| `>=` | `>=` | `{'>=created_at': '2023-01-01'}` | Greater than or equal |
| `<=` | `<=` | `{'<=updated_at': '2023-12-31'}` | Less than or equal |
| `!` | `<>` | `{'!status': 'deleted'}` | Not equal |
| `!=` | `<>` | `{'!=status': 'deleted'}` | Not equal (alternative) |
| `<>` | `<>` | `{'<>status': 'deleted'}` | Not equal (SQL style) |
| `%` | `LIKE` | `{'%email': '@company.com'}` | Like pattern matching |
| `!%` | `NOT LIKE` | `{'!%name': 'test%'}` | Not like pattern matching |
| `><` | `BETWEEN` | `{'><age': [18, 65]}` | Between two values (inclusive) |
| `!><` | `NOT BETWEEN` | `{'!><score': [0, 50]}` | Not between two values |
```

#### Aggregations and Grouping

```python
@engine.transaction
def analytics(tx):
    orders = tx.table('orders')
    
    # Count records
    total_orders = orders.count()
    recent_orders = orders.count(where={'>=created_at': '2023-01-01'})
    
    # Aggregations
    stats = orders.select(
        columns=['COUNT(*) as total', 'SUM(amount) as revenue', 'AVG(amount) as avg_order'],
        where={'status': 'completed'},
        groupby='customer_id'
    ).all()
```

### Raw SQL

When you need full control, execute raw SQL. The `tx.execute()` method returns a **Result object** that provides flexible data transformation:

```python
@engine.transaction
def raw_queries(tx):
    # Execute raw SQL - returns a Result object
    result = tx.execute("""
        SELECT u.name, u.email, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.status = %s
        GROUP BY u.id, u.name, u.email
        HAVING COUNT(o.id) > %s
    """, ['active', 5])
    
    # Multiple ways to work with the Result object:
    
    # Get all rows as list of dictionaries (default)
    rows = result.all()
    for row in rows:
        print(f"User: {row['name']} ({row['email']}) - {row['order_count']} orders")
    
    # Or iterate one row at a time
    for row in result:
        print(f"User: {row['name']}")
    
    # Transform data format
    result.as_tuple().all()        # List of tuples
    result.as_list().all()         # List of lists  
    result.as_json().all()         # List of JSON strings
    result.as_named_tuple().all()  # List of (name, value) pairs
    
    # Get single values
    total = tx.execute("SELECT COUNT(*) FROM users").scalar()
    
    # Get simple list of single column values
    names = tx.execute("SELECT name FROM users").as_simple_list().all()
    
    # Get just the first row
    first_user = tx.execute("SELECT * FROM users LIMIT 1").one()
```

#### Result Object Methods

The **Result object** returned by `tx.execute()` provides powerful data transformation capabilities:

| Method | Description | Returns |
|--------|-------------|---------|
| `.all()` | Get all rows at once | `List[Dict]` (default) or transformed format |
| `.one(default=None)` | Get first row only | `Dict` or `default` if no rows |
| `.scalar(default=None)` | Get first column of first row | Single value or `default` |
| `.batch(qty=1)` | Iterate in batches | Generator yielding lists of rows |
| **Data Format Transformations:** |
| `.as_dict()` | Rows as dictionaries (default) | `{'column': value, ...}` |
| `.as_tuple()` | Rows as tuples | `(value1, value2, ...)` |
| `.as_list()` | Rows as lists | `[value1, value2, ...]` |
| `.as_json()` | Rows as JSON strings | `'{"column": "value", ...}'` |
| `.as_named_tuple()` | Rows as name-value pairs | `[('column', value), ...]` |
| `.as_simple_list(pos=0)` | Extract single column | `value` (from position pos) |
| **Utility Methods:** |
| `.headers` | Get column names | `['col1', 'col2', ...]` |
| `.close()` | Close the cursor | `None` |
| `.enum()` | Add row numbers | `(index, row)` tuples |

```python
@engine.transaction  
def result_examples(tx):
    # Different output formats for the same query
    result = tx.execute("SELECT name, email FROM users LIMIT 3")
    
    # As dictionaries (default)
    dicts = result.as_dict().all()
    # [{'name': 'John', 'email': 'john@example.com'}, ...]
    
    # As tuples  
    tuples = result.as_tuple().all()
    # [('John', 'john@example.com'), ...]
    
    # As JSON strings
    json_rows = result.as_json().all()  
    # ['{"name": "John", "email": "john@example.com"}', ...]
    
    # Just email addresses
    emails = result.as_simple_list(1).all()  # Position 1 = email column
    # ['john@example.com', 'jane@example.com', ...]
    
    # With row numbers
    numbered = result.enum().all()
    # [(0, {'name': 'John', 'email': 'john@example.com'}), ...]
```

## Automatic Schema Evolution

One of Velocity.DB's most powerful features is **automatic table and column creation**. The library uses decorators to catch database schema errors and automatically evolve your schema as your code changes.

### How Automatic Creation Works

Velocity.DB uses the `@create_missing` decorator on key table operations. When you try to:

- **Insert data** with new columns
- **Update rows** with new columns  
- **Query tables** that don't exist
- **Reference columns** that don't exist

The library automatically:

1. **Catches the database error** (table missing, column missing)
2. **Analyzes the data** you're trying to work with
3. **Creates the missing table/columns** with appropriate types
4. **Retries the original operation** seamlessly

```python
@engine.transaction
def create_user_profile(tx):
    # This table and columns don't exist yet - that's OK!
    users = tx.table('users')  # Table will be created automatically
    
    # Insert data with new columns - they'll be created automatically
    user = users.new()
    user['name'] = 'John Doe'           # VARCHAR column created automatically
    user['age'] = 28                    # INTEGER column created automatically  
    user['salary'] = 75000.50           # NUMERIC column created automatically
    user['is_active'] = True            # BOOLEAN column created automatically
    user['bio'] = 'Software engineer'   # TEXT column created automatically
    
    # The table and all columns are now created and data is inserted
    return user['sys_id']

# Call this function - table and columns created seamlessly
user_id = create_user_profile()
```

### Type Inference

Velocity.DB automatically infers SQL types from Python values:

| Python Type | SQL Type (PostgreSQL) | SQL Type (MySQL) | SQL Type (SQLite) |
|-------------|------------------------|-------------------|-------------------|
| `str` | `TEXT` | `TEXT` | `TEXT` |
| `int` | `BIGINT` | `BIGINT` | `INTEGER` |
| `float` | `NUMERIC(19,6)` | `DECIMAL(19,6)` | `REAL` |
| `bool` | `BOOLEAN` | `BOOLEAN` | `INTEGER` |
| `datetime` | `TIMESTAMP` | `DATETIME` | `TEXT` |
| `date` | `DATE` | `DATE` | `TEXT` |

### Progressive Schema Evolution

Your schema evolves naturally as your application grows:

```python
# Week 1: Start simple
@engine.transaction
def create_basic_user(tx):
    users = tx.table('users')
    user = users.new()
    user['name'] = 'Alice'
    user['email'] = 'alice@example.com'
    return user['sys_id']

# Week 2: Add more fields
@engine.transaction  
def create_detailed_user(tx):
    users = tx.table('users')
    user = users.new()
    user['name'] = 'Bob'
    user['email'] = 'bob@example.com'
    user['phone'] = '+1-555-0123'      # New column added automatically
    user['department'] = 'Engineering'  # Another new column added automatically
    user['start_date'] = date.today()   # Date column added automatically
    return user['sys_id']

# Week 3: Even more fields
@engine.transaction
def create_full_user(tx):
    users = tx.table('users')  
    user = users.new()
    user['name'] = 'Carol'
    user['email'] = 'carol@example.com'
    user['phone'] = '+1-555-0124'
    user['department'] = 'Marketing'
    user['start_date'] = date.today()
    user['salary'] = 85000.00          # Salary column added automatically
    user['is_manager'] = True          # Boolean column added automatically
    user['notes'] = 'Excellent performer'  # Notes column added automatically
    return user['sys_id']
```

### Behind the Scenes

The `@create_missing` decorator works by:

```python
# This is what happens automatically:
def create_missing(func):
    def wrapper(self, *args, **kwds):
        try:
            # Try the original operation
            return func(self, *args, **kwds)
        except DbTableMissingError:
            # Table doesn't exist - create it from the data
            data = extract_data_from_args(args, kwds)
            self.create(data)  # Create table with inferred columns
            return func(self, *args, **kwds)  # Retry operation
        except DbColumnMissingError:
            # Column doesn't exist - add it to the table
            data = extract_data_from_args(args, kwds)
            self.alter(data)  # Add missing columns
            return func(self, *args, **kwds)  # Retry operation
    return wrapper
```

### Which Operations Are Protected

These table operations automatically create missing schema elements:

- `table.insert(data)` - Creates table and columns
- `table.update(data, where)` - Creates missing columns in data
- `table.merge(data, pk)` - Creates table and columns (upsert)
- `table.alter_type(column, type)` - Creates column if missing
- `table.alter(columns)` - Adds missing columns

### Manual Schema Control

If you prefer explicit control, you can disable automatic creation:

```python
@engine.transaction
def explicit_schema_control(tx):
    users = tx.table('users')
    
    # Check if table exists before using it
    if not users.exists():
        users.create({
            'name': str,
            'email': str,
            'age': int,
            'is_active': bool
        })
    
    # Check if column exists before using it
    if 'phone' not in users.column_names():
        users.alter({'phone': str})
    
    # Now safely use the table
    user = users.new()
    user['name'] = 'David'
    user['email'] = 'david@example.com'
    user['phone'] = '+1-555-0125'
```

### Development Benefits

**For Development:**
- **Rapid prototyping**: Focus on business logic, not database setup
- **Zero configuration**: No migration scripts or schema files needed
- **Natural evolution**: Schema grows with your application

**For Production:**
- **Controlled deployment**: Use `sql_only=True` to generate schema changes for review
- **Safe migrations**: Test automatic changes in staging environments
- **Backwards compatibility**: New columns are added, existing data preserved

```python
# Generate SQL for review without executing
@engine.transaction
def preview_schema_changes(tx):
    users = tx.table('users')
    
    # See what SQL would be generated
    sql, vals = users.insert({
        'name': 'Test User',
        'new_field': 'New Value'
    }, sql_only=True)
    
    print("SQL that would be executed:")
    print(sql)
    # Shows: ALTER TABLE users ADD COLUMN new_field TEXT; INSERT INTO users...
```

**Key Benefits:**
- **Zero-friction development**: Write code, not schema migrations
- **Type-safe evolution**: Python types automatically map to appropriate SQL types
- **Production-ready**: Generate reviewable SQL for controlled deployments
- **Database-agnostic**: Works consistently across PostgreSQL, MySQL, SQLite, and SQL Server

## Error Handling

The "one transaction per function" design automatically handles rollbacks on exceptions:

```python
@engine.transaction
def safe_transfer(tx, from_id, to_id, amount):
    try:
        # Multiple operations that must succeed together
        from_account = tx.table('accounts').find(from_id)
        to_account = tx.table('accounts').find(to_id)
        
        # Work with rows like dictionaries
        if from_account['balance'] < amount:
            raise ValueError("Insufficient funds")
            
        from_account['balance'] -= amount  # This change...
        to_account['balance'] += amount    # ...and this change are atomic
        
        # If any operation fails, entire transaction rolls back automatically
        
    except Exception as e:
        # Transaction automatically rolled back - no manual intervention needed
        logger.error(f"Transfer failed: {e}")
        raise  # Re-raise to let caller handle the business logic

@engine.transaction
def create_user_with_validation(tx, user_data):
    # Each function is a complete business operation
    users = tx.table('users')
    
    # Check if user already exists
    existing = users.find({'email': user_data['email']})
    if existing:
        raise ValueError("User already exists")
    
    # Create new user using dictionary interface
    user = users.new()
    user['name'] = user_data['name']
    user['email'] = user_data['email']
    user['created_at'] = datetime.now()
    
    # If we reach here, everything commits automatically
    return user['sys_id']
```

**Key Benefits of Transaction-Per-Function:**
- **Automatic rollback**: Any exception undoes all changes in that function
- **Clear error boundaries**: Each function represents one business operation
- **No resource leaks**: Connections and transactions are always properly cleaned up
- **Predictable behavior**: Functions either complete fully or have no effect

## Development

### Setting up for Development

This is currently a private repository. If you have access to the repository:

```bash
git clone <repository-url>
cd velocity-python
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking  
mypy src/

# Linting
flake8 src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

This is currently a private repository and we are not accepting public contributions at this time. However, this may change in the future based on community interest and project needs.

If you are interested in contributing to Velocity.DB, please reach out to discuss potential collaboration opportunities.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

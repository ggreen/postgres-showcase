# PostgreSQL Transactions Workshop

## 🧠 Objective

Learn how PostgreSQL transactions work, why they are critical for consistency, and how to use them effectively.

---

## 📋 Prerequisites

- PostgreSQL installed (or use `bitnami/postgresql` in Docker/Podman)
- Basic SQL knowledge
- Access to `psql` or a SQL client

---

## 📚 Table of Contents

1. Introduction to Transactions
2. ACID Properties
3. `BEGIN`, `COMMIT`, and `ROLLBACK`
4. Nested Transactions with `SAVEPOINT`
5. Locking Behavior
6. Isolation Levels
7. Common Pitfalls
8. Exercises

---

## 1. 🔄 Introduction to Transactions

A **transaction** is a sequence of one or more SQL statements executed as a single unit of work.

**Why?**
- Ensures **data integrity**.
- Prevents **partial updates**.
- Supports **rollback on failure**.

---

## 2. 🔐 ACID Properties

| Property   | Description |
|------------|-------------|
| **Atomicity** | All operations succeed or none do. |
| **Consistency** | Database remains in a valid state. |
| **Isolation** | Transactions are independent. |
| **Durability** | Committed changes are saved permanently. |


---

## 3. 🧪 Basic Transaction Control

Run postgres 

```bash
podman run --rm -it --network=postgres \
  --name postgres \
  -e POSTGRESQL_USERNAME=postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  docker.io/bitnami/postgresql:latest
```

Start One terminal
```bash
podman exec -it postgres psql -U postgres -d postgres
```

Commit 

```sql
BEGIN;
-- Some SQL changes
COMMIT;
```

Or Roll back

```sql
BEGIN;
-- Some SQL changes
ROLLBACK;
```

## 4. 🧬 Savepoints for Partial Rollback

```sql
 BEGIN;
 -- Step 1
 SAVEPOINT step1;

-- Step 2 (fails)
ROLLBACK TO step1;

-- Retry or proceed
COMMIT;

```


```sql
CREATE SCHEMA company;
CREATE TABLE company.employees (
id SERIAL PRIMARY KEY,
name TEXT NOT NULL,
role TEXT,
hired_on DATE DEFAULT CURRENT_DATE
);
```



```shell
INSERT INTO company.employees (name, role) VALUES
('Alice', 'Engineer');

INSERT INTO company.employees (name, role) VALUES
('Mary', 'Developer');
```

Start Another Terminal
```bash
podman exec -it postgres psql -U postgres -d postgres
```

 Test locks with two terminal sessions
```sql
BEGIN;
UPDATE company.employees SET role = 'retired' WHERE name = 'Alice';
```

In another session, try:

```properties
podman run -p 7280:7280 cloudnativedata/jdbc-sql-console-app:0.0.4-SNAPSHOT --name=jdbc-sql-console-app --server.port=7280 --spring.datasource.url=jdbc:postgresql://host.docker.internal:5432/postgres --spring.datasource.username=postgres --spring.datasource.password=postgres
```

or java (must build the project first using maven)

```shell
java -jar applications/jdbc-sql-console-app/target/jdbc-sql-console-app-0.0.4-SNAPSHOT.jar --spring.datasource.url="jdbc:postgresql://localhost:5432/postgres" --spring.datasource.username=postgres --spring.datasource.password=postgres
```

Open URL

```shell
open http://localhost:7280
```


The following will result in a row level block

```sql
UPDATE company.employees SET role = 'promoted' WHERE name = 'Alice';
```



Commit in first terminal

```sql
COMMIT;
```

View update (role will equal promoted)

```sql
select * from company.employees;
```

Start in psql

```sql
BEGIN;
UPDATE company.employees SET role = 'Architect' WHERE name = 'Mary';
```

In another session (will NOT be locked)

```sql
UPDATE company.employees SET role = 'Manager' WHERE name = 'Alice';
```

Commit in first terminal

```sql
COMMIT;
```

```sql
select * from company.employees;
```


8. Exercises

   🧩 Exercise 1: Simple Transaction
```sql
   -- 1. Create a table
   CREATE TABLE company.accounts (
   id SERIAL PRIMARY KEY,
   name TEXT,
   balance INT
   );
```


```sql
-- 2. Insert two users
INSERT INTO company.accounts (name, balance) VALUES ('Alice', 1000), ('Bob', 500);

-- 3. Begin a transaction to transfer $100 from Alice to Bob
BEGIN;

UPDATE company.accounts SET balance = balance - 100 WHERE name = 'Alice';
UPDATE company.accounts SET balance = balance + 100 WHERE name = 'Bob';

-- 4. Commit the transaction
COMMIT;

-- 5. Verify the balances
SELECT * FROM company.accounts;
```


## 🧩 Exercise 2: Rollback on Error

```sql
BEGIN;

UPDATE company.accounts SET balance = balance - 200 WHERE name = 'Alice';
-- Simulate error
SELECT 1 / 0;

-- This won't run if above fails
UPDATE company.accounts SET balance = 9999 WHERE name = 'Bob';

-- Rollback everything
ROLLBACK;
```

Verify the balances did not change
```shell
SELECT * FROM company.accounts;
```
-----------

🧩 Exercise 3: Savepoint Use

```sql
BEGIN;

UPDATE company.accounts SET balance = balance - 50 WHERE name = 'Alice';
SAVEPOINT halfway;

-- Simulate mistake
UPDATE company.accounts SET balance = balance + 50000 WHERE name = 'Bob';

-- Realize mistake and roll back to halfway
ROLLBACK TO halfway;

-- Correct update
UPDATE company.accounts SET balance = balance + 50 WHERE name = 'Bob';

COMMIT;
```

Verify the balances did not change
```sql
SELECT * FROM company.accounts;
```


## 🧩 Exercise 4: Isolation Level Experiment

In two terminals:

In psql

```sql
BEGIN;
UPDATE company.accounts SET balance = 500 WHERE name = 'Alice';
COMMIT;
BEGIN;
UPDATE company.accounts SET balance = 999 WHERE name = 'Alice';
```


ANother Terminal or JDBC Console


```sql
BEGIN;
SELECT * FROM company.accounts WHERE name = 'Alice';
-- Don’t commit yet
```

Commit in first terminal

```sql
COMMIT;
```

Verify you can read commit from Terminal A

```shell
SELECT * FROM company.accounts;
```


-----------------
Observe behavior depending on isolation level.

✅ Summary
Use transactions to group operations safely.

Always handle errors.

Understand isolation to avoid race conditions.

6. 🏗️ Isolation Levels

PostgreSQL supports:

- READ COMMITTED (default)
- REPEATABLE READ 
- SERIALIZABLE


```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
-- Run your queries
COMMIT;
```



## Stop and remove the container


```shell
podman rm -f postgres pgadmin
```

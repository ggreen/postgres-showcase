# 🐘 Postgres as a Document Database using JSONB with Bitnami and Podman

## 🎯 Workshop Objective

Learn how to:
- Deploy Postgres using Bitnami's container image in Podman
- Use Postgres as a document database with `jsonb` columns
- Perform CRUD operations on `jsonb` data
- Utilize JSONB indexing for performance

---

## 📦 Prerequisites

- Linux/macOS system with Podman installed
- Basic knowledge of SQL

---

## 🚀 Step 1: Run Postgres (Bitnami) with Podman

```bash
podman run --rm -it \
  --name postgres \
  -e POSTGRESQL_USERNAME=postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  docker.io/bitnami/postgresql:latest
```


## 🔗 Step 2: Connect to PostgresSQL

```bash
podman exec -it postgres psql -U postgres -d postgres
```

## 🏗️ Step 3: Create a JSONB Table

```sql
Create schema docDB;
CREATE TABLE docDB.documents (
id SERIAL PRIMARY KEY,
data JSONB NOT NULL
);
```


## ✍️ Step 4: Insert JSON Documents
```sql
INSERT INTO docDB.documents (data) VALUES
('{"name": "Alice", "age": 30, "skills": ["SQL", "Python"]}'),
('{"name": "Bob", "age": 25, "skills": ["Go", "Docker"]}');
```


## 🔍 Step 5: Query JSONB Data
Get all docDB.documents

```sql
SELECT * FROM docDB.documents;
```

Filter by JSONB field

```sql
SELECT * FROM docDB.documents
WHERE data->>'name' = 'Alice';
```

Filter by array element

? operator answer question 
Does the string exist as a top-level key within the JSON value

```sql
SELECT * FROM docDB.documents
WHERE data->'skills' ? 'Docker';
```

## ⚡ Step 6: Index JSONB Fields

Improve performance with a GIN index:

```sql
CREATE INDEX idx_gin_data ON docDB.documents USING GIN (data);
```

## 🔄 Step 7: Update JSONB Data

```sql
UPDATE docDB.documents
SET data = jsonb_set(data, '{age}', '31')
WHERE data->>'name' = 'Alice';
```

Select with updated Age 31

```sql
SELECT * FROM docDB.documents
WHERE data->>'name' = 'Alice';
```


## ❌ Step 8: Delete Documents

```sql
DELETE FROM docDB.documents
WHERE data->>'name' = 'Bob';
```

🧪 Bonus: Store Nested JSON


```sql
INSERT INTO docDB.documents (data) VALUES
('{
"title": "Postgres as NoSQL",
"meta": {
"author": "John",
"tags": ["postgresql", "jsonb", "nosql"]
}
}');
```

Query nested key:

```sql
SELECT * FROM docDB.documents
WHERE data->'meta'->>'author' = 'John';
```

#  🧹 Cleanup (optional)


```bash
podman stop postgres
podman rm postgres
```

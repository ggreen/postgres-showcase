# Getting Started: SQL, Schema, and tables

## 🎯 Workshop Objective

By the end of this workshop, you will be able to:

- Run PostgreSQL using Bitnami’s container image with Podman
- Connect to the database using `psql`
- Understand schemas
- Create and query tables using SQL

---

## 📦 Prerequisites

- Podman installed (`brew install podman` or `dnf install podman`)
- PostgreSQL CLI (`psql`) installed
- Basic shell command familiarity

---


## 🚀 Step 1: Start PostgreSQL Using Bitnami and Podman


Create network

```shell
podman  network create postgres
```

```bash
podman run --rm -it --network=postgres \
  --name postgres \
  -e POSTGRESQL_USERNAME=postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  docker.io/bitnami/postgresql:latest
```
  
✅ This starts PostgreSQL with:


## 🔗 Step 2: Connect to PostgreSQL

In new terminal


```bash
podman exec -it postgres psql -U postgres -d postgres
```
Note: password=postgres

## 🧠 Step 3: Understanding Schema
What is a Schema?
A schema is like a namespace inside a database. It helps group related tables, views, and functions together.

List Current Schemas

```sql
\dn
```

You should see public — the default schema.

## 🏗️ Step 4: Create a Schema


```sql
CREATE SCHEMA company;
```


## 📋 Step 5: Create a Table

Inside the company Schema

```sql
CREATE TABLE company.employees (
id SERIAL PRIMARY KEY,
name TEXT NOT NULL,
role TEXT,
hired_on DATE DEFAULT CURRENT_DATE
);
```


Inside the company Schema

```sql
INSERT INTO company.employees (name, role) VALUES
('Alice', 'Engineer'),
('Bob', 'Manager'),
('Charlie', 'Analyst');
```

Insert Sample Data

```sql
INSERT INTO company.employees (name, role) VALUES
('Alice', 'Engineer'),
('Bob', 'Manager'),
('Charlie', 'Analyst');
```


## 🔍 Step 6: Query the Table

```sql
SELECT * FROM company.employees;
```

Or with explicit schema path:

```sql
SELECT name, role FROM company.employees WHERE role = 'Engineer';
```

## 📑 Step 7: List Tables and Describe Structure

```sql
\dt company.*
```

```sql
\d company.employees
```


## 🧹 Step 8: Optional pgadmin

Run pgadmin

```shell
podman run -p 6888:80 --name=pgadmin --network postgres\
    -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=SuperSecret' \
    --rm -it dpage/pgadmin4
```

Open Pgadmin

```shell
open http://localhost:6888
```

Login
```properties
Email=user@domain.com
Password=SuperSecret
```


Register Server

```properties
name=postgres
hostname=postgres
username=postgres
password=postgres
```



## 🧹 Step 9: Clean Up


Exit psql:

```sql
\q
```

## Stop and remove the container


```shell
podman rm -f postgres pgadmin
```








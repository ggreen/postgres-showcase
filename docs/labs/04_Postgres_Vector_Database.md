## Database Setup and Data Loading

Follow these steps to set up your PostgreSQL database and load the Wikipedia articles data.

### Start PostgreSQL with pg_vector using Docker:

This command will pull the pgvector/pgvector:pg17 Docker image and start a PostgreSQL container. The database will be named postgres, the user postgres, and the password postgres. It will be accessible on port 5436 of your local machine.

```bash
podman run --rm -it --network=postgres \
  --name postgres \
  -e POSTGRESQL_USERNAME=postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  docker.io/bitnami/postgresql:latest
```

Start psql

```shell
podman exec -it postgres  psql -U postgres -d postgres  
```


## 📦 2. Install pgvector
Bitnami PostgreSQL image includes support for extensions like pgvector.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 🧠 3. Create a Table with Vector Column

```sql
Create schema ai;
CREATE TABLE ai.documents (
id SERIAL PRIMARY KEY,
content TEXT,
embedding VECTOR(3)  -- 3-dimensional for demo; real use = 1536, 768, etc.
);
```


## 📝 4. Insert Some Vector Data

```sql
INSERT INTO ai.documents (content, embedding) VALUES
('PostgreSQL is a powerful database',        '[0.1, 0.2, 0.3]'),
('AI vector search with pgvector',           '[0.05, 0.1, 0.2]'),
('Containers using Podman and Docker',       '[0.9, 0.1, 0.5]');
```

## 🔍 5. Perform a Vector Similarity Search
Use L2 (Euclidean) or cosine distance:

Find the closest match to this vector
```sql
SELECT id, content, embedding,
embedding <-> '[0.1, 0.2, 0.3]' AS distance
FROM ai.documents
ORDER BY embedding <-> '[0.1, 0.2, 0.3]'
LIMIT 3;
```

You can also use:

| Operator | Meaning         |
| -------- | --------------- |
| `<->`    | L2 (Euclidean)  |
| `<#>`    | Inner product   |
| `<=>`    | Cosine distance |



## ⚡ 6. Speed It Up with Indexing
Create an IVFFlat index (requires ANALYZE before use):

First analyze the table
```sql
ANALYZE ai.documents;
```

Then create the index (use 'l2', 'cosine', or 'ip')
```sql
CREATE INDEX ON ai.documents USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);  -- Tune depending on data volume
```

## 🧪 7. Example: Find Top-N Similar Embeddings

Enable timing

```psql
\timing
```

```sql
SELECT content, embedding <-> '[0.09, 0.21, 0.31]' AS score
FROM ai.documents
ORDER BY score ASC
LIMIT 1;
```

# Bonus - Activity

### Download the Wikipedia Articles Dataset:

This command downloads a zipped file containing the embedded Wikipedia articles.

```
mkdir -p runtime
wget -P runtime https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip
```


### Unzip the Dataset:

Extract the vector_database_wikipedia_articles_embedded.csv file from the downloaded zip archive.

```
cd runtime
unzip vector_database_wikipedia_articles_embedded.zip
```

### Connect to your PostgreSQL database:

You can connect using the psql command-line tool (you must have psql installed)

```bash
psql -d "postgres" -h localhost -U postgres
```
`

### Create the articles table:

This command defines the schema for your articles table, including the vector(1536) columns for embeddings.

```sql
Create schema news;
CREATE TABLE IF NOT EXISTS news.articles (
    id INTEGER NOT NULL PRIMARY KEY,
    url TEXT,
    title TEXT,
    content TEXT,
    title_vector vector(1536),
    content_vector vector(1536),
    vector_id INTEGER
);
```

### Create vector search indexes:

These indexes will significantly speed up your semantic search queries.

```
CREATE INDEX ON news.articles USING ivfflat (content_vector) WITH (lists = 1000);
```

```
CREATE INDEX ON news.articles USING ivfflat (title_vector) WITH (lists = 1000);
```

### Load the dataset into the articles table:

This command copies the data from your CSV file into the articles table. Ensure you run this from the directory where vector_database_wikipedia_articles_embedded.csv is located.

Copy data

```bash
psql -d "postgres" -h "localhost" -U "postgres" -c "\COPY news.articles (id, url, title, content, title_vector, content_vector, vector_id) FROM 'vector_database_wikipedia_articles_embedded.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');"
```

### Verify Data Loading (Optional):
You can run a simple query to check if the data has been loaded correctly.


```bash
psql -d "postgres" -h localhost -U postgres
```

```
SELECT id, url, title, SUBSTRING(content FROM 1 FOR 200) || '...' AS truncated_content
FROM news.articles
LIMIT 5;
```


### Find articles similar to a specific article (Recommendation/Related Articles):

```
WITH TargetArticle AS (
    SELECT content_vector
    FROM news.articles
    WHERE id = 12345 -- Replace with the ID of an article you're interested in
)
SELECT
    a.id,
    a.url,
    a.title,
    SUBSTRING(a.content FROM 1 FOR 150) || '...' AS truncated_content,
    1 - (a.content_vector <=> T.content_vector) AS similarity_score
FROM
    news.articles AS a, TargetArticle AS T
WHERE
    a.id != 12345 -- Exclude the target article itself
ORDER BY
    a.content_vector <=> T.content_vector
LIMIT 10;
```


#  🧹 Cleanup


```bash
podman rm -f postgres pgadmin
```

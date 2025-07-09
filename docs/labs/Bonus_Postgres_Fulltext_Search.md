
# Hands‑On Lab: PostgreSQL Full‑Text Search (FTS) with Podman Bitnami

Audience: Developers & DBAs new to PostgreSQL’s full‑text search

What you’ll learn

Starting PostgreSQL in a disposable Podman container (Bitnami image)

- Core FTS types & functions (tsvector, tsquery, to_tsquery, etc.)
- Creating GIN indexes for fast searching 
- Ranking, highlighting, and language configuration



1. Boot Postgres via Podman


```bash
podman run -d --name pgfts \
-e POSTGRESQL_USERNAME=admin \
-e POSTGRESQL_PASSWORD=secretpw \
-e POSTGRESQL_DATABASE=labdb \
-p 15432:5432 \
docker.io/bitnami/postgresql:latest```


Connect with psql
```bash
psql "postgresql://admin:secretpw@localhost:15432/labdb"
```


# 2. Crash‑Course: Key FTS Objects

| Object / Function                                           | Purpose                                 |
| ----------------------------------------------------------- | --------------------------------------- |
| `tsvector`                                                  | Indexed representation of document text |
| `tsquery`                                                   | Search term(s) with boolean operators   |
| `to_tsvector('english', text)`                              | Parse text → `tsvector`                 |
| `plainto_tsquery / phraseto_tsquery / websearch_to_tsquery` | Helper constructors                     |
| `@@` operator                                               | Match: `tsvector @@ tsquery`            |
| `ts_rank` / `ts_rank_cd`                                    | Relevance ranking                       |


# Setup

```sql
-- 3.1 Enable pg_trgm for similarity (optional but useful)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 3.2 A simple newspaper.articles table
CREATE schema newspaper;
CREATE TABLE newspaper.articles (
  id SERIAL PRIMARY KEY,
  title     TEXT NOT NULL,
  body      TEXT NOT NULL,
  body_tsv  TSVECTOR           -- generated column (v14+)
           GENERATED ALWAYS AS (
             to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))
           ) STORED
);

INSERT INTO newspaper.articles (title, body) VALUES
  ('Introducing PostgreSQL Full-Text Searching',
   'PostgreSQL offers powerful plain, phrase and proximity search capabilities.'),
  ('Running Postgres in Containers',
   'Containers like Podman and Docker make Postgres easy to spin up.'),
  ('Advanced Indexing with GIN and GiST',
   'Full‑text, JSONB, and more benefit from GIN indexes.');

```


4. Indexing for Speed

```sql
CREATE INDEX idx_articles_body_tsv ON newspaper.articles USING GIN (body_tsv);
```

GIN handles large inverted indexes efficiently.


5. Basic Searches

| Query       | Example                                                                  |
| ----------- | ------------------------------------------------------------------------ |
| Single word | `SELECT title FROM newspaper.articles WHERE body_tsv @@ to_tsquery('postgresql');` |
| Boolean AND | `... @@ to_tsquery('postgres & containers');`                            |
| Phrase      | `... @@ phraseto_tsquery('running postgres');`                           |
| Web‑style   | `... @@ websearch_to_tsquery('postgres OR "full text"');`                |

```sql
select * from newspaper.articles;
```

```sql
SELECT id, title, body
FROM   newspaper.articles
WHERE  body_tsv @@ to_tsquery('jsonb');
```

Search contain multiple words seperated by &

```sql
SELECT id, title, body
FROM   newspaper.articles
WHERE  body_tsv @@ to_tsquery('power & search');
```

Search two word next to next other

```sql
SELECT id, title, body
FROM   newspaper.articles
WHERE  body_tsv @@ to_tsquery('Full‑text <-> JSONB');
```

Search two words  separated by 1 word

```sql
SELECT id, title, body
FROM   newspaper.articles
WHERE  body_tsv @@ to_tsquery('proximity <2> capabilities');
```


View the search results ranking

```sql
SELECT id, title,
       ts_rank(body_tsv, to_tsquery('PostgreSQL'))
FROM   newspaper.articles
WHERE  body_tsv @@ to_tsquery('PostgreSQL')
ORDER  BY ts_rank DESC;

```

6. Highlighting Matches

```sql
SELECT title,
       ts_headline('english', body,
                   websearch_to_tsquery('PostgreSQL'),
                   'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=10')
FROM newspaper.articles
WHERE body_tsv @@ websearch_to_tsquery('PostgreSQL');
```

Returns HTML with <mark> tags you can render in a UI.
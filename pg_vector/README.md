## Database Setup and Data Loading

Follow these steps to set up your PostgreSQL database and load the Wikipedia articles data.

### Start PostgreSQL with pg_vector using Docker:

This command will pull the pgvector/pgvector:pg17 Docker image and start a PostgreSQL container. The database will be named postgres, the user postgres, and the password postgres. It will be accessible on port 5436 of your local machine.

```shell
docker run -d  --name pgvector_db -e POSTGRES_PASSWORD=postgres  -e POSTGRES_DATABASE=postgres  -p 5436:5432 pgvector/pgvector:pg17
```

### Download the Wikipedia Articles Dataset:

This command downloads a zipped file containing the embedded Wikipedia articles.

```
wget https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip
```


### Unzip the Dataset:

Extract the vector_database_wikipedia_articles_embedded.csv file from the downloaded zip archive.

```
unzip vector_database_wikipedia_articles_embedded.zip
```

### Connect to your PostgreSQL database:

You can connect using the psql command-line tool.

```
psql -d "postgresql://postgres:postgres@localhost:5436/postgres"
```

### Enable the vector extension:

Once connected to psql, run the following SQL command to enable the pg_vector extension.

```
CREATE EXTENSION vector;
```

### Create the articles table:

This command defines the schema for your articles table, including the vector(1536) columns for embeddings.

```
CREATE TABLE IF NOT EXISTS public.articles (
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
CREATE INDEX ON public.articles USING ivfflat (content_vector) WITH (lists = 1000);
```

```
CREATE INDEX ON public.articles USING ivfflat (title_vector) WITH (lists = 1000);
```

### Load the dataset into the articles table:

This command copies the data from your CSV file into the articles table. Ensure you run this from the directory where vector_database_wikipedia_articles_embedded.csv is located.

```
psql -d "postgresql://postgres:postgres@localhost:5436/postgres" -c "\COPY public.articles (id, url, title, content, title_vector, content_vector, vector_id) FROM 'vector_database_wikipedia_articles_embedded.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');"
```


### Verify Data Loading (Optional):
You can run a simple query to check if the data has been loaded correctly.

```
SELECT id, url, title, SUBSTRING(content FROM 1 FOR 200) || '...' AS truncated_content
FROM public.articles
LIMIT 5;
```


### Find articles similar to a specific article (Recommendation/Related Articles):

```
WITH TargetArticle AS (
    SELECT content_vector
    FROM public.articles
    WHERE id = 12345 -- Replace with the ID of an article you're interested in
)
SELECT
    a.id,
    a.url,
    a.title,
    SUBSTRING(a.content FROM 1 FOR 150) || '...' AS truncated_content,
    1 - (a.content_vector <=> T.content_vector) AS similarity_score
FROM
    public.articles AS a, TargetArticle AS T
WHERE
    a.id != 12345 -- Exclude the target article itself
ORDER BY
    a.content_vector <=> T.content_vector
LIMIT 10;
```







<!-- 



```
docker run -d  --name pgvector_db -e POSTGRES_PASSWORD=postgres  -e POSTGRES_DATABASE=postgres  -p 5436:5432 pgvector/pgvector:pg17
```


```
wget https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip
```


```
unzip vector_database_wikipedia_articles_embedded.zip
```

```
CREATE EXTENSION vector;
```



```
CREATE TABLE IF NOT EXISTS public.articles (
    id INTEGER NOT NULL PRIMARY KEY,
    url TEXT,
    title TEXT,
    content TEXT,
    title_vector vector(1536),
    content_vector vector(1536),
    vector_id INTEGER
);
```


```
CREATE INDEX ON public.articles USING ivfflat (content_vector) WITH (lists = 1000);
```

```
CREATE INDEX ON public.articles USING ivfflat (title_vector) WITH (lists = 1000);
```



```
 psql -d "postgresql://postgres:postgres@localhost:5436/postgres" -c "\COPY public.articles (id, url, title, content, title_vector, content_vector, vector_id) FROM 'vector_database_wikipedia_articles_embedded.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');"
```


```
SELECT id, url, title, SUBSTRING(content FROM 1 FOR 200) || '...' AS truncated_content
FROM public.articles
-- WHERE id = 12345
LIMIT 5;
```


Find articles similar to a specific article (Recommendation/Related Articles):

```
WITH TargetArticle AS (
    SELECT content_vector
    FROM public.articles
    WHERE id = 12345 -- Replace with the ID of an article you're interested in
)
SELECT
    a.id,
    a.url,
    a.title,
    SUBSTRING(a.content FROM 1 FOR 150) || '...' AS truncated_content,
    1 - (a.content_vector <=> T.content_vector) AS similarity_score
FROM
    public.articles AS a, TargetArticle AS T
WHERE
    a.id != 12345 -- Exclude the target article itself
ORDER BY
    a.content_vector <=> T.content_vector
LIMIT 10;
``` -->
# 🐘 PostgreSQL + PostGIS Workshop (Bitnami + Podman)

## 🧭 Workshop Goals

By the end of this workshop, you’ll be able to:

- Run PostgreSQL + PostGIS using Bitnami's container image on Podman
- Create spatial tables and insert geospatial data
- Perform spatial queries with PostGIS functions
- Work with GeoJSON and spatial joins

---

## 🔧 Prerequisites

- [Podman](https://podman.io/getting-started/installation) installed
- `psql` CLI installed or access to a SQL GUI like DBeaver, pgAdmin
- Internet connection to pull container images

---

## 🚀 Step 1: Run PostgreSQL + PostGIS with Bitnami (Podman)

```bash
podman run --rm -it --name postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  bitnami/postgresql:latest
  ```

⏳ Wait a few seconds, then connect:
```bash
podman exec -it postgres psql -U postgres -d postgres
```


🧱 Step 2: Enable PostGIS
Inside the psql prompt:

```sql
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

🌍 Step 3: Create a Spatial Table

```sql
CREATE TABLE landmarks (
id SERIAL PRIMARY KEY,
name TEXT,
location GEOGRAPHY(POINT, 4326)
);

-- Add landmarks in Paris

INSERT INTO landmarks (name, location) VALUES
('Eiffel Tower', ST_GeogFromText('SRID=4326;POINT(2.2945 48.8584)')),
('Louvre Museum', ST_GeogFromText('SRID=4326;POINT(2.3364 48.8606)'));
```

🔎 Step 4: Spatial Queries
📍 Find locations within 1km of a point
```sql
SELECT name
FROM landmarks
WHERE ST_DWithin(
location,
ST_GeogFromText('SRID=4326;POINT(2.295 48.858)'),
1000
);
```


📏 Distance between landmarks

```sql
SELECT  a.name, b.name,
ST_Distance(a.location, b.location) AS distance_meters
FROM landmarks a, landmarks b
WHERE a.name = 'Eiffel Tower' AND b.name = 'Louvre Museum';
```


🧾 Step 5: Work with GeoJSON

```sql
SELECT name, ST_AsGeoJSON(location)::json AS geojson
FROM landmarks;
```

🧭 Step 6: Polygon & Spatial Join
Create an area polygon (bounding box)

```sql
CREATE TABLE areas (
id SERIAL PRIMARY KEY,
name TEXT,
boundary GEOMETRY(POLYGON, 4326)
);

INSERT INTO areas (name, boundary) VALUES (
'Louvre Zone',
ST_GEOMFROMTEXT('POLYGON((51.8121, 0.13712199999997665, 51.9078, 0.21444399999995767))')
);
```

Query: Which landmarks are in the zone?

```sql
SELECT l.name
FROM landmarks l
JOIN areas a ON ST_Contains(a.boundary, l.location);
```
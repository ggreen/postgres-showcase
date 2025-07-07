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

Create network

```shell
podman  network create postgres
```

```bash
podman run --rm -it --name postgres --network postgres\
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  bitnami/postgresql:latest
 ```


Run pgadmin

```shell
podman run -p 6888:80 --network postgres\
    -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=SuperSecret' \
    --rm -it dpage/pgadmin4
```

Open Pgadmin

```shell
open http://localhost:6888
```


Register Server

```properties
name=postgres
hostname=postgres
username=postgres
password=postgres
```






🧱 Step 2: Enable PostGIS
Inside the psql prompt:


In pgadmin Click tools -> query Tool


```sql
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

🌍 Step 3: Create a Spatial Table

```sql
create schema geolocations;
CREATE TABLE geolocations.landmarks (
id SERIAL PRIMARY KEY,
name TEXT,
location GEOGRAPHY(POINT, 4326)
);

-- Add geolocations.landmarks in Paris

INSERT INTO geolocations.landmarks (name, location) VALUES
('Eiffel Tower', ST_GeogFromText('SRID=4326;POINT(2.2945 48.8584)')),
('Louvre Museum', ST_GeogFromText('SRID=4326;POINT(2.3364 48.8606)'));
```

🔎 Step 4: Spatial Queries
📍 Find locations within 1km of a point

```sql
SELECT name
FROM geolocations.landmarks
WHERE ST_DWithin(
location,
ST_GeogFromText('SRID=4326;POINT(2.295 48.858)'),
1000
);
```


📏 Distance between geolocations.landmarks

```sql
SELECT  a.name, b.name,
ST_Distance(a.location, b.location) AS distance_meters
FROM geolocations.landmarks a, geolocations.landmarks b
WHERE a.name = 'Eiffel Tower' AND b.name = 'Louvre Museum';
```


🧾 Step 5: Work with GeoJSON

```sql
SELECT name, ST_AsGeoJSON(location)::json AS geojson
FROM geolocations.landmarks;
```

🧭 Step 6: Polygon & Spatial Join
Create an area polygon (bounding box)

```sql
CREATE TABLE geolocations.areas (
id SERIAL PRIMARY KEY,
name TEXT,
boundary GEOMETRY(POLYGON, 4326)
);

INSERT INTO geolocations.areas (name, boundary) VALUES (
'Louvre Zone',
ST_GEOMFROMTEXT('POLYGON((51.8121, 0.13712199999997665, 51.9078, 0.21444399999995767))')
);
```

Query: Which geolocations.landmarks are in the zone?

```sql
SELECT l.name
FROM geolocations.landmarks l
JOIN geolocations.areas a ON ST_Contains(a.boundary, l.location);
```
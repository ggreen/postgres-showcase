Create network

```shell
podman  network create postgres
```


Start RabbitMQ

```shell
podman run -it --rm \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management
```
Start Postgres

```bash
podman run --rm -it --network=postgres \
  --name postgres \
  -e POSTGRESQL_USERNAME=postgres \
  -e POSTGRESQL_PASSWORD=postgres \
  -e POSTGRESQL_DATABASE=postgres \
  -p 5432:5432 \
  docker.io/bitnami/postgresql:latest
```


Start MongoDB server

```shell
export MONGODB_VERSION=6.0-ubi8
podman  network create postgres
podman run --network=postgres --name mongodb -it --rm  -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=mongo  -e MONGO_INITDB_ROOT_PASSWORD=mongo mongodb/mongodb-community-server:$MONGODB_VERSION
```


Mongosh

```shell
export MONGODB_VERSION=6.0-ubi8
podman run --network=postgres  -it mongodb/mongodb-community-server:$MONGODB_VERSION mongosh "mongodb://mongo:mongo@mongodb/admin"
#podman run --network=postgres  -it mongodb/mongodb-community-server:$MONGODB_VERSION mongosh "mongodb://mongo:mongo@mongodb/local"
```


```shell
show dbs
use admin
db.user.insertOne({"_id": "joedoe", name: "Joe Doe", age: 45, synced: false})
db.user.insertOne({"_id": "jilldoe", name: "Jill Doe", age: 50, synced: false})
db.user.insertOne({"_id": "jsmith", name: "John Smith", age: 33, synced: false})
db.user.insertOne({"_id": "jacme", name: "James Acme", age: 33, synced: false})
```


Query

{ age : { $lt : 0 }, accounts.balance : { $gt : 1000.00 }

```shell
db.user.find({ synced : { $eq :  false }})
```

```shell
db.user.find({})
```


```shell
db.user.updateMany({synced: true}, {$set:{synced: false}})
```


```shell
db.user.updateMany({synced: true, "_id": "joedoe" }, {$set:{synced: false, age: 66}})
```

```shell

gti
```

query


------------------------

Postgres

```sql
CREATE SCHEMA people;
CREATE TABLE people.app_users (
	id varchar NOT NULL,
	name varchar NOT NULL,
	age int NULL,
	CONSTRAINT app_users_id_pk PRIMARY KEY (id)
);
```

---------
# SCDF

Run Skipper

SPRING_APPLICATION_JSON='{"spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.username":"user","spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.password":"bitnami","spring.rabbitmq.username":"user","spring.rabbitmq.password":"bitnami","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.username" :"user","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.password" :"bitnami"}'


```shell
podman run  -it --rm --name skipper --network=postgres \
-e SPRING_APPLICATION_JSON='{"spring.rabbitmq.host" : "rabbitmq", "spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.username":"guest","spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.password":"guest","spring.rabbitmq.username":"guest","spring.rabbitmq.password":"guest","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.username" :"guest","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.password" :"guest"}' \
  -p 7577:7577 \
  springcloud/spring-cloud-skipper-server:2.11.0
```

Start Spring Cloud Data Flow Server

```bash
podman run -it --rm --name dataflow-server --network=postgres \
-e SPRING_APPLICATION_JSON='{"spring.rabbitmq.host" : "rabbitmq", "spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.username":"guest","spring.cloud.stream.binders.rabbitBinder.environment.spring.rabbitmq.password":"guest","spring.rabbitmq.username":"guest","spring.rabbitmq.password":"guest","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.username" :"guest","spring.cloud.dataflow.applicationProperties.stream.spring.rabbitmq.password" :"guest"}' \
-e SPRING_CLOUD_SKIPPER_CLIENT_SERVER_URI=http://skipper:7577/api \
-p 9393:9393 \
springcloud/spring-cloud-dataflow-server:2.11.0
```


Open Dashboard

```shell
open http://localhost:9393/dashboard
```


Adding Applications

- Click Add Applications
- Import ... from dataflow.spring.io
- Stream application starters for RabbitMQ/Maven


Click Stream -> Create Stream

```shell
mongo-stream=mongodb --username=mongo --database=admin --password=mongo --host=mongodb --collection=user --query="{ synced : { $eq :  'false' }" --update-expression="{synced: true}" | postgres: jdbc --columns="name,age" --table-name="people.app_users" --driver-class-name=org.postgresql.Driver --url="jdbc:postgresql://postgres:5432/postgres" --username=postgres --password=postgres
```


Deploy and use properties



```shell
db.user.updateMany({synced: true, "_id": "jsmith" }, {$set:{synced: false, name: "Johnson Smith"}})
```


In new terminal


```bash
podman exec -it postgres psql -U postgres -d postgres
```
Note: password=postgres


```sql
select * from people.app_users;
```

*************


Notes

Click -> Freetext

```properties
app.mongodb.update-expression="'{$set: { synced: true }}'"
app.mongodb.query="'{ synced : { $eq :  false }'"
```

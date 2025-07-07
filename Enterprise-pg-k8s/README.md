## Install Enterprise PostgreSQL on Kubernetes

### Prerequisites

1. Kubernetes cluster with at least v1.30+
2. Helm v3.x
3. psql client installed
4. pg_dump client installed
5. PG_Admin installed: [Dowload your pgAdmin version](https://www.pgadmin.org/download/) (optional)

#### Install cert-manager

```
cd Enterprise-pg-k8s  
```

```shell
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
```

#### Get your credentials from Broadcom Support Portal

```
export HARBOR_USER=XXXXXXXX
export HARBOR_PASSWORD=XXXXXXXX
```


#### Loging to Broadcom Docker Registry 

```shell
helm registry login tanzu-sql-postgres.packages.broadcom.com \
       --username=$HARBOR_USER \
       --password=$HARBOR_PASSWORD
```

#### Pull the operator package from Broadcom Docker Registry 

```shell
helm pull oci://tanzu-sql-postgres.packages.broadcom.com/vmware-sql-postgres-operator --version v3.0.0 --untar --untardir /tmp
```

#### Create a Docker Registry Secret on k8s

```shell
kubectl create secret docker-registry regsecret \
    --docker-server=https://tanzu-sql-postgres.packages.broadcom.com/ \
    --docker-username=$HARBOR_USER \
    --docker-password=$HARBOR_PASSWORD 
```

#### Install the operator package on k8s 

```shell
helm install my-postgres-operator /tmp/vmware-sql-postgres-operator/  --wait
```


#### Verfiy the Operator Installation 

```shell
kubectl get pods 
```


### PostgresDB HA

```shell
kubectl apply -f pg-ha.yaml
```


#### Connect to DB

<!-- ```
echo "Username: " $(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.username}' | base64 --decode)
echo "Password: " $(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.password}' | base64 --decode)
``` -->


```
PG_USERNAME=$(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.username}' | base64 --decode)
PG_PASSWORD=$(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.password}' | base64 --decode)

echo "Retrieved Username: $PG_USERNAME"
echo "Retrieved Password: $PG_PASSWORD"
```

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db
```



### Load Schema

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db -f psql-schema.sql
```


### Load Data

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db -f psql-data-insert.sql
```


### Backup  DB

```
PGPASSWORD=$PG_PASSWORD pg_dump -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db > backup.sql
```



### Restore DB


```
PGPASSWORD=$PG_USERNAME psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres -c "CREATE DATABASE backup OWNER "$PG_USERNAME";"
```


```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d backup -f backup.sql
```
## Install Enterprise PostgreSQL on Kubernetes

## 🎯 Workshop Objective

By the end of this workshop, you will be able to:

- Run Enterprise PostgreSQL on K8s(Docker, Kind, Minikube)
- Connect to the database using `psql`
- Understand schemas
- Create and query tables using SQL files
- Load Data into the database using SQL files
- Backup and Restore the database using SQL files.

---


### Prerequisites

1. Kubernetes cluster with at least v1.30+
2. Helm v3.x
3. postgres v14.x : The demo cluster uses version 14.x and it is recommended to use the same version for client tools like pg_dump
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

[Link to k8s Postgres on Broadcom Support Portal](https://support.broadcom.com/group/ecx/productdownloads?subfamily=VMware%20Tanzu%20for%20Postgres%20on%20Kubernetes)

Click on "VMware Tanzu for Postgres on Kubernetes" and click on green token symbol to get the password. Your username is your email address.

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


### Apply the PostgresDB HA server configuration

Please review the pg-ha.yaml file for any specific configurations that you might want to alter or update.


```shell
kubectl apply -f pg-ha.yaml
```


#### Connect to DB

<!-- ```
echo "Username: " $(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.username}' | base64 --decode)
echo "Password: " $(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.password}' | base64 --decode)
``` -->
**Option 1:** Leveraging pgAdmin tool 

- Downlaod pgAdmin [Dowload your pgAdmin version](https://www.pgadmin.org/download/) 
- configure and run the sql files


**Options 2:** Leveraging psql client tools 

**NOTE:**
Before you can can access the db you need to port-forward the service to your local machine. You can do the below with this command. Please note the below sample uses a differnt port 5444 vs 5432. You can change this as per your needs. IF you wish to change the port to 5432 default please make sure to update port number when you connect via psql or pgAdmin 

```
kubectl  port-forward svc/postgres-ha-sample 5444:5432
```

The below script will export the default username and password from kubernetes secret.

```
PG_USERNAME=$(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.username}' | base64 --decode)
PG_PASSWORD=$(kubectl get secret postgres-ha-sample-db-secret -n default -o jsonpath='{.data.password}' | base64 --decode)

echo "Retrieved Username: $PG_USERNAME"
echo "Retrieved Password: $PG_PASSWORD"
```

Sample command to be able to connect to db using the above credentials via psql

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db
```



### Load Schema

You can leverage the psql-schema.sql file to load sample schema to your database. Note that we are leveraging psql client tool here.

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db -f psql-schema.sql
```


### Load Data

You can leverage psql-data-insert.sql file to load sample data into your database.

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db -f psql-data-insert.sql
```


### Backup  DB

**NOTE:**  Ensure that the client tools are version matching to the server version. i.e 14.x for this example. If you higher/lower version of client tools. Please adjust accordingly. You can update the pgversion in pg-ha.yaml to match the client tools version or vice versa.


To backup the database, you can use **pg_dump** command from you client. You can review the backup.sql file to see what DDL information it has.

```
PGPASSWORD=$PG_PASSWORD pg_dump -h localhost -p 5444 -U "$PG_USERNAME" -d postgres-db > backup.sql
```



### Restore DB

To restore DB we are going to create another database called "backup" on same server  and then restore the data into it.

```
PGPASSWORD=$PG_USERNAME psql -h localhost -p 5444 -U "$PG_USERNAME" -d postgres -c "CREATE DATABASE backup OWNER "$PG_USERNAME";"
```
Below command will allow you restore the backup.sql file to "backupdb" 

```
PGPASSWORD=$PG_PASSWORD psql -h localhost -p 5444 -U "$PG_USERNAME" -d backup -f backup.sql
```


## Trobuleshooting

### k8s
- Describe your pods and pvc to confirm they are healthy.

```
kubectl describe pods, pvc 
```

### pgAdmin
- Connection Refused database "postgres" does not exists.  Check the dbname in pgConfig section of postgres.yaml
- Port issues Check if port is open on your cluster and accessible from your local machine.

### Postgres
- Username or Database does not exists. Check the username and dbname in pgConfig section


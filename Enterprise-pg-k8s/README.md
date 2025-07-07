### Install Enterprise PostgreSQL on Kubernetes

#### Operator

##### Install cert-manager

```shell
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
```

##### Get your credentials from Broadcom Support Portal

```
export HARBOR_USER=XXXXXXXX
export HARBOR_PASSWORD=XXXXXXXX
```


##### Loging to Broadcom Docker Registry 

```shell
helm registry login tanzu-sql-postgres.packages.broadcom.com \
       --username=$HARBOR_USER \
       --password=$HARBOR_PASSWORD
```

##### Pull the operator package from Broadcom Docker Registry 

```shell
helm pull oci://tanzu-sql-postgres.packages.broadcom.com/vmware-sql-postgres-operator --version v3.0.0 --untar --untardir /tmp
```

##### Create a Docker Registry Secret on k8s

```shell
kubectl create secret docker-registry regsecret \
    --docker-server=https://tanzu-sql-postgres.packages.broadcom.com/ \
    --docker-username=$HARBOR_USER \
    --docker-password=$HARBOR_PASSWORD 
```

##### Install the operator package on k8s 

```shell
helm install my-postgres-operator /tmp/vmware-sql-postgres-operator/  --wait
```

###### Create a k8s secrets to be able to pull the images for postgres db

```shell
kubectl create secret docker-registry regsecret \
--docker-server=https://registry.tanzu.vmware.com/ \
--docker-username=$HARBOR_USER \
--docker-password=$HARBOR_PASSWORD
```


```shell
k get pods 
```


#### PostgresDB HA

```
kubectl apply -f pg-ha.yaml
```


### Connect to DB




### Load Schema


### Load Data


### Backup  DB


### Restore DB
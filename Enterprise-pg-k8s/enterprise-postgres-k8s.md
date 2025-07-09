
```shell
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
```

```shell
helm registry login tanzu-sql-postgres.packages.broadcom.com \
       --username=$HARBOR_USER \
       --password=$HARBOR_PASSWORD
```


```shell
helm pull oci://tanzu-sql-postgres.packages.broadcom.com/vmware-sql-postgres-operator --version v3.0.0 --untar --untardir /tmp
```

```
kubectl create secret docker-registry regsecret \
    --docker-server=https://tanzu-sql-postgres.packages.broadcom.com/ \
    --docker-username=$HARBOR_USER \
    --docker-password=$HARBOR_PASSWORD 
```

```
helm install my-postgres-operator /tmp/vmware-sql-postgres-operator/  --wait
```


```shell
kubectl create secret docker-registry regsecret \
--docker-server=https://registry.tanzu.vmware.com/ \
--docker-username=$HARBOR_USER \
--docker-password=$HARBOR_PASSWORD
```

```shell
kubectl create secret docker-registry regsecret \
--docker-server=https://registry.tanzu.vmware.com/ \
--docker-username=$HARBOR_USER \
--docker-password=$HARBOR_PASSWORD -n sql-system
```


```shell
k get pods 
```
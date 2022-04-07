## Cloud Native Architecture Nanodegree (CNAND): Observability

This is the public repository for the Observability course of Udacity's Cloud Native Architecture Nanodegree (CNAND) program (ND064).

The  **Exercise_Starter_Files** directory has all of the files you'll need for the exercises found throughout the course.

The **Project_Starter_Files** directory has the files you'll need for the project at the end of the course.

When vagrant protests that the private network ip should be put to another, change the following
line in Vagrantfile: 
`  config.vm.network "private_network", ip: "192.168.56.10"`

## PREPARING THE OBSERVABILITY PROJECT
`vagrant up`
`vagrant provision` to update vagrant files
`vagrant ssh`
## Install helm using:
 `curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash`

## Install prometheus and Grafana
`kubectl create namespace monitoring`

Add prometheus and grafana repo
`helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
`helm repo add stable https://charts.helm.sh/stable`
`helm repo update`

Install prometheus. Grafana will automatically be installed with it.
`helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --kubeconfig /etc/rancher/k3s/k3s.yaml`

## Install jaeger
`kubectl create namespace observability`

Export jaeger version to enable creating of its yaml files
`export jaeger_version=v1.28.0`
`kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/crds/jaegertracing.io_jaegers_crd.yaml`
`kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/service_account.yaml`
`kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/role.yaml`
`kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/role_binding.yaml`
`kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/operator.yaml`

Because you want to observe other namespaces, you'll need to go ahead and give jaeger
cluster wide visibility
`kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/cluster_role.yaml`
`kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/${jaeger_version}/deploy/cluster_role_binding.yaml`

## Deploy the application
Since the files don't exist in the localhost path after vagrant ssh, you need to create the
yaml files. Copy paste content from existing yaml files, then:
`vim backend.yaml`
Then press `i` for insert, then paste the content. Press `esc` to exit edit mode, then `:wq` press enter.
`kubectl apply -f backend.yaml`
Do the above procedure with `frontend.yaml`, `trial.yaml`, `jaeger.yaml` and `service-monitor.yaml`

## Exposing grafana
Run `kubectl get pod -n monitoring | grep grafana` and look for something named
`prometheus-grafana-###########` where the `#` are random characters.
Copy the `prometheus-grafana-###########` line in its entirety
Run `kubectl port-forward -n monitoring prometheus-grafana-######## 3000` replacing `#` with 
the string copied above.
In your browser, navigate to `localhost:3000`
Log in with `username: admin` and `password:prom-operator`

## Exposing the application
Our frontend needs to be exposed to the internet. Be sure to open a new session on a new terminal window.
Run `kubectl port-forward svc/frontend-service 8080:8080` to expose the application
In you web browser, navigate to `localhost:8080`

## Accessing the jaeger instance
You can verify jaeger instance using (run either one of the following, should return 'simpletest'):
`kubectl get deployment -n observability`
`kubectl get jaegers -n observability`

If you run the command below, you will notice that there is no EXTERNAL-IP available to access
the service/simpletest-query.
`kubectl get deployment,pods,svc -n observability`
To view details of only specific instance, you can try:
`kubectl get svc -l app.kubernetes.io/instances=simpletest -n observability`
Notice the EXTERNAL-IP and the PORT(S) for the `service/simpletest-query`. Since the EXTERNAL-IP is `<none>`, the role of Ingress comes into play. Recall that Ingress manages external access to the services in a cluster.

Check the Ingress port for the service/simpletest-query. Run either of the commands below. Should
return `number: 16686`
`kubectl get -n observability ingresses.v1.networking.k8s.io -o yaml | tail`
`kubectl get -n observability ingress -o yaml | tail`

You can forward a local port to the service/simpletest-query port. Run this command to map local
port 16686 to service/simpletest-query port 16686:
`kubectl port-forward -n observability service/simpletest-query --address 0.0.0.0 16686:16686`
You may not be able to access the jaeger UI on http://127.0..0.1:16686 yet.

To access the jaeger UI from your localhost, we have already mapped the local 16686 port to a port on
your machine,as done in your Vagrantfile.
`config.vm.network "forwarded_port", guest: 16686, host: 8088`
The port mapping above infers you can access jaeger UI via http://127.0.0.1:8088
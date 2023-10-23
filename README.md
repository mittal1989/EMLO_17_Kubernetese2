docker build --platform linux/amd64 -t model-server .
docker build --platform linux/amd64 -t web-server .

---------------------------------------------------------

minikube image load model-server:latest
minikube image load web-server:latest

---------------------------------------------------------

kubectl create namespace emlo

kubectl apply -f . --namespace=emlo
<!-- kubectl apply -f . -->

---------------------------------------------------------

`Check if the redis service is working:`

kubectl run ubuntu --rm -i --tty --image=ubuntu -- bash
redis-cli -h redis-db-service -a "aiwilltakeovertheworld"

---------------------------------------------------------

kubectl get all

---------------------------------------------------------

`You can create a tunnel to the service with minikube:`

minikube service web-server-service

---------------------------------------------------------

minikube addons enable ingress

minikube tunnel

`http://fastapi.localhost/`


#!/bin/bash

cd ~/edupredictops

echo "Starting Minikube..."
minikube start --driver=docker --memory=2048 --cpus=2

echo "Waiting for Minikube to be ready..."
kubectl wait --for=condition=Ready node/minikube --timeout=120s

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yml
sleep 2
kubectl apply -f k8s/flask-deployment.yml
kubectl apply -f k8s/flask-service.yml

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pod --all -n edupredictops --timeout=180s

echo ""
echo "=== Deployment Status ==="
kubectl get all -n edupredictops

echo ""
echo "=== Access URL ==="
minikube service flask-api -n edupredictops --url

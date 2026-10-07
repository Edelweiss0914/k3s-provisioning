# 2단계 — 기본 Kubernetes 기능 확인

> 작성일: 2026-10-07
> 상태: 완료

## 목표

K3s 클러스터에서 Namespace, Deployment, Service가 정상 동작하는지 확인하고 멀티노드 Pod 분산을 검증한다.

## 진행 절차

### 1. Namespace 생성

```bash
kubectl create namespace test-customer
kubectl get namespaces
```

### 2. nginx Deployment 배포

```bash
kubectl create deployment nginx --image=nginx --replicas=1 -n test-customer
kubectl get pods -n test-customer
```

### 3. Service 생성 및 접속 확인

```bash
kubectl expose deployment nginx --port=80 --type=ClusterIP -n test-customer
kubectl get svc -n test-customer
curl http://<ClusterIP>
```

정상 응답: `Welcome to nginx!`

### 4. 멀티노드 분산 확인

```bash
kubectl scale deployment nginx --replicas=2 -n test-customer
kubectl get pods -n test-customer -o wide
```

결과:
```
nginx-xxx   Running   k3s-server
nginx-xxx   Running   k3s-worker
```

두 노드에 Pod가 분산 배치되는 것을 확인했다.

### 5. 테스트 리소스 정리

```bash
kubectl delete namespace test-customer
```

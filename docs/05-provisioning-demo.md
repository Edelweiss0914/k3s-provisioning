# 4~5단계 — 웹폼 및 자동 프로비저닝 완성

> 작성일: 2026-10-07
> 상태: 완료

## 전체 흐름

```
관리자 웹폼 (frontend/index.html)
       ↓  POST /provision
FastAPI Backend (192.168.50.67:8000)
       ↓  Python Kubernetes Client
Kubernetes API Server
       ↓
Namespace / ResourceQuota / LimitRange / Deployment / Service 자동 생성
       ↓
nginx Pod → k3s-worker 노드 실행
```

## 웹폼 입력 항목

| 항목 | 필수 | 기본값 |
|---|---|---|
| 고객 ID (Namespace) | ✅ | - |
| 서비스 이름 | ✅ | - |
| CPU 제한 | - | 200m |
| 메모리 제한 | - | 256Mi |
| Replica 수 | - | 1 |

## 시연 결과 (customer-a)

```bash
kubectl get ns customer-a
# customer-a   Active

kubectl get all -n customer-a
# pod/web-service-xxx     1/1  Running  k3s-worker
# service/web-service     ClusterIP  10.43.26.218  80/TCP
# deployment/web-service  1/1

kubectl get resourcequota -n customer-a
# requests.cpu: 100m/200m  requests.memory: 128Mi/256Mi
# limits.cpu:   200m/200m  limits.memory:   256Mi/256Mi

kubectl get pod -n customer-a -o wide
# web-service-xxx   Running   10.42.1.4   k3s-worker
```

## 관리 기능

### 상태 조회

웹폼 하단 "서비스 관리" 섹션에서 고객 ID 입력 후 **상태 조회** 클릭.
Pod 상태, Deployment Ready 여부, Service ClusterIP를 테이블로 표시.

### 서비스 삭제

**서비스 삭제** 클릭 → Namespace 삭제 → 관련 리소스 전체 제거.

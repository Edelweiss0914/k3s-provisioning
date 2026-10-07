# 3단계 — Backend API 개발 및 배포

> 작성일: 2026-10-07
> 상태: 완료

## 구성

| 항목 | 내용 |
|---|---|
| 프레임워크 | FastAPI |
| Kubernetes 연동 | Python kubernetes 클라이언트 (v31.0.0) |
| 실행 위치 | k3s-server VM (192.168.50.67:8000) |

## 파일 구조

```
backend/
 ├── main.py         # FastAPI 앱, 라우터
 ├── k8s_client.py   # Kubernetes API 연동 함수
 └── requirements.txt
```

## API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| GET | `/health` | 헬스체크 |
| POST | `/provision` | 고객 서비스 프로비저닝 |
| DELETE | `/provision/{customer_id}` | 서비스 삭제 |
| GET | `/provision/{customer_id}/status` | 서비스 상태 조회 |

## 프로비저닝 생성 항목

POST `/provision` 호출 시 아래 리소스를 순서대로 생성한다.

1. Namespace
2. ResourceQuota
3. LimitRange
4. Deployment (nginx, Worker Node 배치)
5. Service (ClusterIP)

## 요청 예시

```json
{
  "customer_id": "customer-a",
  "service_name": "web-service",
  "cpu_limit": "200m",
  "memory_limit": "256Mi",
  "replicas": 1
}
```

## k3s-server 배포 절차

```bash
# 패키지 설치
dnf install -y python3 python3-pip git

# 레포 클론
git clone https://github.com/Edelweiss0914/k3s-provisioning.git
cd k3s-provisioning

# 의존성 설치
pip3 install -r backend/requirements.txt

# RBAC 적용
kubectl apply -f k8s/rbac.yaml

# kubeconfig 권한 설정
chmod 644 /etc/rancher/k3s/k3s.yaml

# 방화벽 오픈
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload

# 서버 실행
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 헬스체크 확인

```bash
curl http://192.168.50.67:8000/health
# {"status":"ok"}
```

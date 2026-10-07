# 외부 접속 구성

> 작성일: 2026-10-07
> 상태: 완료

## 구성 개요

기존 홈랩 인프라(Cloudflare Tunnel + Gateway LXC)를 활용하여 외부에서 프로비저닝 관리 페이지에 접속할 수 있도록 구성했다.

## 접속 경로

```
외부 브라우저
    → https://provision.edelweiss0297.cloud
    → Cloudflare Tunnel (nextcloud-tunnel)
    → FastAPI Backend (192.168.50.67:8000)
    → 프론트엔드 + API 통합 제공
```

## 설정 절차

### 1. Cloudflare Zero Trust 터널 Public Hostname 추가

- Zero Trust → Networks → Tunnels → `nextcloud-tunnel` → Configure
- Public Hostnames → Add a public hostname

| 항목 | 값 |
|---|---|
| Subdomain | `provision` |
| Domain | `edelweiss0297.cloud` |
| Service Type | `HTTP` |
| URL | `192.168.50.67:8000` |

기존 Gateway LXC nginx 설정 변경 없이 터널이 FastAPI로 직접 라우팅된다.

### 2. FastAPI 프론트엔드 서빙

`backend/main.py`에 루트 경로(`/`) 추가:

```python
@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
```

### 3. 프론트엔드 API 경로 수정

외부 도메인에서 동작하도록 API 주소를 상대 경로로 변경:

```javascript
// 변경 전
const API = "http://192.168.50.67:8000";

// 변경 후
const API = "";
```

## 최종 확인

| 항목 | 결과 |
|---|---|
| 외부 접속 | `https://provision.edelweiss0297.cloud` ✅ |
| 프로비저닝 (customer-b) | Pod Running on k3s-worker ✅ |
| TLS | Cloudflare 자동 처리 ✅ |

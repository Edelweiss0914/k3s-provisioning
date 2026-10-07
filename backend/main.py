from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import re

from k8s_client import (
    create_namespace,
    create_resource_quota,
    create_limit_range,
    create_deployment,
    create_service,
    delete_namespace,
    get_namespace_status,
)

app = FastAPI(title="K3s Provisioning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProvisionRequest(BaseModel):
    customer_id: str
    service_name: str
    cpu_limit: str = "200m"
    memory_limit: str = "256Mi"
    replicas: int = 1

    @field_validator("customer_id", "service_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9][a-z0-9\-]{1,30}[a-z0-9]$", v):
            raise ValueError("소문자, 숫자, 하이픈만 허용 (3~32자)")
        return v

    @field_validator("replicas")
    @classmethod
    def validate_replicas(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("replicas는 1~5 사이여야 합니다")
        return v


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/provision")
def provision(req: ProvisionRequest):
    namespace = req.customer_id

    try:
        create_namespace(namespace)
        create_resource_quota(namespace, req.cpu_limit, req.memory_limit)
        create_limit_range(namespace)
        create_deployment(namespace, req.service_name, req.replicas, req.cpu_limit, req.memory_limit)
        create_service(namespace, req.service_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "프로비저닝 완료",
        "namespace": namespace,
        "service": req.service_name,
        "replicas": req.replicas,
    }


@app.delete("/provision/{customer_id}")
def deprovision(customer_id: str):
    try:
        delete_namespace(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"{customer_id} 삭제 완료"}


@app.get("/provision/{customer_id}/status")
def status(customer_id: str):
    try:
        result = get_namespace_status(customer_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result

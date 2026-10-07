from kubernetes import client, config


def load_kube_config():
    """K3s kubeconfig 로드"""
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")


def create_namespace(name: str):
    load_kube_config()
    v1 = client.CoreV1Api()
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=name)
    )
    v1.create_namespace(body=namespace)


def create_resource_quota(namespace: str, cpu_limit: str, memory_limit: str):
    load_kube_config()
    v1 = client.CoreV1Api()
    quota = client.V1ResourceQuota(
        metadata=client.V1ObjectMeta(name="customer-quota", namespace=namespace),
        spec=client.V1ResourceQuotaSpec(
            hard={
                "requests.cpu": cpu_limit,
                "requests.memory": memory_limit,
                "limits.cpu": cpu_limit,
                "limits.memory": memory_limit,
            }
        ),
    )
    v1.create_namespaced_resource_quota(namespace=namespace, body=quota)


def create_limit_range(namespace: str):
    load_kube_config()
    v1 = client.CoreV1Api()
    limit_range = client.V1LimitRange(
        metadata=client.V1ObjectMeta(name="default-limit", namespace=namespace),
        spec=client.V1LimitRangeSpec(
            limits=[
                client.V1LimitRangeItem(
                    type="Container",
                    default={"cpu": "200m", "memory": "256Mi"},
                    default_request={"cpu": "100m", "memory": "128Mi"},
                )
            ]
        ),
    )
    v1.create_namespaced_limit_range(namespace=namespace, body=limit_range)


def create_deployment(namespace: str, name: str, replicas: int, cpu_limit: str, memory_limit: str):
    load_kube_config()
    apps_v1 = client.AppsV1Api()
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels={"app": name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=name,
                            image="nginx:latest",
                            ports=[client.V1ContainerPort(container_port=80)],
                            resources=client.V1ResourceRequirements(
                                requests={"cpu": "100m", "memory": "128Mi"},
                                limits={"cpu": cpu_limit, "memory": memory_limit},
                            ),
                        )
                    ],
                    node_selector={"kubernetes.io/hostname": "k3s-worker"},
                ),
            ),
        ),
    )
    apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)


def create_service(namespace: str, name: str):
    load_kube_config()
    v1 = client.CoreV1Api()
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=80, target_port=80)],
            type="ClusterIP",
        ),
    )
    v1.create_namespaced_service(namespace=namespace, body=service)


def delete_namespace(name: str):
    load_kube_config()
    v1 = client.CoreV1Api()
    v1.delete_namespace(name=name)


def get_namespace_status(namespace: str) -> dict:
    load_kube_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    pods = v1.list_namespaced_pod(namespace=namespace)
    services = v1.list_namespaced_service(namespace=namespace)
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)

    return {
        "pods": [
            {
                "name": p.metadata.name,
                "status": p.status.phase,
                "node": p.spec.node_name,
            }
            for p in pods.items
        ],
        "services": [
            {
                "name": s.metadata.name,
                "cluster_ip": s.spec.cluster_ip,
                "port": s.spec.ports[0].port if s.spec.ports else None,
            }
            for s in services.items
        ],
        "deployments": [
            {
                "name": d.metadata.name,
                "replicas": d.spec.replicas,
                "ready": d.status.ready_replicas or 0,
            }
            for d in deployments.items
        ],
    }

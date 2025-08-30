from __future__ import annotations

from typing import Any, Dict, List

from ..core.types import Resource, CheckRegistry, ReportInfo
from .pod import PodResource
from .workloads import DeploymentResource, StatefulSetResource, DaemonSetResource
from .networking import ServiceResource, IngressResource, NetworkPolicyResource
from .data import ConfigMapResource, SecretResource, PersistentVolumeClaimResource


class NamespaceResource(Resource):
    kind = "Namespace"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context=None) -> "NamespaceResource":
        meta = obj.get("metadata", {})
        return NamespaceResource(
            name=meta.get("name", "default"),
            namespace=None,
            raw=obj,
            kube_context=kube_context,
        )

    def children(self, registry: CheckRegistry) -> List[Resource]:
        # Discover live pods in this namespace via Kubernetes API
        children: List[Resource] = []
        try:
            v1 = self.kube_context.core_v1() if self.kube_context else None
            if not v1:
                return []
            # List pod names, then fetch detail per pod
            pod_list = v1.list_namespaced_pod(self.name)
            for pod in pod_list.items:
                pod_name = pod.metadata.name
                p = v1.read_namespaced_pod(name=pod_name, namespace=self.name)
                pd = {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": p.metadata.name, "namespace": p.metadata.namespace, "labels": p.metadata.labels or {}},
                    "spec": {"containers": [c.to_dict() for c in (p.spec.containers or [])], "nodeSelector": p.spec.node_selector or {}, "initContainers": [c.to_dict() for c in (p.spec.init_containers or [])], "volumes": [v.to_dict() for v in (p.spec.volumes or [])]},
                    "status": {
                        "phase": p.status.phase,
                        "containerStatuses": [cs.to_dict() for cs in (p.status.container_statuses or [])],
                        "initContainerStatuses": [cs.to_dict() for cs in (p.status.init_container_statuses or [])],
                    },
                }
                children.append(PodResource.from_k8s_obj(pd, kube_context=self.kube_context))

            # Services
            svcs = v1.list_namespaced_service(self.name)
            for s in svcs.items:
                sd = {"apiVersion": "v1", "kind": "Service", "metadata": {"name": s.metadata.name, "namespace": s.metadata.namespace}, "spec": s.spec.to_dict() if s.spec else {}}
                children.append(ServiceResource.from_k8s_obj(sd, kube_context=self.kube_context))

            # ConfigMaps
            cms = v1.list_namespaced_config_map(self.name)
            for cm in cms.items:
                cmd = {"apiVersion": "v1", "kind": "ConfigMap", "metadata": {"name": cm.metadata.name, "namespace": cm.metadata.namespace}}
                children.append(ConfigMapResource.from_k8s_obj(cmd, kube_context=self.kube_context))

            # Secrets
            secs = v1.list_namespaced_secret(self.name)
            for sec in secs.items:
                sd = {"apiVersion": "v1", "kind": "Secret", "metadata": {"name": sec.metadata.name, "namespace": sec.metadata.namespace}}
                children.append(SecretResource.from_k8s_obj(sd, kube_context=self.kube_context))

            # PVCs
            pvcs = v1.list_namespaced_persistent_volume_claim(self.name)
            for pvc in pvcs.items:
                pvcd = {"apiVersion": "v1", "kind": "PersistentVolumeClaim", "metadata": {"name": pvc.metadata.name, "namespace": pvc.metadata.namespace}, "spec": pvc.spec.to_dict() if pvc.spec else {}, "status": pvc.status.to_dict() if pvc.status else {}}
                children.append(PersistentVolumeClaimResource.from_k8s_obj(pvcd, kube_context=self.kube_context))

            # Apps/v1 workloads
            apps = self.kube_context.apps_v1() if self.kube_context else None
            if apps:
                deps = apps.list_namespaced_deployment(self.name)
                for d in deps.items:
                    dd = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": d.metadata.name, "namespace": d.metadata.namespace}, "spec": {"template": {"spec": {"containers": [c.to_dict() for c in (d.spec.template.spec.containers or [])]}}}}
                    children.append(DeploymentResource.from_k8s_obj(dd, kube_context=self.kube_context))

                sfs = apps.list_namespaced_stateful_set(self.name)
                for s in sfs.items:
                    sd = {"apiVersion": "apps/v1", "kind": "StatefulSet", "metadata": {"name": s.metadata.name, "namespace": s.metadata.namespace}, "spec": {"template": {"spec": {"containers": [c.to_dict() for c in (s.spec.template.spec.containers or [])]}}}}
                    children.append(StatefulSetResource.from_k8s_obj(sd, kube_context=self.kube_context))

                dss = apps.list_namespaced_daemon_set(self.name)
                for ds in dss.items:
                    dsd = {"apiVersion": "apps/v1", "kind": "DaemonSet", "metadata": {"name": ds.metadata.name, "namespace": ds.metadata.namespace}, "spec": {"template": {"spec": {"containers": [c.to_dict() for c in (ds.spec.template.spec.containers or [])]}}}}
                    children.append(DaemonSetResource.from_k8s_obj(dsd, kube_context=self.kube_context))

            # Networking
            net = self.kube_context.networking_v1() if self.kube_context else None
            if net:
                ings = net.list_namespaced_ingress(self.name)
                for ing in ings.items:
                    idd = {"apiVersion": "networking.k8s.io/v1", "kind": "Ingress", "metadata": {"name": ing.metadata.name, "namespace": ing.metadata.namespace}, "spec": ing.spec.to_dict() if ing.spec else {}}
                    children.append(IngressResource.from_k8s_obj(idd, kube_context=self.kube_context))

                nps = net.list_namespaced_network_policy(self.name)
                for np in nps.items:
                    npd = {"apiVersion": "networking.k8s.io/v1", "kind": "NetworkPolicy", "metadata": {"name": np.metadata.name, "namespace": np.metadata.namespace}}
                    children.append(NetworkPolicyResource.from_k8s_obj(npd, kube_context=self.kube_context))
        except Exception:
            return []
        return children



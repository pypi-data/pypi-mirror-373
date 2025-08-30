from __future__ import annotations

from typing import Any, Dict, List

from ..core.types import Resource, CheckRegistry
from .namespace import NamespaceResource
from .data import PersistentVolumeResource
from .rbac import ClusterRoleResource, ClusterRoleBindingResource
from .nodes import NodeResource


class ClusterResource(Resource):
    kind = "Cluster"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context=None) -> "ClusterResource":
        return ClusterResource(
            name=obj.get("name", "cluster"),
            namespace=None,
            raw=obj,
            kube_context=kube_context,
        )

    def children(self, registry: CheckRegistry) -> List[Resource]:
        # Discover live namespaces via Kubernetes API
        children: List[Resource] = []
        try:
            v1 = self.kube_context.core_v1() if self.kube_context else None
            if v1:
                nss = v1.list_namespace()
                for ns in nss.items:
                    nsd = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns.metadata.name}}
                    children.append(NamespaceResource.from_k8s_obj(nsd, kube_context=self.kube_context))

                # Nodes
                nodes = v1.list_node()
                for node in nodes.items:
                    nd = {"apiVersion": "v1", "kind": "Node", "metadata": {"name": node.metadata.name}}
                    children.append(NodeResource.from_k8s_obj(nd, kube_context=self.kube_context))

                # PersistentVolumes
                pvs = v1.list_persistent_volume()
                for pv in pvs.items:
                    pvd = {"apiVersion": "v1", "kind": "PersistentVolume", "metadata": {"name": pv.metadata.name}}
                    children.append(PersistentVolumeResource.from_k8s_obj(pvd, kube_context=self.kube_context))

            rbac = self.kube_context.rbac_v1() if self.kube_context else None
            if rbac:
                crs = rbac.list_cluster_role()
                for cr in crs.items:
                    crd = {"apiVersion": "rbac.authorization.k8s.io/v1", "kind": "ClusterRole", "metadata": {"name": cr.metadata.name}}
                    children.append(ClusterRoleResource.from_k8s_obj(crd, kube_context=self.kube_context))

                crbs = rbac.list_cluster_role_binding()
                for crb in crbs.items:
                    crbd = {"apiVersion": "rbac.authorization.k8s.io/v1", "kind": "ClusterRoleBinding", "metadata": {"name": crb.metadata.name}}
                    children.append(ClusterRoleBindingResource.from_k8s_obj(crbd, kube_context=self.kube_context))
        except Exception:
            return []
        return children



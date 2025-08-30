from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.namespace import NamespaceResource
from ...core.kube import KubeContext


class OverprivilegedServiceAccountCheck(BaseCheck):
    id = "SA_OVERPRIVILEGED"
    title = "ServiceAccount bound to cluster-admin"
    category = "misconfig"
    target_kind = "ServiceAccount"

    def run(self, resource: NamespaceResource) -> ReportInfo:
        kube: KubeContext | None = resource.kube_context
        if not kube:
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="no kube context")
        found = False
        detail = ""
        try:
            rbac = kube.rbac_v1()
            rbs = rbac.list_namespaced_role_binding(resource.name)
            crbs = rbac.list_cluster_role_binding()
            # Map cluster-admin CRB subjects to SA
            ca_sas = set()
            for b in crbs.items:
                if b.role_ref.kind == "ClusterRole" and b.role_ref.name == "cluster-admin":
                    for s in (b.subjects or []):
                        if s.kind == "ServiceAccount" and s.namespace:
                            ca_sas.add((s.namespace, s.name))
            # Check if any SA in this ns is cluster-admin via direct or namespaced RB
            for rb in rbs.items:
                if rb.role_ref.kind == "ClusterRole" and rb.role_ref.name == "cluster-admin":
                    for s in (rb.subjects or []):
                        if s.kind == "ServiceAccount":
                            if (rb.metadata.namespace, s.name) == (resource.name, s.name):
                                found = True
                                detail = f"{s.name} bound to cluster-admin"
                                break
            # Also if any SA from this ns appears in CRBs
            if not found:
                for ns, sa in ca_sas:
                    if ns == resource.name:
                        found = True
                        detail = f"{sa} bound via ClusterRoleBinding"
                        break
        except Exception:
            pass
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=not found, details=detail or "ok", description="ServiceAccounts should be least-privileged. Docs: https://kubernetes.io/docs/reference/access-authn-authz/rbac/", probable_cause="ClusterRoleBinding to cluster-admin present")



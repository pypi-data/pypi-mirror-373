from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.workloads import DeploymentResource
from ...core.kube import KubeContext


class DeploymentReplicasCheck(BaseCheck):
    id = "DEP_REPLICAS"
    title = "Deployment should have at least 2 replicas in production"
    category = "misconfig"
    target_kind = "Deployment"

    def run(self, resource: DeploymentResource) -> ReportInfo:
        replicas = (resource.raw.get("spec", {}) or {}).get("replicas", 1)
        passed = replicas >= 2
        details = f"replicas={replicas}"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="Multiple replicas provide high availability and rolling update capability. Docs: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#scaling-a-deployment",
            probable_cause="Deployment configured with replicas=1 or default single replica"
        )


class DeploymentRolloutStuckCheck(BaseCheck):
    id = "DEP_ROLLOUT_STUCK"
    title = "Deployment rollout appears stuck"
    category = "fault"
    target_kind = "Deployment"

    def run(self, resource: DeploymentResource) -> ReportInfo:
        status = (resource.raw.get("status", {}) or {})
        desired = int(status.get("replicas" , 0))
        available = int(status.get("availableReplicas" , 0))
        updated = int(status.get("updatedReplicas" , 0))
        progressing = available < desired or updated < desired
        details = f"desired={desired}, updated={updated}, available={available}"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not progressing, 
            details=details, 
            description="Rollout stuck often due to failing readiness probes or insufficient resources. Docs: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#troubleshooting", 
            probable_cause="Readiness probe failing or pods pending"
        )



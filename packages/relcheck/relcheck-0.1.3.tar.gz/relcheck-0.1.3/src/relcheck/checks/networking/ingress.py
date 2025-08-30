from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.networking import IngressResource
from ...core.kube import KubeContext


class IngressTlsCheck(BaseCheck):
    id = "ING_TLS"
    title = "Ingress should use TLS"
    category = "misconfig"
    target_kind = "Ingress"

    def run(self, resource: IngressResource) -> ReportInfo:
        tls = (resource.raw.get("spec", {}) or {}).get("tls")
        passed = bool(tls)
        details = "tls configured" if passed else "no tls section in ingress"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="TLS ensures secure HTTPS communication. Docs: https://kubernetes.io/docs/concepts/services-networking/ingress/#tls",
            probable_cause="TLS section not configured in Ingress spec"
        )


class IngressServiceDriftCheck(BaseCheck):
    id = "ING_DRIFT"
    title = "Ingress backend points to non-matching Service"
    category = "fault"
    target_kind = "Ingress"

    def run(self, resource: IngressResource) -> ReportInfo:
        spec = resource.raw.get("spec", {}) or {}
        rules = spec.get("rules") or []
        kube: KubeContext | None = resource.kube_context
        drift = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                for r in rules:
                    http = r.get("http") or {}
                    for p in http.get("paths", []) or []:
                        backend = p.get("backend", {})
                        svc = backend.get("service", {})
                        name = svc.get("name")
                        if not name:
                            continue
                        s = v1.read_namespaced_service(name=name, namespace=resource.namespace or "default")
                        # if service has selector but selects zero endpoints, drift likely
                        selector = s.spec.selector or {}
                        if selector:
                            label_selector = ",".join([f"{k}={v}" for k, v in selector.items()])
                            pods = v1.list_namespaced_pod(resource.namespace or "default", label_selector=label_selector)
                            if len(pods.items) == 0:
                                drift = True
                                detail = f"service {name} selects 0 pods"
                                break
        except Exception:
            pass

        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not drift, 
            details=detail or "ok", 
            description="Ingress should route to a Service that actually selects pods. Empty endpoints imply drift. Docs: https://kubernetes.io/docs/concepts/services-networking/ingress/", 
            probable_cause="Service selector does not match any pods or deployment scaled to 0"
        )


class IngressWrongServiceTypeCheck(BaseCheck):
    id = "ING_SVC_TYPE"
    title = "Ingress backend Service is not ClusterIP"
    category = "misconfig"
    target_kind = "Ingress"

    def run(self, resource: IngressResource) -> ReportInfo:
        spec = resource.raw.get("spec", {}) or {}
        rules = spec.get("rules") or []
        kube: KubeContext | None = resource.kube_context
        wrong = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                for r in rules:
                    http = r.get("http") or {}
                    for p in http.get("paths", []) or []:
                        backend = p.get("backend", {})
                        svc = backend.get("service", {})
                        name = svc.get("name")
                        if not name:
                            continue
                        s = v1.read_namespaced_service(name=name, namespace=resource.namespace or "default")
                        if s.spec.type and s.spec.type != "ClusterIP":
                            wrong = True
                            detail = f"service {name} type={s.spec.type}"
                            break
        except Exception:
            pass
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not wrong, 
            details=detail or "ok", 
            description="Ingress should usually target ClusterIP services. Docs: https://kubernetes.io/docs/concepts/services-networking/ingress/#the-ingress-resource", 
            probable_cause="Service type set to NodePort/LoadBalancer behind Ingress"
        )



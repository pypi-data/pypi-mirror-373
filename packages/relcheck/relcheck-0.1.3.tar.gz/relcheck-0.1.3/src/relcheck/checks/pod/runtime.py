from __future__ import annotations

from typing import List

from ...core.types import ReportInfo, BaseCheck
from ...resources.pod import PodResource


def _mk(resource: PodResource, check: BaseCheck, passed: bool, details: str, description: str, probable: str) -> ReportInfo:
    return ReportInfo(
        resource_kind=resource.kind,
        resource_name=resource.name,
        namespace=resource.namespace,
        check_id=check.id,
        check_title=check.title,
        category=check.category,
        passed=passed,
        details=details,
        description=description,
        probable_cause=probable,
    )


class PodCrashLoopBackOffCheck(BaseCheck):
    id = "POD_CRASHLOOP"
    title = "Pod is CrashLoopBackOff"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        statuses = (resource.raw.get("status", {}) or {}).get("containerStatuses", [])
        crashing = any((s.get("state", {}).get("waiting", {}) or {}).get("reason") == "CrashLoopBackOff" for s in statuses)
        details = "CrashLoopBackOff detected" if crashing else "no crashloop"
        return _mk(
            resource,
            self,
            passed=not crashing,
            details=details,
            description="Container repeatedly crashes and restarts. See Kubernetes Troubleshooting: https://kubernetes.io/docs/tasks/debug/debug-application/debug-application/",
            probable="Bad env/config, failing startup command, missing dependency, or readiness/liveness interaction",
        )


class PodImagePullBackOffCheck(BaseCheck):
    id = "POD_IMAGEPULL"
    title = "Pod has ImagePullBackOff"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        statuses = (resource.raw.get("status", {}) or {}).get("containerStatuses", [])
        pulling = any((s.get("state", {}).get("waiting", {}) or {}).get("reason") in {"ImagePullBackOff", "ErrImagePull"} for s in statuses)
        details = "ImagePullBackOff detected" if pulling else "images pull successfully"
        return _mk(
            resource,
            self,
            passed=not pulling,
            details=details,
            description="Image pull failures often due to private registries or wrong image name/tag. Docs: https://kubernetes.io/docs/concepts/containers/images/",
            probable="Missing imagePullSecrets, wrong image name/tag, registry unavailable",
        )


class PodReadinessProbeFailCheck(BaseCheck):
    id = "POD_READINESS"
    title = "Readiness probe failing"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        has_probe = any((c.get("readinessProbe") is not None) for c in resource.containers())
        ready = all(s.get("ready", True) for s in (resource.raw.get("status", {}) or {}).get("containerStatuses", []))
        failing = has_probe and not ready
        details = "containers not ready" if failing else "ready"
        return _mk(
            resource,
            self,
            passed=not failing,
            details=details,
            description="Readiness probe prevents traffic to unhealthy pods. Misconfig causes pods to stay unready. Docs: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/",
            probable="Wrong probe path/port/scheme or app not listening",
        )


class PodLivenessProbeLoopCheck(BaseCheck):
    id = "POD_LIVENESS"
    title = "Liveness probe killing pod repeatedly"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        has_probe = any((c.get("livenessProbe") is not None) for c in resource.containers())
        restarts = sum(int(s.get("restartCount", 0)) for s in (resource.raw.get("status", {}) or {}).get("containerStatuses", []))
        failing = has_probe and restarts >= 3
        details = f"restartCount={restarts}"
        return _mk(
            resource,
            self,
            passed=not failing,
            details=details,
            description="Misconfigured liveness probe can kill containers in a loop. Docs: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/",
            probable="Probe path/port wrong or initialDelaySeconds too low",
        )


class PodOOMKilledCheck(BaseCheck):
    id = "POD_OOMKILLED"
    title = "Container terminated OOMKilled"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        statuses = (resource.raw.get("status", {}) or {}).get("containerStatuses", [])
        def _is_oom(s: dict) -> bool:
            term = (s.get("lastState", {}).get("terminated") or s.get("state", {}).get("terminated") or {})
            return term.get("reason") == "OOMKilled"
        oom = any(_is_oom(s) for s in statuses)
        details = "OOMKilled observed" if oom else "no OOMKilled"
        return _mk(
            resource,
            self,
            passed=not oom,
            details=details,
            description="Container killed due to out-of-memory. Docs: https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/",
            probable="Memory limits too low or memory leak",
        )


class PodPendingUnschedulableCheck(BaseCheck):
    id = "POD_PENDING"
    title = "Pod Pending due to scheduling"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        phase = (resource.raw.get("status", {}) or {}).get("phase")
        conds = (resource.raw.get("status", {}) or {}).get("conditions", [])
        reasons = ",".join([c.get("reason", "") for c in conds])
        unsched = phase == "Pending" and ("Unschedulable" in reasons)
        details = f"phase={phase or 'Unknown'} reasons={reasons or '-'}"
        return _mk(
            resource,
            self,
            passed=not unsched,
            details=details,
            description="Pending Unschedulable often due to nodeSelector/taints or resource requests not met. Docs: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/",
            probable="nodeSelector/affinity mismatch, insufficient cluster resources, taints without tolerations",
        )


class PodInitContainerFailedCheck(BaseCheck):
    id = "POD_INIT_FAILED"
    title = "InitContainer failed"
    category = "fault"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        statuses = (resource.raw.get("status", {}) or {}).get("initContainerStatuses", [])
        failed = any(((s.get("state", {}).get("terminated") or {}).get("exitCode", 0) != 0) for s in statuses)
        details = "init container failed" if failed else "ok"
        return _mk(
            resource,
            self,
            passed=not failed,
            details=details,
            description="Init container must complete before app starts. Docs: https://kubernetes.io/docs/concepts/workloads/pods/init-containers/",
            probable="Init command/image wrong, missing dependency or credentials",
        )


class PodRunAsRootCheck(BaseCheck):
    id = "POD_ROOT"
    title = "Pod running as root"
    category = "misconfig"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        def is_root(sc: dict | None) -> bool:
            if not sc:
                return True
            run_as_user = sc.get("runAsUser")
            return run_as_user is None or int(run_as_user) == 0
        pod_sc = (resource.raw.get("spec", {}) or {}).get("securityContext")
        any_root = is_root(pod_sc) or any(is_root(c.get("securityContext")) for c in resource.containers())
        details = "runs as root" if any_root else "non-root"
        return _mk(
            resource,
            self,
            passed=not any_root,
            details=details,
            description="Running as root increases risk. Docs: https://kubernetes.io/docs/concepts/security/pod-security-standards/",
            probable="No runAsUser set or image defaults to root",
        )


class PodCpuThrottlingCheck(BaseCheck):
    id = "POD_CPU_THROTTLE"
    title = "CPU limit likely to cause throttling"
    category = "misconfig"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        def parse_milli(cpu: str | None) -> int:
            if not cpu:
                return 0
            s = str(cpu)
            if s.endswith("m"):
                return int(s[:-1] or 0)
            try:
                # Assume cores -> convert to milli
                return int(float(s) * 1000)
            except Exception:
                return 0

        low = False
        mins: list[str] = []
        for c in resource.containers():
            limits = (c.get("resources", {}) or {}).get("limits", {}) or {}
            milli = parse_milli(limits.get("cpu"))
            if milli and milli <= 100:  # <= 0.1 core
                low = True
                mins.append(f"{c.get('name','?')}={milli}m")
        details = ",".join(mins) if mins else "ok"
        return _mk(
            resource,
            self,
            passed=not low,
            details=details,
            description="Very low CPU limits can cause throttling and latency. Docs: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
            probable="CPU limits set too low (<=100m)",
        )



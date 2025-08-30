from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from kubernetes import client, config


@dataclass
class KubeContext:
    kubeconfig: Optional[str] = None
    context: Optional[str] = None
    in_cluster: bool = False  # retained for future use, but not exposed via CLI

    def to_env(self) -> dict:
        env = {}
        if self.kubeconfig:
            env["KUBECONFIG"] = self.kubeconfig
        if self.context:
            env["KUBECTL_CONTEXT"] = self.context
        if self.in_cluster:
            env["REL_IN_CLUSTER"] = "1"
        return env

    def core_v1(self) -> client.CoreV1Api:
        if self.kubeconfig or self.context:
            config.load_kube_config(config_file=self.kubeconfig, context=self.context)
        else:
            config.load_kube_config()
        return client.CoreV1Api()

    def apps_v1(self) -> client.AppsV1Api:
        # ensure config loaded via core_v1 call path
        self.core_v1()
        return client.AppsV1Api()

    def networking_v1(self) -> client.NetworkingV1Api:
        self.core_v1()
        return client.NetworkingV1Api()

    def rbac_v1(self) -> client.RbacAuthorizationV1Api:
        self.core_v1()
        return client.RbacAuthorizationV1Api()

    def apiextensions_v1(self) -> client.ApiextensionsV1Api:
        self.core_v1()
        return client.ApiextensionsV1Api()

    def autoscaling_v2(self) -> client.AutoscalingV2Api:
        self.core_v1()
        return client.AutoscalingV2Api()

    def apiregistration_v1(self) -> client.ApiregistrationV1Api:
        self.core_v1()
        return client.ApiregistrationV1Api()



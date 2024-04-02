#!/usr/bin/env python3
"""Syncs the kluctl controllers with the kluctl targets."""

from __future__ import annotations

import pathlib
import tempfile
from os import environ

import kubernetes
from fabric import Connection
from ruamel import yaml

YAML = yaml.YAML()

CI = environ.get("CI", "false") == "true"
PROD = (
  environ.get("CI_COMMIT_REF_PROTECTED", "false") == "true"
  or environ.get("FORCE_PROD", "false") == "true"
)
KLUCTL_CRD = {
  "group": "gitops.kluctl.io",
  "version": "v1beta1",
  "plural": "kluctldeployments",
}


def get_kubeconfig() -> pathlib.Path:
  """Get remote kubeconfig file from the server.

  Returns:
      pathlib.Path: Path to the kubeconfig file
  """
  key_filename = environ.get("CLUSTER_KEY")
  ssh_connection = Connection(
    environ.get("CLUSTER_SSH_HOST"), connect_kwargs={"key_filename": key_filename}
  )
  tempdir = tempfile.mkdtemp()
  ssh_connection.get("/etc/rancher/k3s/k3s.conf", f"{tempdir}/k3s.conf")
  return pathlib.Path(f"{tempdir}/k3s.conf")


def get_kluctl_targets() -> list[str]:
  """Extracts the list of targets from the .kluctl.yaml file.

  Raises:
      FileNotFoundError: If the .kluctl.yaml file is not found

  Returns:
      list[str]: List of kluctl targets
  """
  app_deployment_folder = pathlib.Path(__file__).parent.parent / "app-deploy" if not CI else pathlib.Path("./app-deploy")
  if not app_deployment_folder.joinpath(".kluctl.yaml").is_file():
    raise FileNotFoundError(
      f"File {app_deployment_folder.joinpath('.kluctl.yaml')} not found"
    )
  with app_deployment_folder.joinpath(".kluctl.yaml").open() as kluctl_yaml:
    kluctl_config = YAML.load(kluctl_yaml)
    return [deployment["name"] for deployment in kluctl_config["targets"]]


def get_kluctl_controllers() -> list[str]:
  """Get the list of kluctl controllers from the kubernetes cluster.

  Returns:
      list[str]: List of kluctl controllers
  """
  # kubernetes.config.load_kube_config(config_file=get_kubeconfig())
  kubernetes.config.load_kube_config()
  v1_client = kubernetes.client.CustomObjectsApi()
  return [
    controller["metadata"]["name"]
    for controller in v1_client.list_namespaced_custom_object(
      KLUCTL_CRD["group"], KLUCTL_CRD["version"], "default", KLUCTL_CRD["plural"]
    )["items"]
  ]


def compare_kluctl_controllers() -> list[str]:
  """Compare the kluctl controllers with the kluctl targets."""
  kluctl_controllers = get_kluctl_controllers()
  kluctl_targets = get_kluctl_targets()
  modified = []
  for controller in kluctl_controllers:
    if controller not in kluctl_targets:
      delete_kluctl_controller(controller)
      modified.append(controller)
  for target in kluctl_targets:
    if target not in kluctl_controllers:
      create_kluctl_controller(target)
      modified.append(target)
  return modified


def delete_kluctl_controller(target: str) -> None:
  """Delete a kluctl controller for the target.

  Args:
      target (str): The target for which the controller is to be deleted
  """
  kubernetes.config.load_kube_config()
  v1_client = kubernetes.client.CustomObjectsApi()
  v1_client.delete_namespaced_custom_object(
    KLUCTL_CRD["group"],
    KLUCTL_CRD["version"],
    "default",
    KLUCTL_CRD["plural"],
    target,
  )


def create_kluctl_controllers() -> None:
  """Create kluctl controllers for all the targets."""
  for target in get_kluctl_targets():
    create_kluctl_controller(target)


def create_kluctl_controller(target: str) -> None:
  """Create a kluctl controller for the target.

  Args:
      target (str): The target for which the controller is to be created
  """
  kubernetes.config.load_kube_config()
  v1_client = kubernetes.client.CustomObjectsApi()
  kluctl_controller = {
    "apiVersion": f"{KLUCTL_CRD['group']}/{KLUCTL_CRD['version']}",
    "kind": "KluctlDeployment",
    "metadata": {"name": target},
    "spec": {
      "interval": "5m",
      "target": target,
      "source": {
        "git": {
          "url": environ.get("CI_PROJECT_URL")
          if CI
          else "https://github.com/abacf/kube-dep.git",
          "path": "./app-deploy/",
          "ref": {
            "branch": environ.get("CI_COMMIT_REF_NAME") if CI else "main",
          },
        }
      },
      "context": "default",
      "prune": True,
      "delete": True,
    },
  }
  v1_client.create_namespaced_custom_object(
    KLUCTL_CRD["group"],
    KLUCTL_CRD["version"],
    "default",
    KLUCTL_CRD["plural"],
    kluctl_controller,
  )


if __name__ == "__main__":
  print(compare_kluctl_controllers())

#!/usr/bin/env python3
"""Syncs the kluctl controllers with the kluctl targets."""

from __future__ import annotations

import pathlib
import subprocess
import tempfile
from os import environ
from shlex import quote

import kubernetes
from fabric import Connection
from loguru import logger
from ruamel import yaml

YAML = yaml.YAML()

# CRD for kluctl controllers
KLUCTL_CRD = {
  "group": "gitops.kluctl.io",
  "version": "v1beta1",
  "plural": "kluctldeployments",
}

# Being in a Gitlab CI pipeline means that we try use the default CI environment variables
CI = environ.get("CI", "false") == "true"
PROD = (
  environ.get("CI_COMMIT_REF_PROTECTED", "false") == "true"
  or environ.get("FORCE_PROD", "false") == "true"
)
LOCAL = environ.get("LOCAL", "") != ""
CONTROLLER_NAMEPSACE = environ.get("CONTROLLER_NAMEPSACE", "default")
# APP_PATH is the path to the path containing deployments
APP_SUFFIX = environ.get("APP_PATH", "APP_PATH") != ""
if not pathlib.Path(f"{environ.get('CI_PROJECT_DIR', '.')}/{APP_SUFFIX}").is_dir():
  raise FileNotFoundError(
    f"Directory {environ.get('CI_PROJECT_DIR', '.')}/{APP_SUFFIX} not found"
  )
APP_DISCRIMINATOR = environ.get("APP_DISCRIMINATOR", "app-")


def get_kubeconfig() -> pathlib.Path:
  """Get remote kubeconfig file from the server.

  Returns:
      pathlib.Path: Path to the kubeconfig file
  """
  # Get the key file from the environment variables
  key_filename = environ.get("CLUSTER_KEY", "")
  if not pathlib.Path(key_filename).is_file():
    raise FileNotFoundError("Key file not found")
  logger.debug(f"Found key file: {key_filename}")
  # Initialize the SSH connection
  ssh_connection = Connection(
    environ.get("CLUSTER_SSH_HOST", ""), connect_kwargs={"key_filename": key_filename}
  )
  logger.info(f"Connecting to {environ.get('CLUSTER_SSH_HOST', '')}")
  # Open the SSH connection and get the kubeconfig file
  ssh_connection.open()
  tempdir = tempfile.mkdtemp()
  try:
    ssh_connection.get("/etc/rancher/k3s/k3s.conf", f"{tempdir}/k3s.conf")
  except PermissionError:
    logger.error(
      "Permission denied, make sure server has stared with --write-kubeconfig-mode=644"
    )
    raise
  return pathlib.Path(f"{tempdir}/k3s.conf")


def get_kluctl_targets() -> list[str]:
  """Extracts the list of targets from the .kluctl.yaml file.

  Raises:
      FileNotFoundError: If the .kluctl.yaml file is not found

  Returns:
      list[str]: List of kluctl targets
  """
  # In a dev environment, the app-deploy folder is in the root of the repository
  app_deployment_folder = (
    pathlib.Path(__file__).parent.parent / "app-deploy"
    if not CI
    # In a CI environment, the app-deploy folder is in the CI_PROJECT_DIR
    else pathlib.Path(f"{environ.get('CI_PROJECT_DIR', '.')}/{APP_SUFFIX}")
  )
  # Make sure the .kluctl.yaml file exists
  if not app_deployment_folder.joinpath(".kluctl.yaml").is_file():
    raise FileNotFoundError(
      f"File {app_deployment_folder.joinpath('.kluctl.yaml')} not found"
    )
  with app_deployment_folder.joinpath(".kluctl.yaml").open() as kluctl_yaml:
    kluctl_config = YAML.load(kluctl_yaml)
    return [
      # Extract the name of the deployments from the kluctl.yaml file
      deployment["name"]
      for deployment in kluctl_config["targets"]
    ]


def get_kluctl_controllers() -> list[str]:
  """Get the list of kluctl controllers from the kubernetes cluster.

  Returns:
      list[str]: List of kluctl controllers
  """
  if LOCAL:
    # Load the kubeconfig file from the local machine
    kubernetes.config.load_kube_config()
  else:
    # Load the kubeconfig file from the remote server
    kubernetes.config.load_kube_config(config_file=get_kubeconfig())
  # Get CRD client
  v1_client = kubernetes.client.CustomObjectsApi()
  kluctl_controllers = [
    # List all the kluctl controllers and extract their names
    controller["metadata"]["name"]
    for controller in v1_client.list_namespaced_custom_object(
      KLUCTL_CRD["group"],
      KLUCTL_CRD["version"],
      CONTROLLER_NAMEPSACE,
      KLUCTL_CRD["plural"],
    )["items"]
  ]
  return [
    controller for controller in kluctl_controllers if APP_DISCRIMINATOR in controller
  ]


def compare_kluctl_controllers() -> list[str]:
  """Compare the kluctl controllers with the kluctl targets."""
  kluctl_controllers = get_kluctl_controllers()
  kluctl_targets = get_kluctl_targets()
  modified = []
  for controller in kluctl_controllers:
    if controller not in kluctl_targets:
      logger.info(f"Deleting kluctl controller for {controller}")
      delete_kluctl_controller(controller)
      modified.append(controller)
  for target in kluctl_targets:
    if target not in kluctl_controllers:
      logger.info(f"Creating kluctl controller for {controller}")
      create_kluctl_controller(target)
      modified.append(target)
  logger.info(f"Modified controllers: {modified}")
  return modified


def delete_kluctl_controller(target: str) -> None:
  """Delte a kluctl controller for the target.

  Args:
      target (str): Name of the kluctl deployment to be deleted
  """
  v1_client = kubernetes.client.CustomObjectsApi()
  v1_client.delete_namespaced_custom_object(
    KLUCTL_CRD["group"],
    KLUCTL_CRD["version"],
    CONTROLLER_NAMEPSACE,
    KLUCTL_CRD["plural"],
    target,
  )


def create_kluctl_controller(target: str, kubeconfig_path: pathlib.Path) -> None:
  """Create a kluctl controller for the target.

  Args:
      target (str): The target for which the controller is to be created
      kubeconfig_path (pathlib.Path): Path to the kubeconfig file
  """
  # Move to Jinja2 file
  # Create the kluctl controller for the target
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
          "path": APP_SUFFIX,
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
  # Create the kluctl controller in the default namespace
  v1_client = kubernetes.client.CustomObjectsApi()
  v1_client.create_namespaced_custom_object(
    KLUCTL_CRD["group"],
    KLUCTL_CRD["version"],
    "default",
    KLUCTL_CRD["plural"],
    kluctl_controller,
  )
  force_deploy(target, kubeconfig_path)


def force_deploy(target_name: str, kubeconfig: pathlib.Path) -> None:
  """Force deploy the kluctl controllers."""
  # Copy the environment variables
  env = environ.copy()
  env["KUBECONFIG"] = str(kubeconfig)
  subprocess.check_call(
    ["/usr/local/bin/kluctl", "gitops", "deploy", "-y", "--name", quote(target_name)],
    env=env,
  )  # noqa: S603 # Using shlex.quote to escape the target_name


if __name__ == "__main__":
  compare_kluctl_controllers()

#!/usr/bin/env python3

import pathlib
from os import environ
from ruamel import yaml
from fabric import Connection
import tempfile
import kubernetes

YAML = yaml.YAML()

CI = environ.get("CI", "false").lower() == "true"
PROD = environ.get("CI_COMMIT_REF_PROTECTED", "false") == "true" or environ.get("FORCE_PROD", "false").lower() == "true"

def get_kubeconfig():
  key_filename = environ.get("CLUSTER_KEY")
  ssh_connection = Connection(environ.get("PROD_HOST")) if PROD else Connection(environ.get("STAGING_HOST"), connect_kwargs={"key_filename": key_filename})
  tempdir = tempfile.mkdtemp()
  ssh_connection.get("/etc/rancher/k3s/k3s.conf", f"{tempdir}/k3s.conf")
  return f"{tempdir}/k3s.conf"

def get_kluctl_deployments():
    app_deployments = []
    app_deployment_folder = pathlib.Path(__file__).parent.parent / "app-deploy"
    if not app_deployment_folder.joinpath(".kluctl.yaml").is_file():
        return ""
    with open(app_deployment_folder.joinpath(".kluctl.yaml")) as kluctl_yaml:
        kluctl_config = YAML.load(kluctl_yaml)
        for deployment in kluctl_config["targets"]:
          if PROD and "prod" in deployment["name"]:
              app_deployments.append(deployment["name"])
          elif not PROD and "prod" not in deployment["name"]:
              app_deployments.append(deployment["name"])
    return app_deployments

def get_kluctl_controllers():
  app_controllers = []
  kubernetes.config.load_kube_config(config_file=get_kubeconfig())
  v1_client = kubernetes.client.CustomObjectsApi()
  kluctl_crd = {
    "version": "gitops.kluctl.io",
    "group": "kluctl.io",
    "plural": "KluctlDeployment"
  }

if __name__ == "__main__":
    print(get_kluctl_deployments())

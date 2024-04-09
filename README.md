# SAE601

## 1. Introduction

Ce dépot contient les codes sources pour le projet de la SAE601.

Ce projet a pour but de déployer une application web sur un cluster Kubernetes.

Le tout suivant un modèle GitOps.

## 2. Organisation

Le dépot est organisé de la manière suivante:

- `ansible-k3s/`: contient un playbook et les rôles pour déployer avec Ansible
  - un cluster k3s
  - un contrôleur GitOps [kluctl](https://kluctl.io/)
- `app-deploy/`: contient les fichiers
  - de déploiement de l'application [iut-stmalo-sae503](https://github.com/abacf/iut-stmalo-sae503)
  - ainsi qu'un Dockerfile basé sur `alpine` pour construire l'image de l'application.
- `base-deploy/`: contient les fichiers de déploiement de la base applicative
  - [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus)
  - [Traefik](https://doc.traefik.io/traefik/))
- `GitOps/` contient les fichiers
  - permettant la gestion GitOps de l'application avec [kluctl](https://kluctl.io/).

## 3. Déploiement

### 3.1. Prérequis

- Une (ou plusieurs) machine(s) Linux
  - avec un utilisateur disposant des droits `sudo` sans mot de passe.
- `ansible` installé sur la machine de déploiement.
- `kluctl` installé sur la machine de déploiement.

### 3.2. Déploiement du cluster k3s

Pour déployer un cluster k3s :

Lancez le playbook Ansible `ansible-k3s/k3s.yaml` avec la commande suivante:

```bash
ansible-playbook -i <inventory> ansible-k3s/k3s.yaml
```

### 3.4 Déploiement

```bash
./GitOps/deploy.sh
```

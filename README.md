# SAE601

## 1. Introduction

Ce dépot contient les codes sources et les résultats des expériences réalisées dans le cadre du projet de la SAE601.

## 2. Organisation

Le dépot est organisé de la manière suivante:

- `ansible-k3s/`: contient un playbook et les rôles pour déployer un cluster k3s et un contrôleur GitOps kluctl avec Ansible.
- `app-deploy/`: contient les fichiers de déploiement de l'application [iut-stmalo-sae503](https://github.com/abacf/iut-stmalo-sae503) ainsi qu'un Dockerfile basé sur `alpine` pour construire l'image de l'application.
- `base-deploy/`: contient les fichiers de déploiement de la base applicative ([kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) et [Traefik](https://doc.traefik.io/traefik/))
- `GitOps/` contient les fichiers, dont un script, permettant la gestion GitOps de l'application avec [kluctl](https://kluctl.io/).

## 3. Déploiement

### 3.1. Prérequis

- Une (ou plusieurs) machine(s) avec un utilisateur disposant des droits `sudo` sans mot de passe.
- `ansible` installé sur la machine de déploiement.
- `kluctl` installé sur la machine de déploiement.

### 3.2. Déploiement du cluster k3s

Pour déployer un cluster k3s, il suffit de lancer le playbook Ansible `ansible-k3s/k3s.yaml` avec la commande suivante:

```bash
ansible-playbook -i <inventory> ansible-k3s/k3s.yaml
```

### 3.4 Déploiement de la base



### 3.3. Déploiement de l'application

Pour déployer l'application, il suffit de lancer le script `GitOps/deploy.sh` avec la commande suivante:

```bas
./GitOps/deploy.sh
```



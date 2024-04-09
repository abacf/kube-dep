# Gestion de code avec Gitflow

* Nous avons activé avec la protection de la branche main
  * Une Merge Request est obligatoire pour envoyer du code sur la branche main.
  * Les Merge Requests doivent être approuvées par un autre membre de l'équipe.
  * Les Merge Requests doivent passer la de CI avant de pouvoir être fusionnées.
* Cela permets d'isoler l'environement de production de l'environement staging.

## Infrastructure as Code

Nous avons utilisé :

* Ansible pour la configuration de nos serveurs et du cluster K3S.
* Kluctl pour la gestion de nos ressources Kubernetes.

## Intégration continue (CI) avec GitLab-CI

Notre pipeline d'intégration continue (CI) est composé de plusieurs étapes :
:

* [`ansible-lint`](https://ansible-lint.readthedocs.io/)
  * pour vérifier la conformité de notre script Ansible.
* [`ruff`](https://docs.astral.sh/ruff/) pour :
  * linter statiquement le code Python.
  * ainsi que vérifier le formattage du code Python.
* `hahadolint` pour :
  * valider la syntaxe et la structure de nos Dockerfiles.
* [`markdownlint`](https://github.com/DavidAnson/markdownlint-cli2) pour :
  * vérifier la syntaxe
  * la cohérence
  * et le formattage de notre documentation au format Markdown.
* [`syft`](https://github.com/anchore/syft) pour
  * répertorier tous les paquets installés
  * générer une software bill of materials (SBOM).
* [`gitleaks`](https://github.com/gitleaks/gitleaks) pour :
  * scanner le code source à la recherche de secrets sensibles.
* [`mkdocs`](https://www.mkdocs.org/) pour :
  * Contruire la documentation au format HTML.
  * déployer la documentation générée sur les pages GitLab.
* [`kaniko`](https://github.com/GoogleContainerTools/kaniko) pour :
  * construire
  * et pousser les images Docker.
* [`trivy`](https://trivy.dev/) pour :
  * scanner l'image Docker à la recherche de vulnérabilités de sécurité.
  * générer une seconde SBOM pour l'image Docker.
* [`kluctl`](https://kluctl.io/) pour :
  * déployer les ressources Kubernetes au moyen du contrôleur de ressources
    GitOps.

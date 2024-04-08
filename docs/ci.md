#  Gestion de code avec Gitflow :
*	Nous avons activé avec la protection de la branche main, cela veut donc dire qu’il faut faire une pullrequest pour envoyer les modifications d’une autres branche sur main.
# Infrastructure as Code :
*	Pour déployé l’infrastructure sous forme d’infrastructure as code, nous avons utilisé uniquement ansible.

# Intégration continue (CI) avec GitLab-CI

Notre pipeline d'intégration continue (CI) est composé de plusieurs étapes distinctes :
*	Vérification de la syntaxe du script Ansible : Nous utilisons ansible-lint pour vérifier la conformité de notre script Ansible.
*	Test du code Python : Nous utilisons ruff pour tester notre code Python.
*	Validation du Dockerfile : Nous utilisons hahadolint pour valider la syntaxe et la structure de notre Dockerfile.
*	Analyse du markdown : Nous utilisons markdownlint pour vérifier la syntaxe et la cohérence de notre documentation au format Markdown.
*	Liste des paquets installés : Nous utilisons syft pour répertorier tous les paquets installés et générer un fichier JSON.
*	Recherche de secrets exposés : Nous utilisons gitleaks pour scanner le code source à la recherche de secrets sensibles qui pourraient être exposés.
*	Déploiement de la documentation GitLab : Nous utilisons mkdocs pour déployer la documentation générée sur les pages GitLab.
*	Construction de l'image Docker : Nous utilisons kaniko pour construire notre image Docker.
*	Analyse de sécurité de l'image Docker : Nous utilisons trivy pour scanner l'image Docker à la recherche de vulnérabilités de sécurité.
*	Déploiement de l'infrastructure Kubernetes : Une fois que toutes les vérifications sont passées avec succès, nous déployons notre infrastructure Kubernetes pour les environnements de test et de production.

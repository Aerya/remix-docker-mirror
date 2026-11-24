# Miroir Docker Remix

Le code de Remix se trouve dans [Remix-Media/Ether-Remix](https://github.com/Remix-Media/Ether-Remix).

Ce dépôt maintient `ghcr.io/aerya/ether-remix:latest` pour les installations existantes. Les nouvelles installations peuvent utiliser `ghcr.io/remix-media/ether-remix:latest` une fois sa première publication disponible. Aucun changement de volumes ni de configuration n’est nécessaire.

GitHub Actions vérifie la source toutes les 30 minutes (horaire indicatif, soumis aux délais GitHub) et peut être lancé manuellement. Skopeo copie l’index multiarchitecture et tous ses manifestes, sans reconstruire ni exécuter l’image. Les tags `latest` et la version courante sont synchronisés ; les anciennes versions restent disponibles à leur adresse historique. Un échec de lecture de la source ne remplace pas l’image existante.

La seule autorisation de publication est le `GITHUB_TOKEN` éphémère de ce dépôt, avec accès en écriture au paquet historique. Aucun jeton personnel supplémentaire.

## English

Compatibility mirror for existing Remix Docker installations. The canonical source is `ghcr.io/remix-media/ether-remix`; this repository copies its multiarchitecture `latest` and current version to `ghcr.io/aerya/ether-remix` without rebuilding or running the image. Checks are scheduled every 30 minutes, subject to GitHub scheduling delays. Manual dispatch is supported. Existing volumes and application settings remain unchanged.

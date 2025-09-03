[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/onebirdrocks-ebook-mcp-badge.png)](https://mseep.ai/app/onebirdrocks-ebook-mcp)

# Ebook-MCP

<img src="logo.png" alt="ebook-mcp logo" width="132" height="132">

[English](https://github.com/onebirdrocks/ebook-mcp/blob/main/README.md) | [中文](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-CN.md) | [日本語](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-JP.md) | [한국어](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-KR.md) | [Français](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-FR.md) | [Deutsch](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-DE.md)

Ebook-MCP est un serveur Model Context Protocol (MCP) puissant pour le traitement des livres électroniques. Construit sur le [Model Context Protocol](https://github.com/modelcontextprotocol), il fournit un ensemble d'API standardisées pour une intégration transparente entre les applications LLM et les capacités de traitement des livres électroniques. Prend actuellement en charge les formats EPUB et PDF.

## Cas d'usage et valeur

Ebook-MCP transforme la façon dont vous interagissez avec vos livres numériques en permettant des conversations en langage naturel avec vos matériaux de lecture. Il s'intègre parfaitement avec les IDE modernes alimentés par l'IA comme Cursor et Claude, vous permettant de :

- **Gestion intelligente de bibliothèque** : Demandez simplement "Montrez-moi tous les fichiers EPUB dans mon dossier de téléchargements" ou "Trouvez des livres sur GenAI dans ma bibliothèque"
- **Expérience de lecture interactive** : Ayez des conversations naturelles sur vos livres :
  - "Donnez-moi une brève introduction au 'Manuel de l'ingénieur LLM'"
  - "Que couvre le chapitre 3 ?"
  - "Résumez les points clés sur RAG de ce livre"
- **Support d'apprentissage actif** : Améliorez votre apprentissage grâce aux interactions alimentées par l'IA :
  - "Créez un quiz basé sur les concepts RAG du chapitre 5"
  - "Expliquez les différences entre les architectures discutées dans ce chapitre"
  - "Donnez-moi des exercices pratiques basés sur les concepts de cette section"
- **Navigation de contenu** : Naviguez facilement dans vos livres avec des requêtes en langage naturel :
  - "Trouvez toutes les sections discutant de l'ingénierie des prompts"
  - "Montrez-moi les chapitres sur le fine-tuning"
  - "Amenez-moi à la partie sur les bases de données vectorielles"

En comblant le fossé entre les livres électroniques traditionnels et les capacités de l'IA, Ebook-MCP aide les lecteurs à extraire plus de valeur de leur bibliothèque numérique grâce à des interactions intuitives basées sur la conversation.

Démo rapide - Exécuter avec DeepSeek (Veuillez vérifier tous les exemples avec Claude/OpenAI dans le dossier mcp-client-example)
```
Requête : Veuillez vérifier tous les livres epub dans mon dossier de téléchargement. L'ID utilisateur est onebird.
......

Requête : Pouvez-vous me poser quelques questions pour tester ma compréhension de ce livre ?

Réponse : Bien sûr ! Voici 5 questions sur Elon Musk par Walter Isaacson pour tester votre compréhension du livre. Veuillez répondre en vous basant sur vos connaissances — je donnerai des commentaires et ajouterai des détails après chaque réponse.

Question 1 :
Comment l'enfance et le contexte familial de Musk ont-ils façonné sa personnalité et sa carrière plus tard dans la vie ?
(Indice : Sa relation avec son père, grandir en Afrique du Sud, etc.)

Question 2 :
Zip2 et X.com (plus tard PayPal) étaient les premières startups de Musk. Quels problèmes ont-ils résolus ? Comment Musk a-t-il finalement quitté ces entreprises ?
(Indice : Le modèle commercial de Zip2, la fusion de X.com avec Confinity, etc.)

Question 3 :
En 2008, SpaceX et Tesla étaient tous deux au bord de la faillite. Comment Musk a-t-il sauvé ces deux entreprises ?
(Indice : Le quatrième lancement de Falcon 1, le contrat NASA, le sauvetage de dernière minute de Tesla, etc.)

Question 4 :
Quelles controverses entourent le style de gestion de Musk ? Quels incidents spécifiques dans le livre illustrent sa culture de travail "hardcore" ou "extrême" ?
(Indice : "L'enfer de production" de l'usine Fremont, les licenciements Twitter, etc.)

Question 5 :
Quelle est l'attitude de Musk envers l'Intelligence Artificielle (IA) ? Pourquoi a-t-il simultanément soutenu OpenAI et Neuralink, qui semblent avoir des objectifs contradictoires ?
(Indice : L'IA comme menace existentielle, vision d'interface cerveau-machine, etc.)

Veuillez répondre à chaque question. Je fournirai des commentaires et des détails supplémentaires ou corrigerai tout malentendu !
(Si une question n'est pas claire, n'hésitez pas à me demander.)

Requête :
Question 1 : L'attitude abusive de son père l'a rendu moins empathique envers les autres.
Question 2 : Zip2 a résolu le problème des cartes électroniques et des pages jaunes en ligne. X.com a résolu les paiements en ligne.
Question 3 : Il a obtenu un contrat avec la NASA. Tesla a résolu ses problèmes de production en construisant une usine en Chine.
Question 4 : Je ne sais pas. Veuillez répondre pour moi.
Question 5 : Il croit que la technologie open-source est nécessaire pour s'assurer que l'IA soit sûre et ouverte.

Réponse : Vos réponses ont capturé quelques points clés du livre. Laissez-moi ajouter des détails, corriger quelques inexactitudes et fournir plus de contexte pour les questions 4 et 5 :

Question 1 — Correction et complément
Influence de son père :
Le père de Musk, Errol, était effectivement extrêmement dur — par exemple, forçant le jeune Elon à s'agenouiller et compter des grains de riz pendant des heures. Le livre souligne que cette désensibilisation émotionnelle a façonné Musk en une personne extrêmement orientée vers les objectifs — indifférente à la souffrance des autres mais obsessionnellement engagée envers ses objectifs.

Impact inverse :
Ce n'est pas que Musk soit incapable d'empathie — elle est sélective. Par exemple, il peut traiter les employés froidement mais étudier personnellement l'équipement médical pour les problèmes de santé de son fils X.

Question 2 — Correction et complément
Zip2 :
Essentiellement un service de pages jaunes en ligne + navigation cartographique (aidant les journaux à aller en ligne). Musk a écrit une grande partie du code initial lui-même et dormait au bureau. Finalement, Compaq a acquis Zip2 pour 307 millions de dollars (Musk a reçu 22 millions de dollars).

X.com :
Pas seulement les paiements en ligne — c'était la tentative de Musk de créer une plateforme financière complète (visant à remplacer les banques). Plus tard fusionné avec Confinity (le précurseur de PayPal). Musk a été évincé en raison de conflits internes, mais quand eBay a acquis PayPal, Musk a gagné 180 millions de dollars.
(Note : Musk a plus tard racheté le domaine X.com — c'est maintenant le nom de la société mère de Twitter).

Question 3 — Correction et complément
SpaceX :
En 2008, Falcon 1 a réussi lors de son quatrième lancement (après trois échecs qui ont épuisé leurs fonds). Juste après cela, SpaceX a obtenu un contrat NASA de 1,6 milliard de dollars pour le réapprovisionnement de fret — une bouée de sauvetage pour l'entreprise.

Tesla :
En 2008, Tesla a survécu grâce à un investissement de 50 millions de dollars de Daimler et un prêt du Département de l'Énergie américain.
La construction de la Gigafactory en Chine (2019) est venue beaucoup plus tard. Dans les premières années, la survie dépendait du lancement de la Model S (2012) et du pari personnel de Musk — vendre tous ses biens immobiliers pour financer Tesla.

Question 4 — Explication : Controverse autour de son style de gestion
Culture "Hardcore" :

Chez SpaceX/Tesla : Musk exigeait que les employés travaillent 80+ heures par semaine, dormant même à l'usine. ("Si vous n'êtes pas ici, votre remplaçant l'est.")

Après l'acquisition de Twitter : Il a immédiatement licencié 75% du personnel et demandé aux employés restants de signer un "engagement hardcore" — acceptant de longues heures et une production de haute intensité.

Cas extrêmes :

À l'usine Fremont : Pendant "l'enfer de production" de la Model 3, Musk dormait sur la ligne de production et a une fois crié sur les employés en les appelant "pires que des chiens" (il s'est excusé plus tard).

Licenciement de cadres : Musk a une fois licencié sur-le-champ un cadre supérieur de Tesla parce que la taille de police dans leur présentation PowerPoint n'était pas assez grande.

Question 5 — Correction et complément
Théorie de la menace IA :
Musk croit que l'IA pourrait détruire l'humanité ("plus dangereuse que les armes nucléaires"). Par conséquent :

OpenAI : Il l'a initialement soutenu pour promouvoir une IA sûre et open-source (mais est parti plus tard en raison de disputes sur le contrôle).

Neuralink : Il vise à utiliser les interfaces cerveau-machine pour fusionner les humains avec l'IA — pour empêcher les humains d'être laissés pour compte.

Contradictions :
Tout en avertissant des risques de l'IA, Musk pousse simultanément la technologie de conduite entièrement autonome (FSD) chez Tesla et a fondé xAI pour rechercher l'Intelligence Artificielle Générale (AGI).

Évaluation globale :
✅ Vous avez capturé les événements clés avec précision, mais les détails doivent être renforcés (comme les chronologies et les chiffres spécifiques).
🔍 Domaines recommandés pour une étude plus approfondie : Le style de gestion multi-thread de Musk (dirigeant cinq entreprises simultanément) et sa compétence en manipulation médiatique (gouverner par Twitter).
```

## Fonctionnalités

### Support EPUB
- Extraire les métadonnées (titre, auteur, date de publication, etc.)
- Extraire la table des matières
- Extraire le contenu des chapitres (avec sortie Markdown)
- Traitement par lots des fichiers EPUB

### Support PDF
- Extraire les métadonnées (titre, auteur, date de création, etc.)
- Extraire la table des matières
- Extraire le contenu par numéro de page
- Extraire le contenu par titre de chapitre
- Support de sortie Markdown
- Traitement par lots des fichiers PDF

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. Installer les dépendances en utilisant `uv` :
```bash
uv pip install -e .
```

## Utilisation

### Démarrer le serveur MCP en mode développement

Exécuter le serveur en mode développement :
```bash
uv run mcp dev src/ebook_mcp/main.py
```

Vous pouvez visiter http://localhost:5173/ à des fins de test et de débogage
Vous pouvez également installer l'inspecteur pour le test.
```
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

### Démarrer le serveur MCP en mode production

Exécuter le serveur :
```bash
uv run src/ebook_mcp/main.py
```

#### Configurer le MCP dans Cursor

Ajouter la configuration suivante dans Cursor
```bash
"ebook-mcp":{
            "command": "uv",
            "args": [
                "--directory",
                "/Users/onebird/github/ebook-mcp/src/ebook_mcp/",
                "run",
                "main.py"
            ]
        }
```

### Exemples de traitement EPUB

```python
# Obtenir tous les fichiers EPUB dans un répertoire
epub_files = get_all_epub_files("/path/to/books")

# Obtenir les métadonnées EPUB
metadata = get_metadata("/path/to/book.epub")

# Obtenir la table des matières
toc = get_toc("/path/to/book.epub")

# Obtenir le contenu d'un chapitre spécifique (au format Markdown)
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### Exemples de traitement PDF

```python
# Obtenir tous les fichiers PDF dans un répertoire
pdf_files = get_all_pdf_files("/path/to/books")

# Obtenir les métadonnées PDF
metadata = get_pdf_metadata("/path/to/book.pdf")

# Obtenir la table des matières
toc = get_pdf_toc("/path/to/book.pdf")

# Obtenir le contenu d'une page spécifique
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# Obtenir le contenu d'un chapitre spécifique
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## Référence API

### APIs EPUB

#### `get_all_epub_files(path: str) -> List[str]`
Obtenir tous les fichiers EPUB dans le répertoire spécifié.

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
Obtenir les métadonnées d'un fichier EPUB.

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
Obtenir la table des matières d'un fichier EPUB.

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
Obtenir le contenu du chapitre au format Markdown.

### APIs PDF

#### `get_all_pdf_files(path: str) -> List[str]`
Obtenir tous les fichiers PDF dans le répertoire spécifié.

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
Obtenir les métadonnées d'un fichier PDF.

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
Obtenir la table des matières d'un fichier PDF.

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
Obtenir le contenu en texte brut d'une page spécifique.

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
Obtenir le contenu formaté Markdown d'une page spécifique.

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
Obtenir le contenu du chapitre et les numéros de page correspondants par titre de chapitre.

## Dépendances

Les dépendances clés incluent :
- ebooklib : Traitement des fichiers EPUB
- PyPDF2 : Traitement PDF de base
- PyMuPDF : Traitement PDF avancé
- beautifulsoup4 : Analyse HTML
- html2text : Conversion HTML vers Markdown
- pydantic : Validation des données
- fastmcp : Framework de serveur MCP

## Notes importantes

1. Le traitement PDF dépend de la table des matières du document. Certaines fonctionnalités peuvent ne pas fonctionner si la table des matières n'est pas disponible.
2. Pour les gros fichiers PDF, il est recommandé de traiter par plages de pages pour éviter de charger tout le fichier en une fois.
3. Les ID de chapitre EPUB doivent être obtenus à partir de la structure de la table des matières.

## Architecture

```
           ┌────────────────────────────┐
           │      Couche Agent          │
           │  - Stratégie de traduction │
           │  - Vérification cohérence  │
           │  - Appel LLM & Interaction │
           └────────────▲─────────────┘
                        │ Appels d'outils
           ┌────────────┴─────────────┐
           │     Couche Outils MCP    │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ Appels Système/IO
           ┌────────────┴─────────────┐
           │   Couche Base Système    │
           │  - Lecture de fichiers   │
           │  - Analyse ebooklib      │
           │  - Stockage/Vérif. chemin│
           └────────────────────────────┘
```

## Contribution

Nous accueillons les Issues et Pull Requests !

Pour des informations détaillées sur les changements récents, veuillez consulter [CHANGELOG.md](CHANGELOG.md).
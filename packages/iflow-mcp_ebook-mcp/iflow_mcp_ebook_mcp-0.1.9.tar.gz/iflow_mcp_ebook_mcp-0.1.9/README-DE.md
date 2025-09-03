[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/onebirdrocks-ebook-mcp-badge.png)](https://mseep.ai/app/onebirdrocks-ebook-mcp)

# Ebook-MCP

<img src="logo.png" alt="ebook-mcp logo" width="132" height="132">

[English](https://github.com/onebirdrocks/ebook-mcp/blob/main/README.md) | [中文](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-CN.md) | [日本語](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-JP.md) | [한국어](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-KR.md) | [Français](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-FR.md) | [Deutsch](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-DE.md)

Ebook-MCP ist ein leistungsstarker Model Context Protocol (MCP) Server für die Verarbeitung elektronischer Bücher. Aufgebaut auf dem [Model Context Protocol](https://github.com/modelcontextprotocol), bietet es eine Reihe standardisierter APIs für die nahtlose Integration zwischen LLM-Anwendungen und E-Book-Verarbeitungsfunktionen. Unterstützt derzeit EPUB- und PDF-Formate.

## Anwendungsfälle und Wert

Ebook-MCP transformiert die Art, wie Sie mit Ihren digitalen Büchern interagieren, indem es natürlichsprachliche Gespräche mit Ihren Lesematerialien ermöglicht. Es integriert sich nahtlos in moderne KI-gestützte IDEs wie Cursor und Claude und ermöglicht Ihnen:

- **Intelligente Bibliotheksverwaltung**: Fragen Sie einfach "Zeigen Sie mir alle EPUB-Dateien in meinem Downloads-Ordner" oder "Finden Sie Bücher über GenAI in meiner Bibliothek"
- **Interaktive Leseerfahrung**: Führen Sie natürliche Gespräche über Ihre Bücher:
  - "Geben Sie mir eine kurze Einführung in das 'LLM Engineer Handbook'"
  - "Was wird in Kapitel 3 behandelt?"
  - "Fassen Sie die wichtigsten Punkte über RAG aus diesem Buch zusammen"
- **Aktive Lernunterstützung**: Verbessern Sie Ihr Lernen durch KI-gestützte Interaktionen:
  - "Erstellen Sie ein Quiz basierend auf den RAG-Konzepten aus Kapitel 5"
  - "Erklären Sie die Unterschiede zwischen den in diesem Kapitel diskutierten Architekturen"
  - "Geben Sie mir praktische Übungen basierend auf den Konzepten in diesem Abschnitt"
- **Inhaltsnavigation**: Navigieren Sie einfach durch Ihre Bücher mit natürlichsprachlichen Abfragen:
  - "Finden Sie alle Abschnitte, die Prompt Engineering diskutieren"
  - "Zeigen Sie mir die Kapitel über Fine-Tuning"
  - "Bringen Sie mich zu dem Teil über Vektordatenbanken"

Durch die Überbrückung der Lücke zwischen traditionellen E-Books und KI-Fähigkeiten hilft Ebook-MCP Lesern dabei, mehr Wert aus ihrer digitalen Bibliothek durch intuitive, gesprächsbasierte Interaktionen zu extrahieren.

Schnelle Demo - Ausführung mit DeepSeek (Bitte überprüfen Sie alle Beispiele mit Claude/OpenAI im mcp-client-example Ordner)
```
Anfrage: Bitte überprüfen Sie alle epub-Bücher in meinem Download-Ordner. Benutzer-ID ist onebird.
......

Anfrage: Können Sie mir ein paar Fragen stellen, um mein Verständnis dieses Buches zu testen?

Antwort: Sicher! Hier sind 5 Fragen über Elon Musk von Walter Isaacson, um Ihr Verständnis des Buches zu testen. Bitte antworten Sie basierend auf Ihrem Wissen — ich werde Feedback geben und Details nach jeder Antwort hinzufügen.

Frage 1:
Wie haben Musks Kindheit und familiärer Hintergrund seine Persönlichkeit und Karriere später im Leben geprägt?
(Hinweis: Seine Beziehung zu seinem Vater, Aufwachsen in Südafrika, etc.)

Frage 2:
Zip2 und X.com (später PayPal) waren Musks frühe Startups. Welche Probleme haben sie gelöst? Wie ist Musk schließlich aus diesen Unternehmen ausgestiegen?
(Hinweis: Zip2s Geschäftsmodell, X.coms Fusion mit Confinity, etc.)

Frage 3:
2008 standen sowohl SpaceX als auch Tesla am Rande des Bankrotts. Wie hat Musk diese beiden Unternehmen gerettet?
(Hinweis: Falcon 1s vierter Start, NASA-Vertrag, Teslas Last-Minute-Rettung, etc.)

Frage 4:
Welche Kontroversen umgeben Musks Führungsstil? Welche spezifischen Vorfälle im Buch veranschaulichen seine "Hardcore"- oder "extreme" Arbeitskultur?
(Hinweis: Fremont-Fabrik "Produktionshölle", Twitter-Entlassungen, etc.)

Frage 5:
Was ist Musks Einstellung zur Künstlichen Intelligenz (KI)? Warum unterstützte er gleichzeitig sowohl OpenAI als auch Neuralink, die widersprüchliche Ziele zu haben scheinen?
(Hinweis: KI als existenzielle Bedrohung, Gehirn-Maschine-Schnittstellen-Vision, etc.)

Bitte beantworten Sie jede Frage. Ich werde Feedback und zusätzliche Details geben oder Missverständnisse korrigieren!
(Wenn eine Frage unklar ist, fragen Sie mich gerne.)

Anfrage:
Frage 1: Die missbräuchliche Haltung seines Vaters machte ihn weniger empathisch gegenüber anderen.
Frage 2: Zip2 löste das Problem elektronischer Karten und Online-Gelbe Seiten. X.com löste Online-Zahlungen.
Frage 3: Er sicherte sich einen Vertrag mit der NASA. Tesla löste seine Produktionsprobleme durch den Bau einer Fabrik in China.
Frage 4: Ich weiß es nicht. Bitte antworten Sie für mich.
Frage 5: Er glaubt, dass Open-Source-Technologie notwendig ist, um sicherzustellen, dass KI sicher und offen ist.

Antwort: Ihre Antworten haben einige wichtige Punkte aus dem Buch erfasst. Lassen Sie mich Details hinzufügen, einige Ungenauigkeiten korrigieren und weiteren Hintergrund für die Fragen 4 und 5 liefern:

Frage 1 — Korrektur und Ergänzung
Einfluss seines Vaters:
Musks Vater Errol war tatsächlich extrem hart — zum Beispiel zwang er den jungen Elon, stundenlang zu knien und Reiskörner zu zählen. Das Buch betont, dass diese emotionale Desensibilisierung Musk zu einer extrem zielorientierten Person formte — gleichgültig gegenüber dem Leiden anderer, aber obsessiv seinen Zielen verpflichtet.

Umgekehrte Auswirkung:
Es ist nicht so, dass Musk unfähig zur Empathie ist — sie ist selektiv. Zum Beispiel kann er Angestellte kalt behandeln, aber persönlich medizinische Geräte für die Gesundheitsprobleme seines Sohnes X studieren.

Frage 2 — Korrektur und Ergänzung
Zip2:
Im Wesentlichen ein Online-Gelbe-Seiten + Kartennavigationsdienst (half Zeitungen online zu gehen). Musk schrieb viel des frühen Codes selbst und schlief im Büro. Schließlich erwarb Compaq Zip2 für 307 Millionen Dollar (Musk erhielt 22 Millionen Dollar).

X.com:
Nicht nur Online-Zahlungen — es war Musks Versuch, eine umfassende Finanzplattform zu schaffen (mit dem Ziel, Banken zu ersetzen). Später fusionierte es mit Confinity (dem Vorläufer von PayPal). Musk wurde aufgrund interner Konflikte verdrängt, aber als eBay PayPal erwarb, verdiente Musk 180 Millionen Dollar.
(Hinweis: Musk kaufte später die Domain X.com zurück — es ist jetzt der Name von Twitters Muttergesellschaft).

Frage 3 — Korrektur und Ergänzung
SpaceX:
2008 gelang Falcon 1 beim vierten Start (nach drei Fehlschlägen, die ihre Mittel erschöpften). Direkt danach sicherte sich SpaceX einen 1,6-Milliarden-Dollar-NASA-Vertrag für Frachtversorgung — eine Rettungsleine für das Unternehmen.

Tesla:
2008 überlebte Tesla durch eine 50-Millionen-Dollar-Investition von Daimler und ein Darlehen vom US-Energieministerium.
Der Bau der Gigafactory in China (2019) kam viel später. In den frühen Jahren hing das Überleben vom Start des Model S (2012) und Musks persönlichem Einsatz ab — dem Verkauf all seiner Immobilien zur Finanzierung von Tesla.

Frage 4 — Erklärung: Kontroverse um seinen Führungsstil
"Hardcore"-Kultur:

Bei SpaceX/Tesla: Musk verlangte von Angestellten, 80+ Stunden pro Woche zu arbeiten, sogar in der Fabrik zu schlafen. ("Wenn Sie nicht hier sind, ist Ihr Ersatz da.")

Nach der Twitter-Übernahme: Er entließ sofort 75% der Belegschaft und verlangte von den verbleibenden Angestellten, ein "Hardcore-Commitment" zu unterschreiben — Zustimmung zu langen Stunden und hochintensiver Leistung.

Extreme Fälle:

In der Fremont-Fabrik: Während der "Produktionshölle" des Model 3 schlief Musk auf der Produktionslinie und schrie einmal Angestellte an, nannte sie "schlechter als Hunde" (er entschuldigte sich später).

Entlassung von Führungskräften: Musk entließ einmal eine Tesla-Führungskraft auf der Stelle, weil die Schriftgröße in ihrer PowerPoint-Präsentation nicht groß genug war.

Frage 5 — Korrektur und Ergänzung
KI-Bedrohungstheorie:
Musk glaubt, dass KI die Menschheit zerstören könnte ("gefährlicher als Atomwaffen"). Daher:

OpenAI: Er unterstützte es zunächst, um sichere, Open-Source-KI zu fördern (verließ aber später aufgrund von Streitigkeiten über die Kontrolle).

Neuralink: Er zielt darauf ab, Gehirn-Maschine-Schnittstellen zu verwenden, um Menschen mit KI zu verschmelzen — um zu verhindern, dass Menschen zurückgelassen werden.

Widersprüche:
Während er vor KI-Risiken warnt, treibt Musk gleichzeitig die Full Self-Driving (FSD) Technologie bei Tesla voran und hat xAI gegründet, um Artificial General Intelligence (AGI) zu erforschen.

Gesamtbewertung:
✅ Sie haben die wichtigsten Ereignisse genau erfasst, aber die Details müssen verstärkt werden (wie Zeitpläne und spezifische Zahlen).
🔍 Empfohlene Bereiche für weiteres Studium: Musks Multi-Thread-Führungsstil (gleichzeitiges Führen von fünf Unternehmen) und seine Fähigkeit zur Medienmanipulation (Regieren durch Twitter).
```

## Funktionen

### EPUB-Unterstützung
- Metadaten extrahieren (Titel, Autor, Veröffentlichungsdatum, etc.)
- Inhaltsverzeichnis extrahieren
- Kapitelinhalt extrahieren (mit Markdown-Ausgabe)
- Stapelverarbeitung von EPUB-Dateien

### PDF-Unterstützung
- Metadaten extrahieren (Titel, Autor, Erstellungsdatum, etc.)
- Inhaltsverzeichnis extrahieren
- Inhalt nach Seitenzahl extrahieren
- Inhalt nach Kapiteltitel extrahieren
- Markdown-Ausgabe-Unterstützung
- Stapelverarbeitung von PDF-Dateien

## Installation

1. Repository klonen:
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. Abhängigkeiten mit `uv` installieren:
```bash
uv pip install -e .
```

## Verwendung

### MCP-Server im Entwicklungsmodus starten

Server im Entwicklungsmodus ausführen:
```bash
uv run mcp dev src/ebook_mcp/main.py
```

Sie können http://localhost:5173/ für Test- und Debugging-Zwecke besuchen
Sie können auch den Inspector für den Test installieren.
```
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

### MCP-Server im Produktionsmodus starten

Server ausführen:
```bash
uv run src/ebook_mcp/main.py
```

#### MCP in Cursor konfigurieren

Folgende Konfiguration in Cursor hinzufügen
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

### EPUB-Verarbeitungsbeispiele

```python
# Alle EPUB-Dateien in einem Verzeichnis abrufen
epub_files = get_all_epub_files("/path/to/books")

# EPUB-Metadaten abrufen
metadata = get_metadata("/path/to/book.epub")

# Inhaltsverzeichnis abrufen
toc = get_toc("/path/to/book.epub")

# Spezifischen Kapitelinhalt abrufen (im Markdown-Format)
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### PDF-Verarbeitungsbeispiele

```python
# Alle PDF-Dateien in einem Verzeichnis abrufen
pdf_files = get_all_pdf_files("/path/to/books")

# PDF-Metadaten abrufen
metadata = get_pdf_metadata("/path/to/book.pdf")

# Inhaltsverzeichnis abrufen
toc = get_pdf_toc("/path/to/book.pdf")

# Spezifischen Seiteninhalt abrufen
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# Spezifischen Kapitelinhalt abrufen
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## API-Referenz

### EPUB-APIs

#### `get_all_epub_files(path: str) -> List[str]`
Alle EPUB-Dateien im angegebenen Verzeichnis abrufen.

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
Metadaten aus einer EPUB-Datei abrufen.

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
Inhaltsverzeichnis aus einer EPUB-Datei abrufen.

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
Kapitelinhalt im Markdown-Format abrufen.

### PDF-APIs

#### `get_all_pdf_files(path: str) -> List[str]`
Alle PDF-Dateien im angegebenen Verzeichnis abrufen.

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
Metadaten aus einer PDF-Datei abrufen.

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
Inhaltsverzeichnis aus einer PDF-Datei abrufen.

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
Klartext-Inhalt von einer spezifischen Seite abrufen.

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
Markdown-formatierten Inhalt von einer spezifischen Seite abrufen.

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
Kapitelinhalt und entsprechende Seitenzahlen nach Kapiteltitel abrufen.

## Abhängigkeiten

Wichtige Abhängigkeiten umfassen:
- ebooklib: EPUB-Dateiverarbeitung
- PyPDF2: Grundlegende PDF-Verarbeitung
- PyMuPDF: Erweiterte PDF-Verarbeitung
- beautifulsoup4: HTML-Parsing
- html2text: HTML zu Markdown Konvertierung
- pydantic: Datenvalidierung
- fastmcp: MCP-Server-Framework

## Wichtige Hinweise

1. PDF-Verarbeitung basiert auf dem Inhaltsverzeichnis des Dokuments. Einige Funktionen funktionieren möglicherweise nicht, wenn das Inhaltsverzeichnis nicht verfügbar ist.
2. Für große PDF-Dateien wird empfohlen, nach Seitenbereichen zu verarbeiten, um das Laden der gesamten Datei auf einmal zu vermeiden.
3. EPUB-Kapitel-IDs müssen aus der Inhaltsverzeichnisstruktur abgerufen werden.

## Architektur

```
           ┌────────────────────────────┐
           │         Agent-Schicht      │
           │  - Übersetzungsstrategie   │
           │  - Stil-Konsistenzprüfung  │
           │  - LLM-Aufruf & Interaktion│
           └────────────▲─────────────┘
                        │ Tool-Aufrufe
           ┌────────────┴─────────────┐
           │        MCP-Tool-Schicht  │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ System/IO-Aufrufe
           ┌────────────┴─────────────┐
           │     System-Basis-Schicht │
           │  - Datei-Lesen           │
           │  - ebooklib-Parsing      │
           │  - Dateipfad-Speicher/Prüf│
           └────────────────────────────┘
```

## Mitwirken

Wir begrüßen Issues und Pull Requests!

Detaillierte Informationen zu den letzten Änderungen finden Sie in [CHANGELOG.md](CHANGELOG.md).
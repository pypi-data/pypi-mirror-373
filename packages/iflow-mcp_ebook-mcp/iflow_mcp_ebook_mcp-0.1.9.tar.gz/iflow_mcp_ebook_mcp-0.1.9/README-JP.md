[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/onebirdrocks-ebook-mcp-badge.png)](https://mseep.ai/app/onebirdrocks-ebook-mcp)

# Ebook-MCP

<img src="logo.png" alt="ebook-mcp logo" width="132" height="132">

[English](https://github.com/onebirdrocks/ebook-mcp/blob/main/README.md) | [中文](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-CN.md) | [日本語](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-JP.md) | [한국어](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-KR.md) | [Français](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-FR.md) | [Deutsch](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-DE.md)

Ebook-MCPは、電子書籍を処理するための強力なModel Context Protocol（MCP）サーバーです。[Model Context Protocol](https://github.com/modelcontextprotocol)上に構築され、LLMアプリケーションと電子書籍処理機能間のシームレスな統合のための標準化されたAPIセットを提供します。現在、EPUBおよびPDF形式をサポートしています。

## 使用例と価値

Ebook-MCPは、読書資料との自然言語による会話を可能にすることで、デジタル書籍との相互作用を変革します。CursorやClaudeなどの現代的なAI駆動IDEとシームレスに統合し、以下のことを可能にします：

- **スマートライブラリ管理**：「ダウンロードフォルダ内のすべてのEPUBファイルを表示して」や「ライブラリ内のGenAIに関する本を見つけて」と簡単に尋ねることができます
- **インタラクティブな読書体験**：本について自然な会話を行う：
  - 「『LLMエンジニアハンドブック』の簡単な紹介をして」
  - 「第3章では何が扱われていますか？」
  - 「この本からRAGに関する要点をまとめて」
- **アクティブラーニングサポート**：AI駆動のインタラクションを通じて学習を強化：
  - 「第5章のRAG概念に基づいてクイズを作成して」
  - 「この章で議論されているアーキテクチャの違いを説明して」
  - 「このセクションの概念に基づいて実践的な演習を提供して」
- **コンテンツナビゲーション**：自然言語クエリで本を簡単にナビゲート：
  - 「プロンプトエンジニアリングについて議論しているすべてのセクションを見つけて」
  - 「ファインチューニングに関する章を表示して」
  - 「ベクターデータベースに関する部分に案内して」

従来の電子書籍とAI機能の間のギャップを埋めることで、Ebook-MCPは読者が直感的で会話ベースのインタラクションを通じてデジタルライブラリからより多くの価値を抽出するのを支援します。

クイックデモ - DeepSeekで実行（mcp-client-exampleフォルダ下のClaude/OpenAIのすべての例をご確認ください）
```
クエリ：私のダウンロードフォルダ内のすべてのepub本をチェックしてください。ユーザーIDはonebirdです。
......

クエリ：この本の理解度をテストするためにいくつか質問してもらえますか？

回答：もちろんです！ウォルター・アイザックソンの『イーロン・マスク』についてあなたの理解をテストするための5つの質問があります。あなたの知識に基づいて答えてください — 各回答の後にフィードバックと詳細を追加します。

質問1：
マスクの幼少期と家族背景は、後の人生での彼の性格とキャリアをどのように形作りましたか？
（ヒント：父親との関係、南アフリカでの成長など）

質問2：
Zip2とX.com（後のPayPal）はマスクの初期のスタートアップでした。これらはどのような問題を解決しましたか？マスクは最終的にこれらの会社からどのように退出しましたか？
（ヒント：Zip2のビジネスモデル、X.comとConfinityの合併など）

質問3：
2008年、SpaceXとTeslaの両方が破産の危機に瀕していました。マスクはこれら2つの会社をどのように救いましたか？
（ヒント：Falcon 1の4回目の打ち上げ、NASAの契約、Teslaの土壇場での救済など）

質問4：
マスクの管理スタイルを巡ってどのような論争がありますか？本の中で彼の「ハードコア」または「極端な」労働文化を示す具体的な事件は何ですか？
（ヒント：フリーモント工場の「生産地獄」、Twitterのレイオフなど）

質問5：
人工知能（AI）に対するマスクの態度は何ですか？なぜ彼は同時にOpenAIとNeuralinkの両方を支援したのですか？これらは相反する目標を持っているように見えます。
（ヒント：存在的脅威としてのAI、ブレイン・マシン・インターフェースのビジョンなど）

各質問に答えてください。フィードバックと追加の詳細を提供し、誤解があれば訂正します！
（質問が不明な場合は、お気軽にお尋ねください。）

クエリ：
質問1：父親の虐待的な態度により、彼は他人に対して共感が少なくなりました。
質問2：Zip2は電子地図とオンラインイエローページの問題を解決しました。X.comはオンライン決済を解決しました。
質問3：彼はNASAとの契約を確保しました。Teslaは中国に工場を建設することで生産問題を解決しました。
質問4：わかりません。私のために答えてください。
質問5：彼はAIが安全でオープンであることを確保するためにオープンソース技術が必要だと信じています。

回答：あなたの答えは本からいくつかの重要なポイントを捉えています。質問4と5について詳細を追加し、いくつかの不正確さを訂正し、さらなる背景を提供させてください：

質問1 — 訂正と補足
父親の影響：
マスクの父親エロルは確かに極めて厳しく — 例えば、幼いイーロンに何時間も跪いて米粒を数えることを強制しました。本書は、この感情的な鈍感化がマスクを極めて目標志向の人間に形作ったことを強調しています — 他人の苦痛には無関心だが、自分の目標に執着的にコミットしています。

逆の影響：
マスクが共感能力がないということではありません — それは選択的です。例えば、従業員を冷たく扱うかもしれませんが、息子Xの健康問題のために医療機器を個人的に研究します。

質問2 — 訂正と補足
Zip2：
本質的にはオンラインイエローページ + 地図ナビゲーションサービス（新聞のオンライン化を支援）。マスクは初期のコードの多くを自分で書き、オフィスで寝泊まりしました。最終的に、CompaqがZip2を3億700万ドルで買収（マスクは2200万ドルを受け取りました）。

X.com：
単なるオンライン決済ではありません — これは包括的な金融プラットフォームを作成するマスクの試み（銀行の置き換えを目指していました）。後にConfinity（PayPalの前身）と合併。マスクは内部対立により追放されましたが、eBayがPayPalを買収した際、マスクは1億8000万ドルを稼ぎました。
（注：マスクは後にX.comドメインを買い戻しました — 現在はTwitterの親会社名です）。

質問3 — 訂正と補足
SpaceX：
2008年、Falcon 1は4回目の打ち上げで成功しました（3回の失敗で資金が枯渇した後）。その直後、SpaceXは貨物補給のための16億ドルのNASA契約を確保 — 会社の生命線でした。

Tesla：
2008年、TeslaはDaimlerからの5000万ドルの投資と米国エネルギー省からの融資により生き残りました。
中国でのギガファクトリー建設（2019年）はずっと後のことです。初期の頃、生存はModel Sの発売（2012年）とマスクの個人的な賭け — Teslaに資金提供するためにすべての不動産を売却することに依存していました。

質問4 — 説明：彼の管理スタイルを巡る論争
「ハードコア」文化：

SpaceX/Teslaで：マスクは従業員に週80時間以上の労働を要求し、工場で寝ることさえありました。（「あなたがここにいなければ、あなたの代替者がいます。」）

Twitter買収後：彼は即座にスタッフの75%を解雇し、残りの従業員に「ハードコアコミットメント」への署名を求めました — 長時間と高強度の出力に同意することです。

極端なケース：

フリーモント工場で：Model 3の「生産地獄」の間、マスクは生産ラインで寝て、従業員を「犬より悪い」と呼んで怒鳴ったことがありました（彼は後に謝罪しました）。

幹部の解雇：マスクはPowerPointプレゼンテーションのフォントサイズが十分大きくないという理由で、Teslaの上級幹部をその場で解雇したことがあります。

質問5 — 訂正と補足
AI脅威論：
マスクはAIが人類を破壊する可能性があると信じています（「核兵器より危険」）。したがって：

OpenAI：彼は最初、安全でオープンソースのAIを促進するためにそれを支援しました（しかし後に制御権を巡る争いで離脱）。

Neuralink：彼はブレイン・マシン・インターフェースを使用して人間とAIを融合させることを目指しています — 人間が取り残されることを防ぐためです。

矛盾：
AIリスクについて警告する一方で、マスクは同時にTeslaで完全自動運転（FSD）技術を推進し、人工汎用知能（AGI）を研究するためにxAIを設立しています。

全体的な評価：
✅ あなたは重要な出来事を正確に捉えていますが、詳細を強化する必要があります（タイムラインや具体的な数字など）。
🔍 さらなる学習が推奨される分野：マスクのマルチスレッド管理スタイル（5つの会社を同時に運営）とメディア操作のスキル（Twitterを通じた統治）。
```

## 機能

### EPUBサポート
- メタデータの抽出（タイトル、著者、出版日など）
- 目次の抽出
- 章の内容の抽出（Markdown出力付き）
- EPUBファイルのバッチ処理

### PDFサポート
- メタデータの抽出（タイトル、著者、作成日など）
- 目次の抽出
- ページ番号による内容の抽出
- 章タイトルによる内容の抽出
- Markdown出力サポート
- PDFファイルのバッチ処理

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. `uv`を使用して依存関係をインストール：
```bash
uv pip install -e .
```

## 使用方法

### 開発モードでMCPサーバーを起動

開発モードでサーバーを実行：
```bash
uv run mcp dev src/ebook_mcp/main.py
```

テストとデバッグのために http://localhost:5173/ にアクセスできます
テスト用にインスペクターをインストールすることもできます。
```
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

### 本番モードでMCPサーバーを起動

サーバーを実行：
```bash
uv run src/ebook_mcp/main.py
```

#### CursorでMCPを設定

Cursorに以下の設定を追加
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

### EPUB処理の例

```python
# ディレクトリ内のすべてのEPUBファイルを取得
epub_files = get_all_epub_files("/path/to/books")

# EPUBメタデータを取得
metadata = get_metadata("/path/to/book.epub")

# 目次を取得
toc = get_toc("/path/to/book.epub")

# 特定の章の内容を取得（Markdown形式）
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### PDF処理の例

```python
# ディレクトリ内のすべてのPDFファイルを取得
pdf_files = get_all_pdf_files("/path/to/books")

# PDFメタデータを取得
metadata = get_pdf_metadata("/path/to/book.pdf")

# 目次を取得
toc = get_pdf_toc("/path/to/book.pdf")

# 特定のページの内容を取得
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# 特定の章の内容を取得
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## APIリファレンス

### EPUB APIs

#### `get_all_epub_files(path: str) -> List[str]`
指定されたディレクトリ内のすべてのEPUBファイルを取得。

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
EPUBファイルからメタデータを取得。

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
EPUBファイルから目次を取得。

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
Markdown形式で章の内容を取得。

### PDF APIs

#### `get_all_pdf_files(path: str) -> List[str]`
指定されたディレクトリ内のすべてのPDFファイルを取得。

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
PDFファイルからメタデータを取得。

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
PDFファイルから目次を取得。

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
特定のページからプレーンテキスト内容を取得。

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
特定のページからMarkdown形式の内容を取得。

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
章タイトルによって章の内容と対応するページ番号を取得。

## 依存関係

主要な依存関係には以下が含まれます：
- ebooklib：EPUBファイル処理
- PyPDF2：基本的なPDF処理
- PyMuPDF：高度なPDF処理
- beautifulsoup4：HTML解析
- html2text：HTMLからMarkdownへの変換
- pydantic：データ検証
- fastmcp：MCPサーバーフレームワーク

## 重要な注意事項

1. PDF処理は文書の目次に依存します。目次が利用できない場合、一部の機能が動作しない可能性があります。
2. 大きなPDFファイルの場合、ファイル全体を一度に読み込むことを避けるため、ページ範囲で処理することをお勧めします。
3. EPUB章IDは目次構造から取得する必要があります。

## アーキテクチャ

```
           ┌────────────────────────────┐
           │         エージェント層      │
           │  - 翻訳戦略                │
           │  - スタイル一貫性チェック    │
           │  - LLM呼び出しと相互作用    │
           └────────────▲─────────────┘
                        │ ツール呼び出し
           ┌────────────┴─────────────┐
           │        MCPツール層         │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ システム/IO呼び出し
           ┌────────────┴─────────────┐
           │     システム基盤層         │
           │  - ファイル読み取り        │
           │  - ebooklib解析           │
           │  - ファイルパス保存/チェック│
           └────────────────────────────┘
```

## 貢献

IssuesとPull Requestsを歓迎します！

最近の変更の詳細については、[CHANGELOG.md](CHANGELOG.md)をご覧ください。
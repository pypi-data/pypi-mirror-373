[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/onebirdrocks-ebook-mcp-badge.png)](https://mseep.ai/app/onebirdrocks-ebook-mcp)

# Ebook-MCP

<img src="logo.png" alt="ebook-mcp logo" width="132" height="132">

[English](https://github.com/onebirdrocks/ebook-mcp/blob/main/README.md) | [中文](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-CN.md) | [日本語](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-JP.md) | [한국어](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-KR.md) | [Français](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-FR.md) | [Deutsch](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-DE.md)

Ebook-MCP 是一个强大的模型上下文协议（MCP）服务器，用于处理电子书。基于[模型上下文协议](https://github.com/modelcontextprotocol)构建，它提供了一套标准化的API，用于LLM应用程序与电子书处理功能之间的无缝集成。目前支持EPUB和PDF格式。

## 使用场景与价值

Ebook-MCP 通过与您的阅读材料进行自然语言对话，改变了您与数字图书的互动方式。它与现代AI驱动的IDE（如Cursor和Claude）无缝集成，让您能够：

- **智能图书馆管理**：简单地询问"显示我下载文件夹中的所有EPUB文件"或"在我的图书馆中找到关于GenAI的书籍"
- **互动阅读体验**：与您的书籍进行自然对话：
  - "给我简要介绍一下《LLM工程师手册》"
  - "第3章涵盖了什么内容？"
  - "总结这本书中关于RAG的要点"
- **主动学习支持**：通过AI驱动的互动增强您的学习：
  - "基于第5章的RAG概念创建一个测验"
  - "解释本章讨论的架构之间的差异"
  - "基于本节的概念给我一些实践练习"
- **内容导航**：使用自然语言查询轻松浏览您的书籍：
  - "找到所有讨论提示工程的章节"
  - "显示关于微调的章节"
  - "带我到关于向量数据库的部分"

通过弥合传统电子书与AI功能之间的差距，Ebook-MCP帮助读者通过直观的、基于对话的互动从他们的数字图书馆中提取更多价值。

快速演示 - 使用DeepSeek运行（请查看mcp-client-example文件夹下所有Claude/OpenAI的示例）
```
查询：请检查我下载文件夹中的所有epub书籍。用户ID是onebird。
......

查询：你能问我几个问题来测试我对这本书的理解吗？

回答：当然！这里有5个关于沃尔特·艾萨克森的《埃隆·马斯克》的问题来测试你对这本书的理解。请根据你的知识回答——我会在每个回答后给出反馈和补充细节。

问题1：
马斯克的童年和家庭背景如何塑造了他后来的性格和职业生涯？
（提示：他与父亲的关系，在南非的成长经历等）

问题2：
Zip2和X.com（后来的PayPal）是马斯克早期的创业公司。它们解决了什么问题？马斯克最终是如何退出这些公司的？
（提示：Zip2的商业模式，X.com与Confinity的合并等）

问题3：
2008年，SpaceX和特斯拉都濒临破产。马斯克是如何拯救这两家公司的？
（提示：猎鹰1号的第四次发射，NASA合同，特斯拉的最后一刻救援等）

问题4：
围绕马斯克管理风格的争议有哪些？书中哪些具体事件说明了他的"硬核"或"极端"工作文化？
（提示：弗里蒙特工厂的"生产地狱"，推特裁员等）

问题5：
马斯克对人工智能（AI）的态度是什么？为什么他同时支持OpenAI和Neuralink，这两者似乎有冲突的目标？
（提示：AI作为生存威胁，脑机接口愿景等）

请回答每个问题。我会提供反馈和额外细节或纠正任何误解！
（如果问题不清楚，请随时问我。）

查询：
问题1：他父亲的虐待态度使他对他人缺乏同情心。
问题2：Zip2解决了电子地图和在线黄页的问题。X.com解决了在线支付问题。
问题3：他获得了NASA的合同。特斯拉通过在中国建厂解决了生产问题。
问题4：我不知道。请为我回答。
问题5：他认为开源技术对确保AI安全和开放是必要的。

回答：你的答案抓住了书中的一些要点。让我为问题4和5添加细节、纠正一些不准确之处并提供进一步背景：

问题1 — 纠正与补充
父亲的影响：
马斯克的父亲埃罗尔确实极其严厉——例如，强迫年幼的埃隆跪下数米粒数小时。书中强调这种情感脱敏塑造了马斯克成为一个极其目标导向的人——对他人的痛苦漠不关心，但对自己的目标执着追求。

反向影响：
这并不是说马斯克没有同情心——而是选择性的。例如，他可能冷淡地对待员工，但会亲自研究医疗设备来解决儿子X的健康问题。

问题2 — 纠正与补充
Zip2：
本质上是在线黄页+地图导航服务（帮助报纸上线）。马斯克亲自编写了大部分早期代码并睡在办公室。最终，康柏以3.07亿美元收购了Zip2（马斯克获得2200万美元）。

X.com：
不仅仅是在线支付——这是马斯克试图创建综合金融平台的尝试（旨在取代银行）。后来与Confinity（PayPal的前身）合并。马斯克因内部冲突被驱逐，但当eBay收购PayPal时，马斯克赚了1.8亿美元。
（注：马斯克后来买回了X.com域名——现在是推特母公司的名称）。

问题3 — 纠正与补充
SpaceX：
2008年，猎鹰1号在第四次发射中成功（前三次失败耗尽了资金）。紧接着，SpaceX获得了16亿美元的NASA货物补给合同——这是公司的生命线。

特斯拉：
2008年，特斯拉通过戴姆勒5000万美元的投资和美国能源部的贷款得以生存。
在中国建设超级工厂（2019年）是后来的事。在早期，生存依赖于Model S的推出（2012年）和马斯克的个人赌注——出售所有房地产来资助特斯拉。

问题4 — 解释：围绕他管理风格的争议
"硬核"文化：

在SpaceX/特斯拉：马斯克要求员工每周工作80+小时，甚至睡在工厂。（"如果你不在这里，你的替代者就在。"）

收购推特后：他立即裁员75%的员工，并要求剩余员工签署"硬核承诺"——同意长时间和高强度工作。

极端案例：

在弗里蒙特工厂：在Model 3的"生产地狱"期间，马斯克睡在生产线上，曾对员工大喊称他们"比狗还差"（他后来道歉）。

解雇高管：马斯克曾因为PowerPoint演示文稿的字体大小不够大而当场解雇了一名特斯拉高级主管。

问题5 — 纠正与补充
AI威胁论：
马斯克认为AI可能摧毁人类（"比核武器更危险"）。因此：

OpenAI：他最初支持它以促进安全、开源的AI（但后来因控制权争议而离开）。

Neuralink：他旨在使用脑机接口将人类与AI融合——以防止人类被抛在后面。

矛盾：
在警告AI风险的同时，马斯克同时在特斯拉推进全自动驾驶（FSD）技术，并创立了xAI来研究通用人工智能（AGI）。

总体评价：
✅ 你准确地抓住了关键事件，但细节需要加强（如时间线和具体数字）。
🔍 建议进一步学习的领域：马斯克的多线程管理风格（同时运营五家公司）和他的媒体操控技巧（通过推特治理）。
```

## 功能特性

### EPUB支持
- 提取元数据（标题、作者、出版日期等）
- 提取目录
- 提取章节内容（Markdown输出）
- 批量处理EPUB文件

### PDF支持
- 提取元数据（标题、作者、创建日期等）
- 提取目录
- 按页码提取内容
- 按章节标题提取内容
- Markdown输出支持
- 批量处理PDF文件

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. 使用`uv`安装依赖：
```bash
uv pip install -e .
```

## 使用方法

### 在开发模式下启动MCP服务器

在开发模式下运行服务器：
```bash
uv run mcp dev src/ebook_mcp/main.py
```

您可以访问 http://localhost:5173/ 进行测试和调试
您也可以安装检查器进行测试。
```
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

### 在生产模式下启动MCP服务器

运行服务器：
```bash
uv run src/ebook_mcp/main.py
```

#### 在Cursor中配置MCP

在Cursor中添加以下配置
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

### EPUB处理示例

```python
# 获取目录中的所有EPUB文件
epub_files = get_all_epub_files("/path/to/books")

# 获取EPUB元数据
metadata = get_metadata("/path/to/book.epub")

# 获取目录
toc = get_toc("/path/to/book.epub")

# 获取特定章节内容（Markdown格式）
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### PDF处理示例

```python
# 获取目录中的所有PDF文件
pdf_files = get_all_pdf_files("/path/to/books")

# 获取PDF元数据
metadata = get_pdf_metadata("/path/to/book.pdf")

# 获取目录
toc = get_pdf_toc("/path/to/book.pdf")

# 获取特定页面内容
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# 获取特定章节内容
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## API参考

### EPUB APIs

#### `get_all_epub_files(path: str) -> List[str]`
获取指定目录中的所有EPUB文件。

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
从EPUB文件获取元数据。

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
从EPUB文件获取目录。

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
获取Markdown格式的章节内容。

### PDF APIs

#### `get_all_pdf_files(path: str) -> List[str]`
获取指定目录中的所有PDF文件。

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
从PDF文件获取元数据。

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
从PDF文件获取目录。

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
从特定页面获取纯文本内容。

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
从特定页面获取Markdown格式内容。

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
通过章节标题获取章节内容和对应页码。

## 依赖项

主要依赖包括：
- ebooklib：EPUB文件处理
- PyPDF2：基础PDF处理
- PyMuPDF：高级PDF处理
- beautifulsoup4：HTML解析
- html2text：HTML到Markdown转换
- pydantic：数据验证
- fastmcp：MCP服务器框架

## 重要说明

1. PDF处理依赖于文档的目录。如果没有目录，某些功能可能无法工作。
2. 对于大型PDF文件，建议按页面范围处理，以避免一次加载整个文件。
3. EPUB章节ID必须从目录结构中获取。

## 架构

```
           ┌────────────────────────────┐
           │         代理层             │
           │  - 翻译策略                │
           │  - 风格一致性检查          │
           │  - LLM调用与交互           │
           └────────────▲─────────────┘
                        │ 工具调用
           ┌────────────┴─────────────┐
           │        MCP工具层          │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ 系统/IO调用
           ┌────────────┴─────────────┐
           │     系统基础层            │
           │  - 文件读取              │
           │  - ebooklib解析          │
           │  - 文件路径存储/检查      │
           └────────────────────────────┘
```

## 贡献

我们欢迎Issues和Pull Requests！

有关最近更改的详细信息，请参阅 [CHANGELOG.md](CHANGELOG.md)。
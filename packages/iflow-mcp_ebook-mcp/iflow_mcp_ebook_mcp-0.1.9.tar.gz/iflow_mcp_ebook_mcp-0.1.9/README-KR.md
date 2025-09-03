[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/onebirdrocks-ebook-mcp-badge.png)](https://mseep.ai/app/onebirdrocks-ebook-mcp)

# Ebook-MCP

<img src="logo.png" alt="ebook-mcp logo" width="132" height="132">

[English](https://github.com/onebirdrocks/ebook-mcp/blob/main/README.md) | [中文](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-CN.md) | [日本語](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-JP.md) | [한국어](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-KR.md) | [Français](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-FR.md) | [Deutsch](https://github.com/onebirdrocks/ebook-mcp/blob/main/README-DE.md)

Ebook-MCP는 전자책 처리를 위한 강력한 Model Context Protocol(MCP) 서버입니다. [Model Context Protocol](https://github.com/modelcontextprotocol) 위에 구축되어 LLM 애플리케이션과 전자책 처리 기능 간의 원활한 통합을 위한 표준화된 API 세트를 제공합니다. 현재 EPUB 및 PDF 형식을 지원합니다.

## 사용 사례 및 가치

Ebook-MCP는 독서 자료와의 자연어 대화를 가능하게 하여 디지털 도서와의 상호작용을 변화시킵니다. Cursor 및 Claude와 같은 현대적인 AI 기반 IDE와 원활하게 통합되어 다음을 가능하게 합니다:

- **스마트 라이브러리 관리**: "다운로드 폴더의 모든 EPUB 파일을 보여줘" 또는 "내 라이브러리에서 GenAI에 관한 책을 찾아줘"라고 간단히 물어보세요
- **대화형 독서 경험**: 책에 대해 자연스러운 대화를 나누세요:
  - "'LLM 엔지니어 핸드북'에 대한 간단한 소개를 해줘"
  - "3장에서는 무엇을 다루나요?"
  - "이 책에서 RAG에 대한 핵심 포인트를 요약해줘"
- **능동적 학습 지원**: AI 기반 상호작용을 통해 학습을 향상시키세요:
  - "5장의 RAG 개념을 바탕으로 퀴즈를 만들어줘"
  - "이 장에서 논의된 아키텍처 간의 차이점을 설명해줘"
  - "이 섹션의 개념을 바탕으로 실습 문제를 제공해줘"
- **콘텐츠 내비게이션**: 자연어 쿼리로 책을 쉽게 탐색하세요:
  - "프롬프트 엔지니어링을 논의하는 모든 섹션을 찾아줘"
  - "파인튜닝에 관한 장을 보여줘"
  - "벡터 데이터베이스에 관한 부분으로 안내해줘"

전통적인 전자책과 AI 기능 간의 격차를 해소함으로써, Ebook-MCP는 독자들이 직관적이고 대화 기반의 상호작용을 통해 디지털 라이브러리에서 더 많은 가치를 추출할 수 있도록 도와줍니다.

빠른 데모 - DeepSeek으로 실행 (mcp-client-example 폴더 하위의 Claude/OpenAI 모든 예제를 확인해주세요)
```
쿼리: 내 다운로드 폴더의 모든 epub 책을 확인해주세요. 사용자 ID는 onebird입니다.
......

쿼리: 이 책에 대한 이해도를 테스트하기 위해 몇 가지 질문을 해주실 수 있나요?

답변: 물론입니다! 월터 아이작슨의 『일론 머스크』에 대한 이해도를 테스트하기 위한 5가지 질문이 있습니다. 당신의 지식을 바탕으로 답변해주세요 — 각 답변 후에 피드백과 세부사항을 추가하겠습니다.

질문 1:
머스크의 어린 시절과 가족 배경이 그의 성격과 후의 경력에 어떤 영향을 미쳤나요?
(힌트: 아버지와의 관계, 남아프리카에서의 성장 등)

질문 2:
Zip2와 X.com(후의 PayPal)은 머스크의 초기 스타트업이었습니다. 이들은 어떤 문제를 해결했나요? 머스크는 결국 이 회사들에서 어떻게 퇴출했나요?
(힌트: Zip2의 비즈니스 모델, X.com과 Confinity의 합병 등)

질문 3:
2008년, SpaceX와 Tesla 모두 파산 위기에 처했습니다. 머스크는 이 두 회사를 어떻게 구했나요?
(힌트: Falcon 1의 네 번째 발사, NASA 계약, Tesla의 막판 구조 등)

질문 4:
머스크의 관리 스타일을 둘러싼 논란은 무엇인가요? 책에서 그의 "하드코어" 또는 "극단적인" 업무 문화를 보여주는 구체적인 사건은 무엇인가요?
(힌트: 프리몬트 공장의 "생산 지옥", 트위터 해고 등)

질문 5:
인공지능(AI)에 대한 머스크의 태도는 무엇인가요? 왜 그는 상충하는 목표를 가진 것처럼 보이는 OpenAI와 Neuralink를 동시에 지원했나요?
(힌트: 존재적 위협으로서의 AI, 뇌-기계 인터페이스 비전 등)

각 질문에 답변해주세요. 피드백과 추가 세부사항을 제공하거나 오해가 있다면 수정하겠습니다!
(질문이 명확하지 않다면 언제든 물어보세요.)

쿼리:
질문 1: 아버지의 학대적인 태도로 인해 그는 다른 사람들에 대한 공감이 부족해졌습니다.
질문 2: Zip2는 전자 지도와 온라인 옐로우페이지 문제를 해결했습니다. X.com은 온라인 결제를 해결했습니다.
질문 3: 그는 NASA와 계약을 확보했습니다. Tesla는 중국에 공장을 건설하여 생산 문제를 해결했습니다.
질문 4: 모르겠습니다. 저를 위해 답변해주세요.
질문 5: 그는 AI가 안전하고 개방적이도록 보장하기 위해 오픈소스 기술이 필요하다고 믿습니다.

답변: 당신의 답변은 책의 몇 가지 핵심 포인트를 잘 포착했습니다. 질문 4와 5에 대한 세부사항을 추가하고, 일부 부정확한 부분을 수정하며, 추가 배경을 제공하겠습니다:

질문 1 — 수정 및 보완
아버지의 영향:
머스크의 아버지 에롤은 확실히 극도로 가혹했습니다 — 예를 들어, 어린 일론에게 무릎을 꿇고 몇 시간 동안 쌀알을 세도록 강요했습니다. 책은 이러한 감정적 둔감화가 머스크를 극도로 목표 지향적인 사람으로 만들었다고 강조합니다 — 타인의 고통에는 무관심하지만 자신의 목표에는 강박적으로 헌신합니다.

역방향 영향:
머스크가 공감 능력이 없다는 것이 아니라 — 선택적입니다. 예를 들어, 직원들을 차갑게 대할 수 있지만 아들 X의 건강 문제를 위해 의료 장비를 개인적으로 연구합니다.

질문 2 — 수정 및 보완
Zip2:
본질적으로 온라인 옐로우페이지 + 지도 내비게이션 서비스(신문의 온라인화 지원). 머스크는 초기 코드의 대부분을 직접 작성했고 사무실에서 잠을 잤습니다. 결국 Compaq이 Zip2를 3억 700만 달러에 인수했습니다(머스크는 2200만 달러를 받았습니다).

X.com:
단순한 온라인 결제가 아니라 — 포괄적인 금융 플랫폼을 만들려는 머스크의 시도였습니다(은행을 대체하는 것을 목표로). 나중에 Confinity(PayPal의 전신)와 합병했습니다. 머스크는 내부 갈등으로 축출되었지만, eBay가 PayPal을 인수했을 때 머스크는 1억 8천만 달러를 벌었습니다.
(참고: 머스크는 나중에 X.com 도메인을 다시 구매했습니다 — 현재 트위터의 모회사 이름입니다).

질문 3 — 수정 및 보완
SpaceX:
2008년, Falcon 1은 네 번째 발사에서 성공했습니다(세 번의 실패로 자금이 고갈된 후). 바로 그 후, SpaceX는 화물 보급을 위한 16억 달러의 NASA 계약을 확보했습니다 — 회사의 생명줄이었습니다.

Tesla:
2008년, Tesla는 Daimler의 5천만 달러 투자와 미국 에너지부의 대출을 통해 생존했습니다.
중국에서의 기가팩토리 건설(2019년)은 훨씬 나중의 일입니다. 초기에는 Model S 출시(2012년)와 머스크의 개인적 도박 — Tesla에 자금을 제공하기 위해 모든 부동산을 매각하는 것에 생존이 달려 있었습니다.

질문 4 — 설명: 그의 관리 스타일을 둘러싼 논란
"하드코어" 문화:

SpaceX/Tesla에서: 머스크는 직원들에게 주당 80시간 이상 일하도록 요구했고, 심지어 공장에서 잠을 자기도 했습니다. ("당신이 여기 없다면, 당신의 대체자가 있습니다.")

트위터 인수 후: 그는 즉시 직원의 75%를 해고하고 나머지 직원들에게 "하드코어 약속"에 서명하도록 요구했습니다 — 장시간과 고강도 업무에 동의하는 것입니다.

극단적인 사례:

프리몬트 공장에서: Model 3의 "생산 지옥" 기간 동안, 머스크는 생산 라인에서 잠을 자고 직원들을 "개보다 못하다"고 소리치며 욕했습니다(그는 나중에 사과했습니다).

임원 해고: 머스크는 PowerPoint 프레젠테이션의 글꼴 크기가 충분히 크지 않다는 이유로 Tesla 고위 임원을 즉석에서 해고한 적이 있습니다.

질문 5 — 수정 및 보완
AI 위협론:
머스크는 AI가 인류를 파괴할 수 있다고 믿습니다("핵무기보다 위험"). 따라서:

OpenAI: 그는 처음에 안전하고 오픈소스인 AI를 촉진하기 위해 지원했습니다(하지만 나중에 통제권 분쟁으로 떠났습니다).

Neuralink: 그는 뇌-기계 인터페이스를 사용하여 인간과 AI를 융합시키는 것을 목표로 합니다 — 인간이 뒤처지는 것을 방지하기 위해서입니다.

모순:
AI 위험에 대해 경고하면서도, 머스크는 동시에 Tesla에서 완전 자율주행(FSD) 기술을 추진하고 있으며 인공일반지능(AGI)을 연구하기 위해 xAI를 설립했습니다.

전체 평가:
✅ 당신은 주요 사건들을 정확하게 포착했지만, 세부사항을 강화할 필요가 있습니다(타임라인과 구체적인 수치 등).
🔍 추가 학습이 권장되는 영역: 머스크의 멀티스레드 관리 스타일(5개 회사를 동시에 운영)과 미디어 조작 기술(트위터를 통한 통치).
```

## 기능

### EPUB 지원
- 메타데이터 추출 (제목, 저자, 출판일 등)
- 목차 추출
- 장 내용 추출 (Markdown 출력 포함)
- EPUB 파일 일괄 처리

### PDF 지원
- 메타데이터 추출 (제목, 저자, 생성일 등)
- 목차 추출
- 페이지 번호별 내용 추출
- 장 제목별 내용 추출
- Markdown 출력 지원
- PDF 파일 일괄 처리

## 설치

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. `uv`를 사용하여 종속성 설치:
```bash
uv pip install -e .
```

## 사용법

### 개발 모드에서 MCP 서버 시작

개발 모드에서 서버 실행:
```bash
uv run mcp dev src/ebook_mcp/main.py
```

테스트 및 디버깅을 위해 http://localhost:5173/ 을 방문할 수 있습니다
테스트를 위해 인스펙터를 설치할 수도 있습니다.
```
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

### 프로덕션 모드에서 MCP 서버 시작

서버 실행:
```bash
uv run src/ebook_mcp/main.py
```

#### Cursor에서 MCP 구성

Cursor에 다음 구성 추가
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

### EPUB 처리 예제

```python
# 디렉토리의 모든 EPUB 파일 가져오기
epub_files = get_all_epub_files("/path/to/books")

# EPUB 메타데이터 가져오기
metadata = get_metadata("/path/to/book.epub")

# 목차 가져오기
toc = get_toc("/path/to/book.epub")

# 특정 장 내용 가져오기 (Markdown 형식)
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### PDF 처리 예제

```python
# 디렉토리의 모든 PDF 파일 가져오기
pdf_files = get_all_pdf_files("/path/to/books")

# PDF 메타데이터 가져오기
metadata = get_pdf_metadata("/path/to/book.pdf")

# 목차 가져오기
toc = get_pdf_toc("/path/to/book.pdf")

# 특정 페이지 내용 가져오기
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# 특정 장 내용 가져오기
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## API 참조

### EPUB APIs

#### `get_all_epub_files(path: str) -> List[str]`
지정된 디렉토리의 모든 EPUB 파일을 가져옵니다.

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
EPUB 파일에서 메타데이터를 가져옵니다.

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
EPUB 파일에서 목차를 가져옵니다.

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
Markdown 형식으로 장 내용을 가져옵니다.

### PDF APIs

#### `get_all_pdf_files(path: str) -> List[str]`
지정된 디렉토리의 모든 PDF 파일을 가져옵니다.

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
PDF 파일에서 메타데이터를 가져옵니다.

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
PDF 파일에서 목차를 가져옵니다.

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
특정 페이지에서 일반 텍스트 내용을 가져옵니다.

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
특정 페이지에서 Markdown 형식 내용을 가져옵니다.

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
장 제목으로 장 내용과 해당 페이지 번호를 가져옵니다.

## 종속성

주요 종속성은 다음과 같습니다:
- ebooklib: EPUB 파일 처리
- PyPDF2: 기본 PDF 처리
- PyMuPDF: 고급 PDF 처리
- beautifulsoup4: HTML 파싱
- html2text: HTML에서 Markdown으로 변환
- pydantic: 데이터 검증
- fastmcp: MCP 서버 프레임워크

## 중요 사항

1. PDF 처리는 문서의 목차에 의존합니다. 목차를 사용할 수 없는 경우 일부 기능이 작동하지 않을 수 있습니다.
2. 큰 PDF 파일의 경우 전체 파일을 한 번에 로드하는 것을 피하기 위해 페이지 범위별로 처리하는 것이 좋습니다.
3. EPUB 장 ID는 목차 구조에서 가져와야 합니다.

## 아키텍처

```
           ┌────────────────────────────┐
           │         에이전트 레이어     │
           │  - 번역 전략               │
           │  - 스타일 일관성 검사       │
           │  - LLM 호출 및 상호작용     │
           └────────────▲─────────────┘
                        │ 도구 호출
           ┌────────────┴─────────────┐
           │        MCP 도구 레이어    │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ 시스템/IO 호출
           ┌────────────┴─────────────┐
           │     시스템 기반 레이어    │
           │  - 파일 읽기              │
           │  - ebooklib 파싱          │
           │  - 파일 경로 저장/검사     │
           └────────────────────────────┘
```

## 기여

Issues와 Pull Requests를 환영합니다!

최근 변경사항에 대한 자세한 정보는 [CHANGELOG.md](CHANGELOG.md)를 참조하세요.
# MarkdownFlow Agent (Python)

MarkdownFlow Agent is a library designed to transform MarkdownFlow document into personalized content.

MarkdownFlow (also known as MDFlow) extends standard Markdown with AI-powered intelligence to create personalized, interactive pages. The tagline: **"Write Once, Deliver Personally"**.

Learn more about MarkdownFlow at [markdownflow.ai](https://markdownflow.ai).

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Pip

### Installation

#### Install from PyPI

```bash
pip install markdown-flow
```

#### Local Development Installation

```bash
cd markdown-flow
pip install -e .
```

## Usage

```python
from markdown_flow import MarkdownFlow, ProcessMode

# Create interactive Markdown document
document = """
Ask {{name}} about his/her Python experience level.

?[%{{level}} Beginner | Intermediate | Expert]

The user's Python experience level is {{level}}. Give some suggestions about the learning path.
"""

# Initialize and process
mf = MarkdownFlow(document, llm_provider=your_llm)
result = await mf.process(0, variables={'name': 'User'})
```

## 🔗 Related Links

- **PyPI Package**: <https://pypi.org/project/markdownflow/>
- **GitHub Repository**: <https://github.com/ai-shifu/markdown-flow-agent-py>

---

*Built with ❤️ by AI Shifu Team*

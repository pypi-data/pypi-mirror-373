# ![Parmot Logo](https://parmot-frontend.vercel.app/_next/image?url=%2Flogo.png&w=128&q=75)

**Parmot Python SDK**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Parmot is a lightweight package tracking and managing **end-user usage, limits, and subscription plans** across AI providers (OpenAI, Anthropic, Cohere, etc.).

Visit [parmot.com](https://www.parmot.com/) for more.

---

## 🚀 Features

- Track **token usage and costs** across multiple providers.
- Enforce **rate limits** and **usage limits** for end-users.
- Manage **subscription plans** (create, update, delete, assign).
- Easy-to-use wrappers for OpenAI, Anthropic, and Cohere clients with automatic tracking.

---

## 📦 Installation

```bash
pip install parmot[openai]
```

To install Parmot for other provider clients, simply include them in the brackets:

```bash
pip install parmot[anthropic]
pip install parmot[cohere]
```

---

## ⚡ Quick Start

```python
from parmot import TrackedOpenAI

client = TrackedOpenAI(api_key="OPENAI_API_KEY", parmot_api_key="PARMOT_API_KEY")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    user_id="end_user_123",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)

print(response.choices[0].message)
```

---

## 📖 Docs

👉 [Full Documentation](https://www.parmot.com/docs)

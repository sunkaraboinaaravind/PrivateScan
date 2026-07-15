# 🔒 PrivateScan

**Your documents, your AI, your privacy. Zero cloud dependency.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OSDHack 2026](https://img.shields.io/badge/OSDHack-2026-orange)](https://unstop.com)
[![On-Device AI](https://img.shields.io/badge/AI-On--Device-purple)]()

---

## 🚀 What is PrivateScan?

**PrivateScan** is an offline-first desktop application that lets you **drag & drop any file** — PDFs, images, Word documents, CSVs, text files, code — and get instant **AI-powered analysis**, all running **100% locally on your machine**.

> **No cloud. No APIs. No data leaving your device. Ever.**

Built with **Ollama** for local LLM inference, PrivateScan brings the power of AI document analysis to your desktop without compromising privacy.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-Format Support** | PDF, Images (JPG/PNG/BMP), DOCX, TXT, Markdown, CSV, Code files |
| 🔍 **PII Detection** | Automatically detect emails, phone numbers, SSNs, credit cards, addresses |
| 📝 **Smart Summarization** | Get concise AI-generated summaries of any document |
| 🔑 **Key Info Extraction** | Extract names, dates, amounts, organizations automatically |
| 💬 **Local Q&A Chat** | Ask questions about your documents — answered by local AI |
| 🖼️ **Image Analysis** | OCR text extraction + AI-powered image description |
| 🌙 **Dark Mode UI** | Modern, sleek dark-themed interface |
| 🔒 **100% Offline** | All AI inference runs locally via Ollama |

---

## 🧠 On-Device AI

PrivateScan uses **Ollama** to run large language models entirely on your machine:

- **Text Analysis**: Llama 3.2 (3B), Mistral 7B, Phi-3 Mini, or any Ollama-compatible model
- **Image Understanding**: LLaVA for vision-based image analysis
- **OCR**: Tesseract for text extraction from images

**No internet required** for core AI features. Your documents never leave your device.

### Architecture

```
┌─────────────────────────────────────────────┐
│              PrivateScan UI (Tkinter)        │
├─────────────────────────────────────────────┤
│           File Processor Engine              │
│  ┌───────┬───────┬──────┬──────┬──────────┐ │
│  │  PDF  │ Image │ DOCX │ CSV  │ TXT/Code │ │
│  └───┬───┴───┬───┴──┬───┴──┬───┴────┬─────┘ │
│      └───────┴──────┴──────┴────────┘        │
│                    │                         │
│           ┌───────▼────────┐                 │
│           │  AI Analyzer   │                 │
│           │  (Ollama LLM)  │                 │
│           └───────┬────────┘                 │
│                   │                          │
│        ┌──────────┼──────────┐               │
│        ▼          ▼          ▼               │
│   Summarize   PII Detect   Q&A Chat         │
└─────────────────────────────────────────────┘
         ▲
         │  100% Local
         ▼
   ┌──────────┐
   │  Ollama   │  (Local LLM Server)
   │  Server   │
   └──────────┘
```

---

## 📸 Screenshots

<!-- Screenshots will be added here -->
*Screenshots coming soon — see Demo Video below*

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **UI Framework** | Tkinter (built-in) |
| **Local LLM** | Ollama |
| **PDF Parsing** | PyMuPDF (fitz) |
| **Image Processing** | Pillow |
| **OCR** | Tesseract (pytesseract) |
| **Word Documents** | python-docx |
| **CSV/Excel** | pandas, openpyxl |
| **Theme** | Custom dark theme |

---

## ⚡ Quick Start

### Prerequisites

1. **Install Ollama** — [https://ollama.com/download](https://ollama.com/download)
2. **Pull a model**:
   ```bash
   ollama pull llama3.2
   ```
3. **Install Tesseract OCR** (optional, for image text extraction):
   - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PrivateScan.git
cd PrivateScan

# Install dependencies
pip install -r requirements.txt

# Start Ollama (if not running)
ollama serve

# Launch PrivateScan
python main.py
```

---

## 📖 Usage

1. **Launch** the app with `python main.py`
2. **Drop a file** onto the drop zone or click **Browse** to select a file
3. **View extracted text** in the left panel
4. **Choose an action**:
   - 📝 **Summarize** — Get an AI summary
   - 🔍 **Detect PII** — Find sensitive information
   - 🔑 **Extract Info** — Pull out key details
   - 💬 **Ask a Question** — Chat with your document
5. **Results appear** in the right panel — all processed locally!

### Supported File Types

| Extension | Type | Processing |
|-----------|------|-----------|
| `.pdf` | PDF Documents | Text extraction via PyMuPDF |
| `.jpg`, `.png`, `.bmp`, `.gif`, `.webp` | Images | OCR + AI Vision |
| `.docx` | Word Documents | python-docx parsing |
| `.txt`, `.md` | Text/Markdown | Direct reading |
| `.csv` | CSV Data | pandas parsing |
| `.py`, `.js`, `.java`, `.cpp`, `.rs`, `.go`, `.html`, `.css` | Code | Syntax-aware reading |

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🏆 Built for OSDHack 2026

This project was built for **OSDHack 2026** by [Open Source Developers Community (OSDC)](https://discord.gg/qNcWcJXyd).

**Theme**: On-Device AI — *Build AI that runs closer to the user, faster, lighter, more private, and open source.*

---

<p align="center">
  <b>🔒 PrivateScan — Because your documents deserve privacy.</b><br>
  <i>Made with ❤️ for OSDHack 2026</i>
</p>

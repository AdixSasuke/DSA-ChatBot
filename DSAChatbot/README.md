# DSA Chatbot

## Introduction

A conversational AI assistant trained on Data Structures and Algorithms concepts, providing instant answers from your custom documents.

## Features

-   **Custom Knowledge Base**: Train with your DSA books and resources.
-   **Interactive UI**: Built with Chainlit.
-   **Vector Search**: Uses FAISS for semantic search.
-   **Local LLM**: Powered by Ollama.
-   **OCR Capability**: Process DSA problems or code from images.
-   **Memory System**: Maintains conversation context.
-   **Performance Metrics**: Shows query processing time.
-   **Easy Updates**: Add new materials easily.

## Setup

### Requirements

-   Python 3.8+
-   Ollama installed and running
-   Tesseract OCR installed
-   Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Installation

1. Clone repository:
    ```bash
    git clone https://github.com/AdixSasuke/DSA-ChatBot
    cd DSAChatbot
    ```
2. Install Ollama and pull a model:
    ```bash
    ollama pull llama3.2
    ```
3. Install Tesseract OCR:
    - [Windows download](https://github.com/UB-Mannheim/tesseract/wiki)
    - macOS: `brew install tesseract`
    - Linux: `apt-get install tesseract-ocr`
4. Update paths in `ingest.py` and `chatbot.py` if needed.

## Usage

### Add Documents

1. Place PDFs in the `sourcedata` folder.
2. Build vector database:
    ```bash
    python ingest.py
    ```

### Run Chatbot

1. Start Ollama:
    ```bash
    ollama serve
    ```
2. Launch chatbot:
    ```bash
    chainlit run chatbot.py
    ```

### Using OCR

-   Upload or drag-and-drop DSA images.
-   The bot extracts and answers based on the image.

## Updating

-   Add or remove PDFs in `sourcedata/`.
-   Rebuild database:
    ```bash
    python ingest.py
    ```
-   Restart chatbot.

## Customization

-   Adjust chunk size and overlap in `ingest.py`.
-   Change embedding model in `ingest.py`.
-   Change LLM model in `chatbot.py`.
-   Adjust OCR settings in `chatbot.py`.
-   Edit UI by modifying `chainlit.md`.

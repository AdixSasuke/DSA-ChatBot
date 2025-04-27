# DSA Chatbot

## Introduction

A conversational AI assistant trained on Data Structures and Algorithms concepts. This chatbot provides instant answers to DSA questions using the knowledge from your custom documents.

## Features

-   **Custom Knowledge Base**: Train on your own DSA books and resources
-   **Interactive UI**: Built with Chainlit for a smooth chat experience
-   **Vector Search**: Uses FAISS for efficient semantic search of concepts
-   **Ollama Integration**: Powered by Ollama for fast, local LLM inference
-   **OCR Capability**: Process images containing DSA problems or code snippets
-   **Memory System**: Maintains conversation context for natural follow-up questions
-   **Performance Metrics**: Shows query processing time in the interface
-   **Easy to Update**: Simple process to update with new books or materials

## Setup

### Requirements

1. Python 3.8 or higher
2. Required packages (install using requirements.txt)
3. Ollama installed and running on your system
4. Tesseract OCR installed on your system (for image processing)

### Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/AdixSasuke/DSA-ChatBot
    cd DSAChatbot
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Install Ollama:

    - Follow instructions at [ollama.ai](https://ollama.ai/) to install on your platform
    - Pull the llama3 model (or your preferred model):
        ```bash
        ollama pull llama3.2
        ```

4. Install Tesseract OCR:

    - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
    - macOS: `brew install tesseract`
    - Linux: `apt-get install tesseract-ocr`
    - Update the tesseract path in `chatbot.py` if needed

5. Configure paths in `ingest.py` (if needed):
    - `DATA_PATH`: Directory where your PDF documents are stored (default: 'sourcedata/')
    - `DB_FAISS_PATH`: Directory for the vector database (default: 'vectorstore/db_faiss')

## Usage

### Adding Documents to Knowledge Base

1. Place your PDF files in the `sourcedata` directory:

    - Remove any existing PDFs you don't want in your knowledge base
    - Add your new DSA books/materials (PDF format only)

2. Build the vector database:
    ```bash
    python ingest.py
    ```

### Running the Chatbot

1. Make sure Ollama service is running:

    ```bash
    ollama serve
    ```

2. Launch the chatbot with:
    ```bash
    chainlit run chatbot.py
    ```

### Using the OCR Feature

To use the OCR capability:

1. Take a screenshot or photo of DSA code, problems, or diagrams
2. Upload the image during your chat session or drag-and-drop into the chat interface
3. The chatbot will extract text from the image and respond to the content
4. You can also include a text question along with your image for more specific responses

## Updating with New Books

To update the chatbot with new content:

1. Remove unwanted files from the `sourcedata` folder
2. Add new PDF books to the `sourcedata` folder
3. Run `python ingest.py` to rebuild the database
4. Restart the chatbot

## Customization

-   Adjust chunk size and overlap in `ingest.py` to optimize how documents are processed
-   Modify the embedding model in `ingest.py` for different performance characteristics
-   Change the LLM model in `chatbot.py` by updating the `model_name` parameter in the `get_ollama_response` function
-   Customize the UI by editing `chainlit.md`
-   Adjust OCR preprocessing parameters in `chatbot.py` for different image types

## License

This project is licensed under the [MIT License](License).

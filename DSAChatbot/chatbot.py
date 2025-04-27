from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import ollama
import chainlit as cl
import time
import pytesseract
import cv2
import asyncio

# Configure pytesseract path for Windows (you may need to update this path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DB_FAISS_PATH = 'vectorstore/db_faiss'

# Load embeddings and vector database
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

SYSTEM_PROMPT = """You are a helpful assistant specializing in Data Structures and Algorithms (DSA).

Instructions:
- Provide only a helpful and accurate answer.
- If the question is unrelated to DSA, respond with: "I can only answer questions related to Data Structures and Algorithms. Please ask a relevant question."
- If the provided context does not contain the answer, use your own DSA knowledge to respond.
- If you genuinely don't know the answer, reply with: "I don't know."
- Maintain conversation continuity by referring to previous exchanges when appropriate.
- Keep responses focused and precise.
- If the user provides an image with text, process the text content and respond accordingly.
"""

# OCR function to extract text from images
def process_image(image_path):
    try:
        # Read the image from its path (image_path is a string now)
        img = cv2.imread(image_path)
        
        if img is None:
            print(f"Failed to load image from path: {image_path}")
            return "Error: Could not load the image. The file may be corrupt or in an unsupported format."
        
        # Preprocess the image to improve OCR accuracy
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform OCR on the processed image
        extracted_text = pytesseract.image_to_string(thresh)
        
        # Return the extracted text
        return extracted_text.strip() if extracted_text.strip() else "No text detected in the image."
    except Exception as e:
        print(f"Error processing image: {e}")
        return f"Error extracting text from the image: {str(e)}. Please try a clearer image."

@cl.on_chat_start
async def start():
    # Initialize chat messages for this session with system prompt
    cl.user_session.set("messages", [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    
    msg = cl.Message(content="Starting the DSA Chatbot...")
    await msg.send()
    msg.content = "Hi, Welcome to Data Structures and Algorithms Bot. What is your query? You can also upload an image containing DSA problems or code."
    await msg.update()

@cl.on_message
async def main(message: cl.Message):
    # Start timing
    start_time = time.time()
    
    query = message.content
    image_text = ""
    
    # Process any attached images using OCR
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.Image):
                # Extract text from the image
                image_text = process_image(element.path)
                
                # Add notification that image is being processed
                await cl.Message(content=f"Processing image... Extracted text:\n```\n{image_text}\n```").send()
                
                # Combine image text with user query if there is any
                if query:
                    query = f"{query}\n\nText from image:\n{image_text}"
                else:
                    query = f"Process the following text from an image:\n{image_text}"
    
    # If no valid query, inform the user
    if not query and not image_text:
        await cl.Message(content="Please provide a question or upload an image with text content.").send()
        return
    
    # Retrieve messages from session
    messages = cl.user_session.get("messages")
    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Create a thinking step with dynamic name updating
    step = cl.Step(name="Thinking...", type="thinking")
    await step.send()
    
    try:
        # Update thinking step periodically to show elapsed time
        async def update_step_time():
            elapsed = 0
            while True:
                elapsed = time.time() - start_time
                step.name = f"Thinking... ({elapsed:.2f}s)"
                await step.update()
                if elapsed > 60:  # Don't update too frequently after a minute
                    await asyncio.sleep(5)
                elif elapsed > 30:  # Update every 2 seconds after 30 seconds
                    await asyncio.sleep(2)
                elif elapsed > 10:  # Update every second after 10 seconds
                    await asyncio.sleep(1)
                else:  # Update every 0.5 seconds at the start
                    await asyncio.sleep(0.5)
        
        # Start the timer update task
        timer_task = asyncio.create_task(update_step_time())
        
        # Get relevant documents from FAISS
        docs = db.similarity_search(query, k=2)
        
        # Format context from documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Add context to the user query
        enhanced_query = f"Based on this context: {context}\n\nMy question is: {query}"
        
        # Add the enhanced user message to history
        messages.append({"role": "user", "content": enhanced_query})
        
        # Get response from Ollama with full message history
        response = ollama.chat(
            model="llama3.2:latest", 
            messages=messages
        )
        
        assistant_message = response['message']
        response_text = assistant_message['content']
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": response_text})
        
        # Limit history to last 10 exchanges (plus system prompt) to avoid context overflow
        if len(messages) > 21:  # system prompt + 10 exchanges (20 messages)
            messages = [messages[0]] + messages[-20:]
        
        # Update session history
        cl.user_session.set("messages", messages)
        
        # Cancel the timer update task
        timer_task.cancel()
        
        # Set final elapsed time
        elapsed_time = time.time() - start_time
        step.name = f"Thinking... ({elapsed_time:.2f}s)"
        await step.update()
        
        # End the step
        await step.end()
        
        # Send response
        await cl.Message(content=response_text).send()
        
    except Exception as e:
        # Cancel timer task if it exists
        if 'timer_task' in locals():
            timer_task.cancel()
        
        error_msg = f"An error occurred while processing your request: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()
        
        # End the step with error status
        if 'step' in locals():
            step.name = f"Error after ({time.time() - start_time:.2f}s)"
            await step.update()
            await step.end()

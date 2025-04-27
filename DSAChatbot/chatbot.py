from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import ollama
import chainlit as cl

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
"""

@cl.on_chat_start
async def start():
    # Initialize chat messages for this session with system prompt
    cl.user_session.set("messages", [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    
    msg = cl.Message(content="Starting the DSA Chatbot...")
    await msg.send()
    msg.content = "Hi, Welcome to Data Structures and Algorithms Bot. What is your query?"
    await msg.update()

@cl.on_message
async def main(message: cl.Message):
    query = message.content
    
    # Retrieve messages from session
    messages = cl.user_session.get("messages")
    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Show typing indicator
    async with cl.Step(name="Thinking...") as step:
        step.stream = True
        await step.update()
        
        try:
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
            
            # Send response
            await cl.Message(content=response_text).send()
            
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {str(e)}"
            print(error_msg)
            await cl.Message(content=error_msg).send()

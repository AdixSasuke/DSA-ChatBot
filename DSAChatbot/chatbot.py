from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import ollama
import json
import chainlit as cl
import asyncio

DB_FAISS_PATH = 'vectorstore/db_faiss'

custom_prompt_template = """
You are a helpful assistant specializing in Data Structures and Algorithms (DSA).

Context:
{context}

Question:
{question}

Instructions:
- Provide only a helpful and accurate answer.
- If the question is unrelated to DSA, respond with: "I can only answer questions related to Data Structures and Algorithms. Please ask a relevant question."
- If the context does not contain the answer, use your own DSA knowledge to respond.
- If you genuinely don't know the answer, reply with: "I don't know."

Helpful Answer:
"""


def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])
    return prompt

# Use Ollama instead of CTransformers
def get_ollama_response(prompt, model_name="llama3.2:latest"):
    try:
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Error with Ollama: {e}")
        return "I encountered an error processing your request."

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
qa_prompt = set_custom_prompt()

# Modified retrieval and generation function
def answer_query(query):
    try:
        # Get relevant documents from FAISS
        docs = db.similarity_search(query, k=2)
        
        # Format context from documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Format the prompt with context and question
        formatted_prompt = qa_prompt.format(context=context, question=query)
        
        # Get response from Ollama
        response = get_ollama_response(formatted_prompt)
        return response
    except Exception as e:
        print(f"Error in answer_query: {e}")
        return "I encountered an error while processing your query."

@cl.on_chat_start
async def start():
    try:
        msg = cl.Message(content="Starting the bot...")
        await msg.send()
        msg.content = "Hi, Welcome to Data Structures and Algorithms Bot. What is your query?"
        await msg.update()
    except Exception as e:
        print(f"Error during chat start: {e}")

@cl.on_message
async def main(message: cl.Message):
    query = message.content
    
    # Show typing indicator
    async with cl.Step(name="Thinking...") as step:
        step.stream = True
        await step.update()
        
        try:
            # Get answer from Ollama with relevant context
            response = answer_query(query)
            
            # Create response message
            response_message = cl.Message(content=response)
            await response_message.send()
            
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {str(e)}"
            print(error_msg)
            await cl.Message(content=error_msg).send()

from langchain_ollama import OllamaLLM
from rag import searcher
from sql_agent import retrieve
from langchain.schema import HumanMessage, AIMessage
import os
llm = OllamaLLM(model="llama3")
def get_run_number(directory: str, prefix: str) -> int: 
    files = [f for f in os.listdir(directory) if f.startswith(prefix)] 
    if not files: 
        return 1 
    run_numbers = [int(f.split('_')[-1].split('.')[0]) for f in files] 
    return max(run_numbers) + 1

def answer(user_query: str, chat_history: list):
    retrieve1 = searcher(user_query)  
    retrieve2 = retrieve(user_query)  

    retrieve1_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve1)])
    retrieve2_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve2)])

    history_str = "\n".join([f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}" for message in chat_history])

    system_prompt = f"""
    You are an intelligent agent tasked with providing helpful responses based on the information provided. If you 
    find the information not useful for the question then ignore it
    Given the retrieved data, the user's query, and the chat history, provide an accurate and relevant response.

    Retrieved Information (from wikipedia):
    {retrieve1_text}

    Retrieved Information (from database):
    {retrieve2_text}

    Chat History:
    {history_str}

    User's Query:
    {user_query}
    """

    message = [HumanMessage(content=system_prompt)]

    ai_response = llm.invoke(message)

    directory="static"
    run_number=get_run_number(directory,"response")
    os.makedirs(directory, exist_ok=True)
    # # Save the retrieved information to files
    # with open(os.path.join(directory, f"retrieve1_{run_number}.txt"), "w", encoding="utf-8") as f: 
    #     f.write(retrieve1_text) 
    # with open(os.path.join(directory, f"retrieve2_{run_number}.txt"), "w", encoding="utf-8") as f: 
    #     f.write(retrieve2_text)
    # Save the AI response to a file 
    with open(os.path.join(directory, f"response_{run_number}.txt"), "w", encoding="utf-8") as f: 
        f.write(ai_response)
    # Save the user query to a file 
    with open(os.path.join(directory, f"user_query_{run_number}.txt"), "w", encoding="utf-8") as f: 
        f.write(user_query)
    return ai_response


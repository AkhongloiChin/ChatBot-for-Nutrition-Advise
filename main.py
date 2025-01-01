import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from router import rl
from question_agent import answer
from small_talk_agent import small_talker
from user_data_tool import init_user_db, view_diet, search_nutrition, insert_user_data
from query_agent import extract_food_with_llm
from unitconverter import convert_to_grams
from cross_encoder import reranking
import sqlite3

init_user_db()

# Initialize chat history in session state if not already done
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def router(query: str, chat_history: list):
    print(">Router")
    route = rl(query)
    
    if route.name == 'small_talk':
        print("small talking")
        response = small_talker(query, chat_history)
    
    elif route.name == 'diet_tracker':
        print("diet tracking")
        parse_results = extract_food_with_llm(query, chat_history)  # Parse results: [{'food': 'apples', 'amount': '100 grams'}]
        print(f"Parse results: {parse_results}")
        g_parse_results = convert_to_grams(parse_results)  # Parse results with right unit: [{'food': 'apples', 'amount': 100.0}]
        print(f"Parse results with right unit: {g_parse_results}")
        for result in g_parse_results:
            food_data = search_nutrition(result.get('food'))
            if len(food_data) == 0:
                return "Sorry I couldn't find your food in our database"
            elif len(food_data) == 1:
                insert_user_data(food_data, result['amount'])
            else:
                ori_name = result.get('food')
                food_names = [entry[0] for entry in food_data]  
                final = reranking(ori_name, food_names)
                #print("ori_names:", ori_name)
                #print("food_names:", food_names)
                #print("final:", final, "type:", type(final))
                #print("food_data:", food_data, "type:", type(food_data))
                for food in food_data:
                    if food[0] == final:
                        fin = food
                        print("found it")
                        break
                insert_user_data(fin, result['amount'])
        response = "Saving complete"
        data = view_diet()
        if data:
            st.write("Here is the list of diet reports:")
            st.dataframe(data)
        else:
            st.write("No data available or error in fetching data.")
    
    elif route.name == 'nutrition_advisor':
        response = answer(query, chat_history)
    
    else:
        response = "Sorry, I couldn't answer your request"
    
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response))
    
    return response

# Function to delete the user_reports table
def delete_user_table():
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    
    # SQL command to delete the user_reports table
    cursor.execute("DROP TABLE IF EXISTS user_reports")
    
    conn.commit()
    conn.close()
    st.write("user_reports table deleted successfully.")

st.title("Nutrition Advisor Chatbot")

# Input field for user queries
user_input = st.text_input("Ask me anything about nutrition:")

# Buttons to clear chat and delete user table
clear_chat = st.button("Clear Chat")
delete_table = st.button("Delete User Data Table")

# Clear chat functionality
if clear_chat:
    st.session_state.chat_history.clear()

# Delete user table functionality
if delete_table:
    delete_user_table()

# Process user input
if user_input and not (clear_chat or delete_table):
    response = router(user_input, st.session_state.chat_history)
    
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.chat_history.append(AIMessage(content=response))

# Display response if there is any
if st.session_state.chat_history:
    response = st.session_state.chat_history[-1]
    if isinstance(response, AIMessage):
        st.markdown(f"**Bot:** {response.content}")

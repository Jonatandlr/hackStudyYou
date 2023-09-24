import pickle
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth
from io import StringIO
import pdfplumber
import os
from softtek_llm.chatbot import Chatbot
from softtek_llm.models import OpenAI
from softtek_llm.cache import Cache
from softtek_llm.vectorStores import PineconeVectorStore
from softtek_llm.embeddings import OpenAIEmbeddings
from softtek_llm.schemas import Filter
from dotenv import load_dotenv
import PyPDF2
from docx import Document

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env file")

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
if OPENAI_API_BASE is None:
    raise ValueError("OPENAI_API_BASE not found in .env file")

OPENAI_EMBEDDINGS_MODEL_NAME = os.getenv("OPENAI_EMBEDDINGS_MODEL_NAME")
if OPENAI_EMBEDDINGS_MODEL_NAME is None:
    raise ValueError("OPENAI_EMBEDDINGS_MODEL_NAME not found in .env file")

OPENAI_CHAT_MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL_NAME")
if OPENAI_CHAT_MODEL_NAME is None:
    raise ValueError("OPENAI_CHAT_MODEL_NAME not found in .env file")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY not found in .env file")

PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
if PINECONE_ENVIRONMENT is None:
    raise ValueError("PINECONE_ENVIRONMENT not found in .env file")

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
if PINECONE_INDEX_NAME is None:
    raise ValueError("PINECONE_INDEX_NAME not found in .env file")


vector_store = PineconeVectorStore(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENVIRONMENT,
    index_name=PINECONE_INDEX_NAME,
)
embeddings_model = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model_name=OPENAI_EMBEDDINGS_MODEL_NAME,
    api_type="azure",
    api_base=OPENAI_API_BASE,
)
cache = Cache(
    vector_store=vector_store,
    embeddings_model=embeddings_model,
)
model = OpenAI(
    api_key=OPENAI_API_KEY,
    model_name=OPENAI_CHAT_MODEL_NAME,
    api_type="azure",
    api_base=OPENAI_API_BASE,
    verbose=True,
)
filters = [
    Filter(
        type="DENY",
        case="talk about something else not related to my note"
    )
]
chatbot = Chatbot(
     model=model,
    description="you are my assistant who reads my class notes and you get information only from my notes. ",
    cache=cache,
    verbose=True,
)

def procesar_variable(variable_recibida):
    max_intentos = 5
    intentos = 0
    response = None


    while intentos < max_intentos:
        try:
       
            response = chatbot.chat(
                prompt=variable_recibida,
                print_cache_score=True,
                cache_kwargs={"namespace": "chatbot-test"},
            )
            return(response.message.content)
            break  # Si la respuesta es exitosa, salimos del bucle
        except Exception as e:
            print(f"Error al hacer la solicitud a la API: {e}")
            intentos += 1
            if intentos < max_intentos:
                print(f"Reintentando (intentos restantes: {max_intentos - intentos})")
            else:
                return("Se alcanzó el número máximo de intentos, no se pudo obtener respuesta.")

text = ''
#--- User Authentitactor -------
col2, col4 = st.columns([1,3])
with col4:
    st.title('Study...By Yourself ✏️')
names = ["Daniel", "Jonny"]
usernames = ["JDaniel", "Djon"]


file_path = Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords=pickle.load(file)

authenticator=stauth.Authenticate(names, usernames, hashed_passwords, "Hack2023", "abc", cookie_expiry_days=0)

name, authenticator_status, username = authenticator.login("Login", "main")

if authenticator_status == False:
    st.warning("Username/password is incorrect")
if authenticator_status == None:
    st.warning("Please enter your username and password")
#-----------------------InputFile----------------------------------
#col2, col4 = st.columns([1,0.1])
#with col4:
if authenticator_status == True:
    with st.sidebar:
        st.subheader("New Note..................+")
        st.divider()
        st.title("Libretas 📓")
        st.button("Control")
        st.button("Power Units")
        st.button("Quick Prototyping")
        st.button("Mexican History")
        st.button("Project Managment")
        st.button("German")
        st.button("Circuits 101")
        st.button("Circuits Lab")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            #text = ''
            for page in pdf.pages:
             text += page.extract_text()
             procesar_variable(f"lee estas notas: {text}")
    preguntaf="Cuantos años tienes?"
    respuestaf="Nose"
    respuestaqu="Nose"

    if st.checkbox("Learn📖"):
        res=procesar_variable(f"hazme un resumen corto de ellas")
        st.write(res)
    if st.checkbox("Flashcards📇"):
        preguntaf=procesar_variable(f"hazme una pregunta del texto para estudiar, solo la pregunta")
        respuestaf=procesar_variable(f"dime la respuesta de manera corta, solo la respuesta")
        st.write(preguntaf)
        Respuesta = st.button('Show answer!')
        if Respuesta:
            st.write(respuestaf)

    if st.checkbox("Quiz📝"):
        preguntaf=(procesar_variable(f"hazme una pregunta del texto para estudiar con 4 opciones de respuesta "))
        st.write(preguntaf)
        res = st.text_input('Type yours answer')
        fed=(procesar_variable((res)))
        st.write(fed)
    col2, col4 = st.columns([1,0.15])
    with col4:
        authenticator.logout("Logout")

    




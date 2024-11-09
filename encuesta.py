import os
import re
import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Cargar las credenciales desde variables de entorno
credentials_dict = {
    "type": os.getenv("GCP_TYPE"),
    "project_id": os.getenv("GCP_PROJECT_ID"),
    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GCP_CLIENT_EMAIL"),
    "client_id": os.getenv("GCP_CLIENT_ID"),
    "auth_uri": os.getenv("GCP_AUTH_URI"),
    "token_uri": os.getenv("GCP_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL")
}

# Guardar temporalmente las credenciales para autenticar
with open("temp_credentials.json", "w") as f:
    json.dump(credentials_dict, f)


# Configuración de Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("temp_credentials.json", scope)
client = gspread.authorize(creds)

# Eliminar el archivo temporal de credenciales para mayor seguridad
os.remove("temp_credentials.json")

sheet = client.open("Encuesta").sheet1  # Reemplaza con el nombre de tu hoja

# Función para generar un ID único e incremental
def obtener_siguiente_id():
    records = sheet.get_all_records()
    if records:
        ultimo_id = records[-1].get("ID", 0)  # Obtiene el último ID registrado en la columna "ID"
        return ultimo_id + 1
    else:
        return 1  # Si no hay registros, comienza con ID = 1

# Función para almacenar el resultado en Google Sheets
def guardar_resultado(user_id, e_mail, color_predominante, color_secundario, color_terciario, id_unico):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([user_id, e_mail, color_predominante, color_secundario, color_terciario, timestamp, id_unico])

# Función para calcular el color predominante y complementarios
def calcular_colores(respuestas):
    # Determinación del color predominante y complementarios (ejemplo básico)
    colores = {
        "Rojo": sum(1 for r in respuestas if "A. " in r),
        "Verde": sum(1 for r in respuestas if "B. " in r),
        "Azul": sum(1 for r in respuestas if "C. " in r),
        "Amarillo": sum(1 for r in respuestas if "D. " in r)
    }        
    colores_ordenados = sorted(colores.items(), key=lambda x: x[1], reverse=True)    
    color_predominante = colores_ordenados[0][0]
    color_secundario = colores_ordenados[1][0] if colores_ordenados[1][1] > 0 else None
    color_terciario = colores_ordenados[2][0] if colores_ordenados[2][1] > 0 else None
    return color_predominante, color_secundario, color_terciario    

# Función para verificar si el correo ya fue registrado
def verificar_correo_registrado(user_email):
    registros = sheet.get_all_records()
    for registro in registros:
        if registro.get("e_mail") == user_email:
            return True
    return False

# Función para validar el formato del correo electrónico
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

# Función para mostrar y guardar el resultado
def mostrar_resultado(color_predominante, color_secundario, color_terciario):
    resultado = f"Tu color predominante es {color_predominante}."
    if color_secundario:
        resultado += f" Color complementario: {color_secundario}."
    if color_terciario:
        resultado += f" Otro color complementario: {color_terciario}."    
    st.success(resultado)
    
# Inicializar variables de estado
if "encuesta_completada" not in st.session_state:
    st.session_state.encuesta_completada = False
if "agradecimiento" not in st.session_state:
    st.session_state.agradecimiento = ""
if "color_resultado" not in st.session_state:
    st.session_state.color_resultado = ""
if "correo_valido" not in st.session_state:
    st.session_state.correo_valido = ""
    

#Cargar preguntas desde un archivo Json
with open("preguntas.json", "r", encoding="utf-8") as file:
    preguntas = json.load(file)
    
st.title("Test de Personalidad: Descubre tu Color Predominante")  

# Preguntar al usuario si el correo ya está registrado
user_id = st.text_input("Introduce tu nombre:", "")   
e_mail = st.text_input("Introduce tu correo electrónico:", "")
if e_mail:
    if validar_correo(e_mail):
        if verificar_correo_registrado(e_mail):
            st.session_state.encuesta_completada = True
            st.session_state.color_resultado = "Este correo ya ha sido registrado."
            st.session_state.agradecimiento = "¡Gracias por completar la encuesta! 🎉"        
        else:
            st.session_state.encuesta_completada = False
    else:
        st.session_state.correo_valido = 'Introduce un correo válido.'

if st.session_state.encuesta_completada:
    st.success(st.session_state.agradecimiento)
    st.write(st.session_state.color_resultado)
else:
    respuestas = []
    
    # Validar que el usuario haya ingresado su identificador
    if user_id and validar_correo(e_mail):    
        st.write("Responde a todas las preguntas antes de enviar.")
        
        # Diccionario para almacenar las respuestas del usuario
        respuestas_dict = {i: None for i in range(len(preguntas))}
        
        # Preguntas y opciones
        for i, pregunta in enumerate(preguntas):
            opciones = ["Seleccione una respuesta"] + pregunta["opciones"]
            st.write(f"**Pregunta {i+1}:** {pregunta['pregunta']}")
            respuesta = st.radio("", opciones, key=i)
            respuestas_dict[i] = respuesta        
    
        # Botón para enviar respuestas
        if st.button("Enviar"):
            if "Seleccione una respuesta" in respuestas_dict.values():
                st.warning("Por favor, responde a todas las preguntas antes de enviar.")
            else:
                st.success("Gracias por completar la encuesta.")            
                respuestas = list(respuestas_dict.values())                
                id_unico = obtener_siguiente_id()
                color_predominante, color_secundario, color_terciario = calcular_colores(respuestas)
                guardar_resultado(user_id, e_mail, color_predominante, color_secundario or "", color_terciario or "", id_unico)                 
                mostrar_resultado(color_predominante, color_secundario, color_terciario)
                st.session_state.encuesta_completada = True
    else:
        st.warning("Por favor, introduce tus datos completos. " + st.sesion_state.correo_valido)

import os
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

# Opcional: Elimina el archivo temporal si deseas mayor seguridad
import os
os.remove("temp_credentials.json")

sheet = client.open("Encuesta").sheet1  # Reemplaza con el nombre de tu hoja

# Función para almacenar el resultado en Google Sheets
def guardar_resultado(user_id, color_predominante, color_secundario, color_terciario):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([user_id, color_predominante, color_secundario, color_terciario, timestamp])

# Preguntas del Test
preguntas = []


# Título de la aplicación
st.title("Test de Personalidad: Descubre tu Color Predominante")

# Identificador único del usuario
user_id = st.text_input("Introduce tu nombre:", "")

# Validar que el usuario haya ingresado su identificador
if user_id:
    respuestas = []

    # Preguntas y opciones
    for i, pregunta in enumerate(preguntas):
        st.write(f"**Pregunta {i+1}:** {pregunta['pregunta']}")
        respuesta = st.radio("", pregunta["opciones"], key=i)
        respuestas.append(respuesta)

    # Botón para enviar respuestas
    if st.button("Enviar"):
        # Determinación del color predominante y complementarios (ejemplo básico)
        colores = {
            "Rojo": sum(1 for r in respuestas if "A. " in r),
            "Verde": sum(1 for r in respuestas if "B. " in r),
            "Azul": sum(1 for r in respuestas if "C. " in r),
            "Amarillo": sum(1 for r in respuestas if "D. " in r)
        }
        
        # Ordenar colores por frecuencia
        colores_ordenados = sorted(colores.items(), key=lambda x: x[1], reverse=True)

        # Identificar el color predominante
        color_predominante = colores_ordenados[0][0]

        # Identificar colores complementarios solo si tienen un valor distinto de cero
        color_secundario = colores_ordenados[1][0] if colores_ordenados[1][1] > 0 else None
        color_terciario = colores_ordenados[2][0] if colores_ordenados[2][1] > 0 else None

        # Guardar resultado
        guardar_resultado(user_id, color_predominante, color_secundario or "", color_terciario or "")

        # Mostrar resultado
        resultado = f"Tu color predominante es {color_predominante}."
        if color_secundario:
            resultado += f" Color complementario: {color_secundario}."
        if color_terciario:
            resultado += f" Otro color complementario: {color_terciario}."
        
        st.success(resultado)
else:
    st.warning("Por favor, introduce tu identificador único.")

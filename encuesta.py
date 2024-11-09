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
preguntas = [
    {
        "pregunta": "¿Cómo prefieres abordar los problemas en el trabajo o en la vida cotidiana?",
        "opciones": [
            "A. Tomando decisiones rápidas y directas para resolver el problema.",  # Rojo
            "B. Buscando consenso y evitando conflictos para mantener la armonía.",  # Verde
            "C. Analizando cuidadosamente los detalles y planificando cada paso.",  # Azul
            "D. Pensando en soluciones creativas y motivando a los demás para actuar."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Cómo te describen generalmente tus amigos y compañeros de trabajo?",
        "opciones": [
            "A. Decidido/a, asertivo/a y orientado/a a resultados.",  # Rojo
            "B. Amable, empático/a y un buen mediador/a.",  # Verde
            "C. Organizado/a, preciso/a y orientado/a al detalle.",  # Azul
            "D. Optimista, sociable y lleno/a de energía."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Qué valoras más en el trabajo o en un proyecto?",
        "opciones": [
            "A. La eficiencia y los logros.",  # Rojo
            "B. La colaboración y el bienestar del equipo.",  # Verde
            "C. La precisión y el cumplimiento de normas.",  # Azul
            "D. La creatividad y el entusiasmo."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Cómo sueles tomar decisiones?",
        "opciones": [
            "A. Rápidamente, guiado/a por la intuición y los resultados que quiero lograr.",  # Rojo
            "B. Con cautela, considerando cómo afectará a los demás.",  # Verde
            "C. Tras evaluar toda la información y los datos disponibles.",  # Azul
            "D. De manera espontánea, basándome en las oportunidades del momento."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Qué haces cuando enfrentas un desafío nuevo?",
        "opciones": [
            "A. Me lanzo sin dudar, confiado/a en que encontraré la solución en el camino.",  # Rojo
            "B. Pido ayuda o busco apoyo para enfrentar el desafío en equipo.",  # Verde
            "C. Reviso todos los detalles y diseño un plan estructurado.",  # Azul
            "D. Encuentro la parte divertida del desafío y lo enfrento con energía."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Cómo te comportas en reuniones o eventos sociales?",
        "opciones": [
            "A. Suelo liderar y proponer soluciones o acciones.",  # Rojo
            "B. Prefiero escuchar y apoyar a los demás.",  # Verde
            "C. Me concentro en los detalles y en asegurarme de que todos entiendan los puntos clave.",  # Azul
            "D. Hablo y me relaciono con facilidad, buscando animar el ambiente."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Cuál es tu reacción cuando recibes una crítica?",
        "opciones": [
            "A. La tomo con seguridad y, si es necesario, defiendo mi posición.",  # Rojo
            "B. Me lo tomo a pecho y tiendo a buscar reconciliación.",  # Verde
            "C. Lo analizo y considero si es una observación válida.",  # Azul
            "D. Trato de tomarlo con humor y mantener una actitud positiva."  # Amarillo
        ]
    },
    {
        "pregunta": "¿Qué te resulta más satisfactorio al finalizar un proyecto?",
        "opciones": [
            "A. Lograr resultados concretos y cumplir los objetivos.",  # Rojo
            "B. Sentir que todos en el equipo están contentos y satisfechos.",  # Verde
            "C. Ver que el trabajo ha sido hecho con precisión y sin errores.",  # Azul
            "D. Disfrutar el proceso y ver que el equipo mantiene un buen ánimo."  # Amarillo
        ]
    }
]


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

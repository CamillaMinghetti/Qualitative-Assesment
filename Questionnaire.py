import streamlit as st  # type: ignore
import pandas as pd  
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Titolo dell'app
st.title("Qualitative Performance Assessment of EndoDAC and Depth Pro Models")

# Descrizione del questionario
st.write(
    "The video in the center shows a colonoscopy, while the two side videos (left and right) "
    "represent depth maps generated by two predictive models, where blue indicates deeper areas "
    "and red indicates shallower areas. \n"
    "Which of the two side videos (left or right) do you think best reflects reality in terms of accuracy in depth estimation?"
)

# Prima domanda: sei un clinico?
clinician = st.radio("Are you a clinician?", ["Yes", "No"])

# Se sei un clinico, quale livello di esperienza?
experience_level = None
procedures_performed = None
if clinician == "Yes":
    experience_level = st.radio("What is your experience level?", ["Specializzando", "Resident", "Esperto"])
    procedures_performed = st.radio(
        "How many endoscopic procedures have you performed?",
        ["<50", "Between 50 and 100", ">100"]
    )

# Seconda domanda: nome
name = st.text_input("Please enter your name")

# Video da mostrare
video_paths = [
    './VideoColonoscopy3.mp4',
    './VideoColonoscopy4.mp4',
    './VideoColonoscopy5.mp4',
    './VideoColonoscopy6.mp4',
    './VideoColonoscopy7.mp4',
    './VideoColonoscopy8.mp4',
    './VideoColonoscopy9.mp4',
    './VideoColonoscopy10.mp4',
    './VideoColonoscopy11.mp4',
    './VideoColonoscopy12.mp4',
]

# Session state
if "question_index" not in st.session_state:
    st.session_state["question_index"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = [None] * len(video_paths)

# Se l'utente ha inserito il nome, procedi con il questionario
if name:
    st.header("Questionnaire")
    
    question_index = st.session_state["question_index"]
    
    st.subheader(f"Question {question_index + 1}")
    st.video(video_paths[question_index])
    
    existing_response = st.session_state["responses"][question_index]
    default_index = 0 if existing_response == "Left" else 1 if existing_response == "Right" else None
    
    response = st.radio(
        "Which of the two side videos (left or right) do you think best reflects reality in terms of accuracy in depth estimation?", 
        ["Left", "Right"], 
        key=f"question_{question_index}",
        index=default_index
    )
    
    st.session_state["responses"][question_index] = response
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous") and question_index > 0:
            st.session_state["question_index"] -= 1
            st.rerun()
    with col2:
        if st.button("Next") and question_index < len(video_paths) - 1:
            st.session_state["question_index"] += 1
            st.rerun()
    
    # Codice per inviare le risposte a Google Sheets
    if question_index == len(video_paths) - 1 and st.button("Submit Answers"):
        # Ottieni le credenziali JSON da Streamlit Secrets
        gcp_credentials = st.secrets["gcp_credentials"]

        # Crea un dizionario con le credenziali
        credentials_dict = {
            "type": gcp_credentials["type"],
            "project_id": gcp_credentials["project_id"],
            "private_key_id": gcp_credentials["private_key_id"],
            "private_key": gcp_credentials["private_key"],
            "client_email": gcp_credentials["client_email"],
            "client_id": gcp_credentials["client_id"],
            "auth_uri": gcp_credentials["auth_uri"],
            "token_uri": gcp_credentials["token_uri"],
            "auth_provider_x509_cert_url": gcp_credentials["auth_provider_x509_cert_url"],
            "client_x509_cert_url": gcp_credentials["client_x509_cert_url"],
            "universe_domain": gcp_credentials["universe_domain"]
        }

        # Crea le credenziali utilizzando il dizionario
        creds = Credentials.from_service_account_info(credentials_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])

        # Connetti a Google Sheets
        service = build("sheets", "v4", credentials=creds)
        sheet_id = "1keTMaYMtN0D-YIClxJFxYAKOMeb1ddKPIHH6Q92LxYw"  # Sostituisci con il tuo Google Sheet ID  # Sostituisci con l'ID del tuo Google Sheets

        # Crea i dati da inviare
        new_data = {
            "Name": name,
            "Clinician": clinician,
            "Experience Level": experience_level if clinician == "Yes" else None,
            "Procedures Performed": procedures_performed if clinician == "Yes" else None,
        }

        for i in range(len(video_paths)):
            new_data[f"Question {i+1}"] = st.session_state["responses"][i] if st.session_state["responses"][i] else "No Response"

        # Prepara la riga dei dati da inviare a Google Sheets
        data = [list(new_data.values())]

        # Scrivi i dati nel foglio
        sheet = service.spreadsheets()
        request = sheet.values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A1",  # Sostituisci con la tua gamma (range) di celle
            valueInputOption="RAW",
            body={"values": data},
        )
        request.execute()

        st.success("Your answers have been saved to Google Sheets!")
        st.stop()

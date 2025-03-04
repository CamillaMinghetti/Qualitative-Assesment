import streamlit as st  # type: ignore
import pandas as pd  
import gspread
from google.oauth2.service_account import Credentials


# Configura Google Sheets
def save_to_google_sheets(name, clinician, experience_level, procedures, responses):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Apri il Google Sheet (sostituisci con il tuo ID)
    sheet = client.open_by_key("ABC1234567890xyz").sheet1  # Sostituisci con il tuo ID foglio

    # Crea una nuova riga con i dati
    new_data = [name, clinician, experience_level, procedures] + responses

    # Aggiungi la riga nel foglio
    sheet.append_row(new_data)

    st.success("Risposte salvate con successo su Google Sheets!")


# Titolo della web app
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

# Se sei un clinico, chiediamo esperienza
experience_level = None
procedures_performed = None
if clinician == "Yes":
    experience_level = st.radio("What is your experience level?", ["Specializzando", "Resident", "Esperto"])
    procedures_performed = st.radio(
        "How many endoscopic procedures have you performed?",
        ["<50", "Between 50 and 100", ">100"]
    )

# Nome del partecipante
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

# Session state per gestire le domande
if "question_index" not in st.session_state:
    st.session_state["question_index"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = [None] * len(video_paths)

# Se il nome è stato inserito, mostriamo il questionario
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
    
    # Salvataggio delle risposte su Google Sheets
    if question_index == len(video_paths) - 1 and st.button("Submit Answers"):
        responses = [st.session_state["responses"][i] if st.session_state["responses"][i] else "No Response" for i in range(len(video_paths))]

        save_to_google_sheets(name, clinician, experience_level if clinician == "Yes" else None, procedures_performed if clinician == "Yes" else None, responses)

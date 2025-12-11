# -*- coding: utf-8 -*-
"""Student Grade Predictor.ipynb

Original file is located at
    https://colab.research.google.com/drive/10qPmK-N_7CfehlEjKT5Owm0SHMw9Uqrv
"""

# Importing libraries

import streamlit as st    #load streamlit library#
import re                 #Used for pattern matching#

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Student Predictor", layout="wide")   #Initial configuration of webpage#
st.title("Student Predictor Chatbot")                               #Displays big page title#

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:              #creates sidebar section on the left#
    st.title("Student Predictor Chatbot")   #Displays a title in the sidebar#
    st.write(                               #Adds a short description#
        "This chatbot predicts your grade based on your subject scores. "
        "Provide scores like 'math: 80 english: 90' and ask for 'predict my grade'."
    )

    st.sidebar.divider()                   #draws a horizontal line to separate sections#

    st.sidebar.header("Student Information")  #adds a section header in the sidebar#
    student_name = st.sidebar.text_input("Student Name") #creates a text field where users type their name#
    year_level = st.sidebar.selectbox(                   #creates dropdown with yr levels#
        "Year Level",
        ["First year", "Second year", "Third year", "Fourth year"]
    )
    current_gpa = st.sidebar.number_input("Current GPA", 0.0, 4.0, 3.0)  #numeric input field#
    st.sidebar.progress(0.75, text="75% towards target grade")           #displays a progress bar#

    st.sidebar.header("Study Habits")                                    #labels the next group of inputs#
    study_hours = st.sidebar.number_input("Study Hours per Week", 0, 168, 10)
    attendance = st.sidebar.slider("Attendance Rate (%)", 0, 100, 80)

    st.sidebar.header("Other Factors")                                #separates the next category of inputs#
    extracurriculars = st.sidebar.multiselect(
        "Extracurricular Activities",
        ["Sports", "Music", "Chess", "Drama", "Volunteer Work", "Table tennis", "Christian Union"]
    )
    previous_grade = st.sidebar.selectbox(                  #Dropdown to choose last course grade#
        "Previous Course Grade", ["A", "B", "C", "D", "F"]
    )

    st.sidebar.header("Exam Information")           #Defines another section heading#
    exam_date = st.sidebar.date_input("Exam Date")
    confidence = st.slider("Confidence level", 50, 100, 80)    #slider for self confidence#

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "history" not in st.session_state:        #checks whether the key 'history' exists inside streamlit's session_state#
    st.session_state.history = []            # a small memory#

if "scores" not in st.session_state:         #if theres no history yet it creates an empty list#
    st.session_state.scores = {}

# ---------------------------------------------------
# CHAT HISTORY DISPLAY
# ---------------------------------------------------
for msg in st.session_state.history:         #loops through every saved chat message#
    with st.chat_message(msg["role"]):       #creates a chat bubble UI for each message#
        st.write(msg["content"])             #writes the message inside the bubble#

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def extract_scores_from_text(text):
    """Extract subject scores from user input using pattern: subject: score."""    #extract subject score pairs from what the user types#
    matches = re.findall(r'(\w+)\s*:\s*(\d+)', text.lower())                       #uses regex to find patterns#
    scores = {subject: int(score) for subject, score in matches}                   #converts all matched pairs into a dictionary#
    return scores


def calculate_grade(scores_dict):         #compute an average score and convert it into a letter grade#
    """Calculate the final grade from extracted scores."""
    if not scores_dict:
        return None
    avg = sum(scores_dict.values()) / len(scores_dict)

    if avg >= 90:
        grade = "A"
    elif avg >= 80:
        grade = "B"
    elif avg >= 70:
        grade = "C"
    elif avg >= 60:
        grade = "D"
    else:
        grade = "F"

    return grade, avg


def detect_intent(user_input):                                            #identify what the user wants#
    """Detect user intent based on keywords and score patterns."""   
    text = user_input.lower()

    # Priority: score detection first
    if extract_scores_from_text(user_input):
        return "provide_scores"

    if any(word in text for word in ["hello", "hi", "hey"]):
        return "greeting"

    if "predict" in text and "grade" in text:
        return "predict"

    if any(word in text for word in ["help", "how", "what can you do"]):
        return "help"

    if any(word in text for word in ["bye", "exit", "quit"]):
        return "exit"

    return "fallback"


def generate_response(intent, user_input):
    """Rule–based responses according to detected intent."""
    
    if intent == "greeting":
        return (
            "Hello! I'm your Student Grade Predictor chatbot. "
            "Share scores like 'math: 85 science: 90' and I'll predict your grade!"
        )

    if intent == "provide_scores":
        new_scores = extract_scores_from_text(user_input)
        st.session_state.scores.update(new_scores)
        formatted = ", ".join([f"{k.capitalize()}: {v}" for k, v in new_scores.items()])
        return f"Got it! I've recorded your scores: {formatted}. Say 'predict my grade' when you're ready."

    if intent == "predict":
        if st.session_state.scores:
            grade, avg = calculate_grade(st.session_state.scores)
            return f"Your predicted grade is **{grade}** with an average of **{avg:.1f}%**. Keep going!"
        return "You haven't given me any scores yet. Provide something like 'math: 85'."

    if intent == "help":
        return (
            "I predict grades based on the scores you give me. "
            "Try: 'math: 80 english: 90', then say 'predict my grade'."
        )

    if intent == "exit":
        return "Goodbye! Come back any time."

    return (
        "Hmm, I didn't understand that. You can give me scores like 'biology: 78', "
        "ask for 'predict my grade', or say 'help'!"
    )


# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------
user_input = st.chat_input("Ask me anything about your grades:")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    intent = detect_intent(user_input)
    response = generate_response(intent, user_input)

    st.session_state.history.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.write(response)

    st.rerun()

# ---------------------------------------------------
# SIDEBAR SCORE SUMMARY
# ---------------------------------------------------
if st.session_state.scores:
    st.sidebar.divider()
    st.sidebar.header("📊 Current Scores")

    for subject, score in st.session_state.scores.items():
        st.sidebar.write(f"**{subject.capitalize()}**: {score}")

    grade_info = calculate_grade(st.session_state.scores)
    if grade_info:
        grade, avg = grade_info
        st.sidebar.metric("Predicted Grade", grade, f"Average: {avg:.1f}%")

            
   
            

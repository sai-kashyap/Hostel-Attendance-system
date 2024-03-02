import streamlit as st
from pages import notification, warden , student_details , vacation , attendance,registration

st.set_page_config(page_title="Hostel Management", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Notification", "warden","Student details","vacation", "Take Attendance","New Registrartion"])

if page == "Notification":
    notification.app()
elif page == "warden":
    warden.app()
elif page=="Student details":
    student_details.app()
elif page=="vacation":
    vacation.app()
elif page=="Take Attendance":
    attendance.app()
elif page=="New Registrartion":
    registration.app()

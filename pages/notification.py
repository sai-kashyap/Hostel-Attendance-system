import streamlit as st
import mysql.connector
import pywhatkit as kit
import threading
from datetime import datetime, timedelta, time
def app():
    # Establish a MySQL connection
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="nandan@931",
        database="myproject"
    )
    cursor = db.cursor()

    # Retrieve student data from the database
    def fetch_students():
        cursor.execute("SELECT * FROM student_")
        return cursor.fetchall()

    # Function to send messages using pywhatkit with a timed delay
    def send_whatsapp_message(phone, message, send_time):
        kit.sendwhatmsg(f"+91{phone}", message, send_time.time().hour, send_time.time().minute)  # Set the scheduled send time

    # Streamlit web app
    st.title('WhatsApp Message Sender to Students')

    students = fetch_students()

    selected_students = st.multiselect('Select students to send messages', [student[1] for student in students])

    message = st.text_area("Compose your WhatsApp message")

    send_time = st.time_input("Select the time to send the message", value=time(0, 0))

    if st.button('Send Message'):
        selected_students_info = [student for student in students if student[1] in selected_students]

        # Extract phone numbers of selected students
        selected_student_numbers = [student[2] for student in selected_students_info]

        # Initialize datetime object with today's date and selected time
        current_datetime = datetime.combine(datetime.today(), send_time)

        # Initialize delay increment
        delay_increment = timedelta(seconds=15)  # 15 seconds delay between messages

        # Threaded messages with the selected time and delay
        for idx, phone_number in enumerate(selected_student_numbers):
            send_whatsapp_message(phone_number, message, current_datetime)
            current_datetime += delay_increment  # Increment the current_datetime by the delay

        # Display success message
        st.success(f"Messages sent to selected students starting at {send_time.hour}:{send_time.minute} with a 15-second delay between messages.")

    # Close the MySQL connection
    cursor.close()
    db.close()

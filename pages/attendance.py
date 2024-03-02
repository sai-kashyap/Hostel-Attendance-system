import cv2
import face_recognition
import mysql.connector
from mysql.connector import Error
from PIL import Image
from io import BytesIO
import streamlit as st
from datetime import date
def app():
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "attendance",
        "password": "password",
        "database": "myproject"
    }

    # Function to get student SRN from Streamlit input
    def get_srn():
        srn = st.text_input("Enter student SRN:")
        return srn

    # SQL queries
    select_query = "SELECT image FROM student_ WHERE srn = %s"
    insert_query = "INSERT INTO attendance (date, SRN) VALUES (%s, %s)"
    check_existing_query = "SELECT * FROM attendance WHERE date = %s AND SRN = %s"

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)

    if connection.is_connected():
        st.write("Connected to MySQL database")

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Streamlit app title
        st.title("Face Recognition Attendance System")

        # Get SRN from Streamlit input
        srn = get_srn()

        # Execute the SELECT query with the provided SRN
        cursor.execute(select_query, (srn,))

        # Fetch the first row from the result set
        result = cursor.fetchone()

        # Check if there is a result
        if result is not None:
            # Access the image data from the result
            image_data = result[0]

            # Create an image object from the binary data
            known_image = face_recognition.load_image_file(BytesIO(image_data))

            # Encode the known face
            known_face_encoding = face_recognition.face_encodings(known_image)[0]

            # Streamlit webcam access
            cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

            # Streamlit placeholder for the webcam feed
            img_placeholder = st.empty()

            
            # Capture an image for the unknown face
            ret, unknown_frame = cap.read()
            # Check if the frame is captured
            if ret:
                # Convert the captured frame to the required format (BGR to RGB)
                unknown_image = cv2.cvtColor(unknown_frame, cv2.COLOR_BGR2RGB)
                # Find face locations in the unknown image
                face_locations = face_recognition.face_locations(unknown_image)
                if len(face_locations) == 0:
                    st.write("No faces found in the captured image.")
                else:
                    # Encode the faces in the unknown image
                    unknown_face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
                    # Compare the known face encoding with all the unknown face encodings
                    for unknown_face_encoding in unknown_face_encodings:
                        results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)
                        if results[0]:
                            st.write("Match: The known face matches the unknown.")
                            # Check if attendance record already exists for the current date and SRN
                            current_date = date.today()
                            cursor.execute(check_existing_query, (current_date, srn))
                            existing_record = cursor.fetchone()
                            if not existing_record:
                                # Attendance record does not exist, insert a new one
                                cursor.execute(insert_query, (current_date, srn))
                                connection.commit()
                                st.write("Attendance updated.")
                            else:
                                st.write("Attendance already marked for this student.")
            else:
                st.write("Unable to capture the image for the unknown face.")
            # Display the webcam feed in Streamlit
            img_placeholder.image(unknown_frame, channels="RGB")
        # Close the cursor and database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            st.write("Connection closed")

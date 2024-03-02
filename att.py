import cv2
import face_recognition
import mysql.connector
from mysql.connector import Error
from PIL import Image
from io import BytesIO
import tkinter as tk
from tkinter import simpledialog
from datetime import date

# Database configuration
db_config = {
    "host": "localhost",
    "user": "attendance",
    "password": "password",
    "database": "myproject"
}

# Function to get student SRN from tkinter GUI
def get_srn():
    srn = simpledialog.askstring("Input", "Enter student SRN:")
    return srn

# SQL queries
select_query = "SELECT image FROM student_ WHERE srn = %s"
insert_query = "INSERT INTO attendance (date, SRN) VALUES (%s, %s)"
check_existing_query = "SELECT * FROM attendance WHERE date = %s AND SRN = %s"

try:
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MySQL database")

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Get SRN from tkinter GUI
        srn = get_srn()

        # Execute the SELECT query with the provided SRN
        cursor.execute(select_query, (srn,))

        # Fetch the image data
        image_data = cursor.fetchone()[0]

        # Create an image object from the binary data
        known_image = face_recognition.load_image_file(BytesIO(image_data))

        # Encode the known face
        known_face_encoding = face_recognition.face_encodings(known_image)[0]

        # Access the webcam to capture an image for the unknown face
        cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

        # Capture an image for the unknown face
        ret, unknown_frame = cap.read()

        # Check if the frame is captured
        if ret:
            # Convert the captured frame to the required format (BGR to RGB)
            unknown_image = cv2.cvtColor(unknown_frame, cv2.COLOR_BGR2RGB)

            # Find face locations in the unknown image
            face_locations = face_recognition.face_locations(unknown_image)

            if len(face_locations) == 0:
                print("No faces found in the captured image.")
            else:
                # Encode the faces in the unknown image
                unknown_face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

                # Compare the known face encoding with all the unknown face encodings
                for unknown_face_encoding in unknown_face_encodings:
                    results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)
                    if results[0]:
                        print("Match: The known face matches the unknown.")

                        # Check if attendance record already exists for the current date and SRN
                        current_date = date.today()
                        cursor.execute(check_existing_query, (current_date, srn))
                        existing_record = cursor.fetchone()

                        if not existing_record:
                            # Attendance record does not exist, insert a new one
                            cursor.execute(insert_query, (current_date, srn))
                            connection.commit()
                            print("Attendance updated.")
                        else:
                            print("Attendance already marked for this student.")
        else:
            print("Unable to capture the image for the unknown face.")

except Error as e:
    print(f"Error: {e}")

finally:
    # Close the cursor and database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed")

    # Release the camera
    cap.release()

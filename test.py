import cv2
import face_recognition
import mysql.connector
from mysql.connector import Error
from PIL import Image
from io import BytesIO
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import date, datetime

# Database configuration
db_config = {
    "host": "localhost",
    "user": "attendance",
    "password": "password",
    "database": "myproject"
}

# SQL queries
select_query = "SELECT image FROM student_ WHERE srn = %s"
insert_query = "INSERT INTO attendance (date, SRN) VALUES (%s, %s)"

# Function to get student SRN from tkinter GUI
def get_srn():
    srn = simpledialog.askstring("Input", "Enter student SRN:")
    return srn

# Function to update the GUI with the current time
def update_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.config(text="Current Time: " + current_time)
    root.after(1000, update_time)  # Update every 1000 milliseconds (1 second)

try:
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MySQL database")

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Create Tkinter GUI
        root = tk.Tk()
        root.title("Face Recognition Attendance System")

        # Label to display current time
        time_label = tk.Label(root, text="")
        time_label.pack()

        # Start updating the time
        update_time()

        # Access the webcam to continuously capture images
        cap = cv2.VideoCapture(0)  # Change the index if you have multiple cameras

        while True:
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

            # Capture an image for the unknown face
            ret, unknown_frame = cap.read()

            # Check if the frame is captured
            if ret:
                # Convert the captured frame to the required format (BGR to RGB)
                unknown_image = cv2.cvtColor(unknown_frame, cv2.COLOR_BGR2RGB)

                # Find face locations in the unknown image
                face_locations = face_recognition.face_locations(unknown_image)

                if len(face_locations) > 0:
                    # Encode the faces in the unknown image
                    unknown_face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

                    # Compare the known face encoding with all the unknown face encodings
                    for unknown_face_encoding in unknown_face_encodings:
                        results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)
                        if results[0]:
                            print("Match: The known face matches the unknown.")

                            # Update the attendance table with the current date and SRN
                            current_date = date.today()
                            try:
                                cursor.execute(insert_query, (current_date, srn))
                                connection.commit()
                                print("Attendance updated.")
                                messagebox.showinfo("Attendance", "Attendance marked successfully.")
                            except Error as e:
                                # Handle the case where attendance has already been marked
                                if "Duplicate entry" in str(e):
                                    print("Error: Attendance already marked for this student.")
                                    messagebox.showinfo("Error", "Attendance already marked for this student.")
                            finally:
                                # Continue capturing images for attendance
                                break

                else:
                    print("No faces found in the captured image.")

            else:
                print("Unable to capture the image for the unknown face.")

        # Close the cursor and database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed")

except Error as e:
    print(f"Error: {e}")

# Release the camera
cap.release()
# Close the Tkinter GUI
root.mainloop()

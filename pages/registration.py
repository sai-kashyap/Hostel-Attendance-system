import streamlit as st
import mysql.connector
from PIL import Image
from io import BytesIO
def app():
    def add_student(name, srn, phone, section, room_no, block_id, parent_name, parent_phone, parent_address, guardian_name, guardian_phone, guardian_address, image_data):
        # Database connection parameters
        db_config = {
            "host": "localhost",
            "user": "register",
            "password": "registration",
            "database": "myproject"
        }

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check if all student fields are filled
            if not name or not srn or not phone or not section or not room_no or not block_id:
                st.error("All student fields are required")
                return

            # Check if all parent fields are filled
            if not parent_name or not parent_phone or not parent_address:
                st.error("All parent fields are required")
                return

            # Check if all guardian fields are filled
            if not guardian_name or not guardian_phone or not guardian_address:
                st.error("All guardian fields are required")
                return

            # Insert student details
            student_query = "INSERT INTO student_ (name, SRN, phone, section, room_no, block_id, image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            student_values = (name, srn, phone, section, room_no, block_id, image_data)
            cursor.execute(student_query, student_values)

            # Insert parent details
            parent_query = "INSERT INTO Parent (name, phone, addr, SRN) VALUES (%s, %s, %s, %s)"
            parent_values = (parent_name, parent_phone, parent_address, srn)
            cursor.execute(parent_query, parent_values)

            # Insert guardian details
            guardian_query = "INSERT INTO guardian (name, phone, addr, SRN) VALUES (%s, %s, %s, %s)"
            guardian_values = (guardian_name, guardian_phone, guardian_address, srn)
            cursor.execute(guardian_query, guardian_values)

            conn.commit()
            conn.close()

            st.success("Student, Parent, and Guardian details added to the database")

        except Exception as e:
            st.error(f"Error: {e}")

    # Create the Streamlit app
    st.title("Student Database Entry")

    # Create input fields
    name = st.text_input("Name:")
    srn = st.text_input("SRN:")
    phone = st.text_input("Phone:")
    section = st.text_input("Section:")
    room_no = st.text_input("Room Number:")
    block_id = st.text_input("Block ID:")

    # Create input fields for parent information
    parent_name = st.text_input("Parent Name:")
    parent_phone = st.text_input("Parent Phone:")
    parent_address = st.text_input("Parent Address:")

    # Create input fields for guardian information
    guardian_name = st.text_input("Guardian Name:")
    guardian_phone = st.text_input("Guardian Phone:")
    guardian_address = st.text_input("Guardian Address:")

    # Create a file uploader for the image
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

    # Create a button to add the student
    if st.button("Add Student") and uploaded_file:
        # Convert the uploaded image file to bytes
        image_data = uploaded_file.read()

        # Resize the image if needed (adjust as necessary)
        img = Image.open(BytesIO(image_data))
        img = img.resize((200, 200))

        # Convert the image back to bytes
        image_data = BytesIO()
        img.save(image_data, format="PNG")
        image_data = image_data.getvalue()

        # Add student with image data to the database
        add_student(name, srn, phone, section, room_no, block_id, parent_name, parent_phone, parent_address, guardian_name, guardian_phone, guardian_address, image_data)

        st.text("Student, Parent, and Guardian details added successfully!")

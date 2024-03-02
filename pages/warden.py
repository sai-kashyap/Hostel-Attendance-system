import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import pywhatkit as pwk
def app():
    # MySQL database configuration
    db_config = {
        "host": "localhost",
        "user": "warden",
        "password": "warden",  
        "database": "myproject"
    }

    # Create a connection to the MySQL database
    conn = mysql.connector.connect(**db_config)

    # Streamlit app title
    st.title('Student Details for Warden')

    # User input for warden_id
    warden_id = st.number_input('Enter Warden ID:', min_value=1)

    if st.button('Fetch Student Details'):
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Define the SQL query to fetch absentees who are not in the attendance table for today
        student_query = f"""
        SELECT s.SRN, s.name ,s.room_no
        FROM student_ s
        LEFT JOIN block b ON s.block_id = b.block_id
        WHERE b.warden_id = {warden_id}
        AND s.SRN NOT IN (
            SELECT a.SRN 
            FROM attendance a 
            WHERE a.date = '{today}'
        );
        """
        # Execute the query and fetch the results
        student_df = pd.read_sql(student_query, conn)

        # Display student details in a dataframe
        st.write('Student Details:')
        st.dataframe(student_df)

        # Create a button for each student row to fetch parent and guardian details
        for index, row in student_df.iterrows():
            srn = row['SRN']
            
            # Define the SQL query to fetch parent and guardian details
            details_query = f"""
            SELECT p.name AS parent_name, p.phone AS parent_phone, p.addr AS parent_address,
                g.name AS guardian_name, g.phone AS guardian_phone, g.addr AS guardian_address
            FROM Parent p
            LEFT JOIN guardian g ON p.SRN = g.SRN
            WHERE p.SRN = '{srn}';
            """
            # Execute the query and fetch the results
            details_df = pd.read_sql(details_query, conn)
            # Display parent and guardian details in a dataframe
            if not details_df.empty:
                st.write(f"Parent and Guardian Details for SRN: {srn}")
                st.dataframe(details_df)
            else:
                st.write(f"No Parent and Guardian Details found for SRN: {srn}")





    if st.button('Send WhatsApp Messages to Absent Students'):
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Define the SQL query to fetch absent students' phone numbers
        absent_students_query = f"""
        SELECT phone
        FROM student_
        WHERE SRN NOT IN (
            SELECT SRN 
            FROM attendance 
            WHERE date = '{today}'
        );
        """
        # Execute the query and fetch absent students' phone numbers
        absent_students_phone_df = pd.read_sql(absent_students_query, conn)

        # Send WhatsApp messages to absent students
        for index, row in absent_students_phone_df.iterrows():
            phone_number = row['phone']
            # Here, send the WhatsApp message using pywhatkit
            pwk.sendwhatmsg(f"+91{phone_number}", "You were absent today for attendance. Please contact the warden before 10:15 without fail", 22,5)
            st.write(f"WhatsApp message sent to {phone_number}")

    # Close the database connection
    conn.close()
    # Close the database connection

    conn.close()

import mysql.connector
import streamlit as st

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "nandan@931",
    "database": "myproject"
}
def app():
    # Function to update vacation table with absence details
    def update_vacation_table(srn, start_date, end_date):
        try:
            connection = mysql.connector.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )

            cursor = connection.cursor()

            # Insert into the vacation table
            insert_query = "INSERT INTO vacation (srn, start_date, end_date) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (srn, start_date, end_date))
            connection.commit()

            st.success("Vacation details updated successfully")

        except mysql.connector.Error as error:
            st.error(f"Failed to update vacation details: {error}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    # Streamlit web app
    st.title("Update Vacation Details")

    srn = st.number_input("Enter SRN (Student Registration Number):", min_value=1)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if start_date > end_date:
        st.error("End date cannot be before the start date.")
    else:
        if st.button("Update Vacation Details"):
            update_vacation_table(srn, start_date, end_date)

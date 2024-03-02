import streamlit as st
import mysql.connector
import pandas as pd

def app():
    # Function to create MySQL connection
    def create_conn():
        conn = mysql.connector.connect(
            host='localhost',
            user='warden',
            password='warden',
            database='myproject'
        )
        return conn

    # Function to call stored procedures
    def call_procedure(procedure_name, srn):
        conn = create_conn()
        cursor = conn.cursor()

        try:
            cursor.callproc(procedure_name, [srn])
            
            # Fetch all the result sets (if any)
            for result in cursor.stored_results():
                # Get column names
                column_names = [i[0] for i in result.description]

                # Create a DataFrame from the result
                df = pd.DataFrame(result.fetchall(), columns=column_names)
                
                if not df.empty:
                    conn.close()
                    return df

            conn.close()
            return pd.DataFrame()  # Return empty DataFrame if no results

        except mysql.connector.Error as e:
            st.error(f"Error: {e}")
            return pd.DataFrame()

    # Streamlit app
    st.title('Details')

    # Input for SRN
    srn = st.text_input('Enter SRN')

    # Button to fetch and display student details
    if st.button('Get Student Details'):
        if srn:
            df = call_procedure('GetStudentInformation', srn)
            if not df.empty:
                st.write('**Student Details:**')
                st.table(df)
            else:
                st.write('No details found.')
        else:
            st.write('Please enter an SRN.')

    # Button to fetch and display parent details
    if st.button('Get Parent Details'):
        if srn:
            df = call_procedure('GetParentInformation', srn)
            if not df.empty:
                st.write('**Parent Details:**')
                st.table(df)
            else:
                st.write('No details found.')
        else:
            st.write('Please enter an SRN.')

    # Button to fetch and display guardian details
    if st.button('Get Guardian Details'):
        if srn:
            df = call_procedure('GetGuardianInformation', srn)
            if not df.empty:
                st.write('**Guardian Details:**')
                st.table(df)
            else:
                st.write('No details found.')
        else:
            st.write('Please enter an SRN.')

if __name__ == '__main__':
    app()

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
import re


excel_file = "details.xlsx"

    # Initialize DataFrame
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Receipt No'] = df['Receipt No'].astype(str)
else:
    df = pd.DataFrame(columns=['Receipt No', 'Name', 'Phone No', 'Location', 'Payment Mode', 'Amount (INR)', 'Date'])

    # Function to add data to the DataFrame
def add_data(df, receipt_no, name, phone_no, location, payment_mode, amount, date): #df as argument
        new_entry = {
            'Receipt No': str(receipt_no),
            'Name': name,
            'Phone No': phone_no,
            'Location': location,
            'Payment Mode': payment_mode,
            'Amount (INR)': amount,
            'Date': date
        }
        new_df = pd.DataFrame([new_entry])
        df = pd.concat([df, new_df], ignore_index=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df.to_excel(excel_file, index=False)
        return df #return df

def form_registration():
   
    global df 
    # Streamlit app layout
    st.title('Receipt Entry Form')

    # Input fields
    receipt_no = st.text_input('Receipt No')
    name = st.text_input('Name')
    phone_no = st.text_input('Phone No')
    location = st.text_input('Location')
    payment_mode = st.selectbox('Payment Mode', ['Cash', 'Online'])
    amount = st.number_input('Amount (INR)', min_value=0, step=1)
    date = st.date_input('Date', value=datetime.today().date())

    # Add Receipt button
    if st.button('Add Receipt'):
        if receipt_no and name and phone_no and location and amount:
            if str(receipt_no) in df['Receipt No'].values:
                st.error('Receipt No already exists. Please enter a unique Receipt No.')
            else:
                phone_regex = r"^[0-9]{10}$"
                if re.match(phone_regex, phone_no):
                    df = add_data(df, receipt_no, name, phone_no, location, payment_mode, amount, date) # pass df
                    st.write(df)
                    st.success('Receipt added successfully!')
                else:
                    st.error('Invalid Phone Number. Please enter a 10-digit number.')
        else:
            st.error('Please fill all fields.')

    # Return the DataFrame
    return df

# Call the function and get the DataFrame
df = form_registration()

# Payment summary (now df is accessible)
summary_date = st.date_input('Select Date for Payment Summary', value=datetime.today().date())

if not df.empty:
    filtered_df = df[df['Date'] == summary_date]
    if not filtered_df.empty:
        cash_sum = filtered_df[filtered_df['Payment Mode'] == 'Cash']['Amount (INR)'].sum()
        online_sum = filtered_df[filtered_df['Payment Mode'] == 'Online']['Amount (INR)'].sum()

        st.subheader(f'Payment Summary for {summary_date}')
        st.write(f"Total Cash Payments: INR {cash_sum}")
        st.write(f"Total Online Payments: INR {online_sum}")
    else:
        st.write(f"No payments found for {summary_date}")

# Download Excel button
if st.button('Update Excel'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Receipts')
    output.seek(0)
    st.download_button(
        label="Download Excel File",
        data=output,
        file_name="details.xlsx",
        mime="application/vnd.ms-excel"
    )
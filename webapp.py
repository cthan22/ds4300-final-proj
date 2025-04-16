import streamlit as st
import json

st.title('Wine Reviews')

file = st.file_uploader('Upload a JSON file here', type=['json'])

if file:
    try:
        data = json.load(file)
        st.json(data)
        st.success('File Upload Complete')
    except Exception as e:
        st.error(f'Error:{e}')
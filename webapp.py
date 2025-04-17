import streamlit as st
import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-2")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

st.title('Wine Reviews')
file = st.file_uploader('Upload a JSON file here', type=['json'])


if file is not None:

    data = json.load(file)
    if data:
        st.json(data)  # Display the data in Streamlit
    else:
        st.error("The file is empty or has invalid JSON content.")
        raise ValueError("The file is empty or has invalid JSON content.")
    #st.json(data)
    file.seek(0)
    filename = file.name

    try:
        s3_client.upload_fileobj(
            file,
            s3_bucket_name,
            f"uploads/{filename}",
        )

        st.success('File Upload Complete')
    except Exception as e:
        st.error(f'Error:{e}')
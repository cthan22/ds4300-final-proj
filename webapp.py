import streamlit as st
import json
import boto3
import os
import pymysql
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-2")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")

RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = int(os.getenv("RDS_PORT", 3306))
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DB = os.getenv("RDS_DB")

# Set up S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)

st.title('Wine Reviews Uploader & Dashboard')

# Upload section
st.header("Upload JSON to S3")
file = st.file_uploader("Upload a JSON file here", type=["json"])

if file is not None:
    data = json.load(file)
    st.json(data)
    file.seek(0)
    filename = file.name

    try:
        s3_client.upload_fileobj(
            file,
            s3_bucket_name,
            f"uploads/{filename}",
        )
        st.success("File Upload Complete")
    except Exception as e:
        st.error(f"Upload Error: {e}")

# Analysis section
st.header("Explore Metrics from wine_reviews Table")

@st.cache_resource
def get_connection():
    return pymysql.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB
    )

@st.cache_resource
def fetch_reviews():
    conn = get_connection()
    df = pd.read_sql("SELECT DISTINCT title, points, price, description, province FROM reviews", conn)
    conn.close()
    return df

try:
    df = fetch_reviews()

    if df.empty:
        st.warning("No records available in the database.")
    else:
        # Top 5 provinces
        st.subheader("Top 5 Most Frequent Provinces")
        top_provinces = df['province'].value_counts().head(5)
        st.dataframe(top_provinces.rename_axis("Province").reset_index(name="Count"))

        # Top 5 expensive wines
        st.subheader("Top 5 Most Expensive Wines")
        expensive_wines = df[['title', 'price']].dropna().sort_values(by='price', ascending=False).head(5)
        st.dataframe(expensive_wines.reset_index(drop=True))

        # Top 5 highest scoring wines
        st.subheader("Top 5 Highest Scoring Wines")
        top_scores = df[['title', 'points', 'description']].dropna(subset=['points']).sort_values(by='points', ascending=False).head(5)
        st.dataframe(top_scores.reset_index(drop=True))

except Exception as e:
    st.error(f"Database Error: {e}")
import streamlit as st
import fitz  # PyMuPDF
import nltk
import csv
import requests
from io import StringIO, BytesIO

# Ensure the punkt tokenizer is available
nltk.download('punkt')

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()  # Check that the request was successful
    return BytesIO(response.content)

def extract_text_from_pdf(pdf_stream):
    # Open the PDF file
    document = fitz.open(stream=pdf_stream, filetype="pdf")
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def split_into_sentences(text):
    # Use nltk to split the text into sentences
    sentences = nltk.sent_tokenize(text)
    return sentences

def write_sentences_to_csv(sentences):
    # Write sentences to a CSV in-memory and return as bytes
    output = StringIO()
    writer = csv.writer(output)
    for sentence in sentences:
        writer.writerow([sentence])
    output.seek(0)
    # Convert StringIO to bytes
    return output.getvalue().encode('utf-8')

def main():
    st.title("PDF Sentence Extractor")

    # Upload PDF or provide URL
    pdf_source = st.radio("Select PDF source:", ("Upload PDF", "PDF URL"))

    pdf_stream = None

    if pdf_source == "Upload PDF":
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            pdf_stream = BytesIO(uploaded_file.read())
    else:
        pdf_url = st.text_input("Enter PDF URL:")
        if pdf_url:
            try:
                pdf_stream = download_pdf(pdf_url)
                st.success("PDF downloaded successfully.")
            except Exception as e:
                st.error(f"Error downloading PDF: {e}")

    if pdf_stream:
        # Extract text from the PDF
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(pdf_stream)

        # Split the text into sentences
        with st.spinner("Splitting text into sentences..."):
            sentences = split_into_sentences(text)

        # Write sentences to CSV
        csv_data = write_sentences_to_csv(sentences)

        # Provide download link for the CSV file
        st.download_button(
            label="Download Sentences as CSV",
            data=csv_data,
            file_name="sentences.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()


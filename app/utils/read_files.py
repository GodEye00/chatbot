import gensim
import nltk
from gensim.models import ldamodel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import PyPDF2  # For PDF processing
import os

# Function to import text from a file
def import_text_from_file(file_path):
    """Imports text from a TXT or PDF file."""
    if file_path.endswith(".txt"):
        try:
            with open(file_path, "r") as file:
                text = file.read()
            return text
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return None
    elif file_path.endswith(".pdf"):
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    full_text += text
                return full_text
        except (PyPDF2.errors.PdfReadError, FileNotFoundError) as e:
            print(f"Error reading PDF file: {file_path}")
            print(f"Exception: {e}")
            return None
    else:
        print(f"Error: Unsupported file type: {file_path}")
        return None

# Function to import text from all TXT and PDF files in a directory
def import_text_from_directory(directory_path):
    """Imports text from all TXT and PDF files within a directory."""
    full_text = ""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                text = import_text_from_file(file_path)
                if text:
                    full_text += text + "\n"  # Add newline for separation
    return full_text

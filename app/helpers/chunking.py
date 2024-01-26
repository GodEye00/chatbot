# from gensim import models, corpora
# import nltk
# from gensim.models import ldamodel
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize

# import nltk  # For sentence tokenization
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
# from sklearn.cluster import KMeans
# import numpy as np
# import torch  # Required for Transformer models

# import numpy as np
# # from keras.preprocessing.text import Tokenizer
# from keras.preprocessing.sequence import pad_sequences
# import tensorflow as tf
# from keras import layers




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
        print(f"Root is: root", {root})
        for file in files:
            print(f"file is: file: %s" % file)
            if file.endswith(".txt") or file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                text = import_text_from_file(file_path)
                if text:
                    full_text += text + "\n"  # Add newline for separation
    return full_text




# Function for topic-aware chunking
def topic_aware_chunking(text, threshold=0.5):
    """Splits text into chunks based on topic shifts using a pre-trained LDA model."""
    print("About to chunk text: %s" % text)
    def preprocess_text(text):
        print("About to preprocess text")
        """Preprocesses text for LDA analysis:
        - Converts to lowercase
        - Tokenizes into words
        - Removes stop words
        """
        stop_words = set(stopwords.words("english"))  # Adjust stop words as needed
        tokens = word_tokenize(text.lower())
        filtered_tokens = [token for token in tokens if token not in stop_words]
        return filtered_tokens

    lda_model_path = AutoModel.from_pretrained("Gen-Sim/Gen-Sim", trust_remote_code=True)
    try:
        lda_model = models.LdaModel.load(lda_model_path)
    except FileNotFoundError:
        print("Error: LDA model file not found. Please provide a valid path or train a model.")
        return []

    chunks = []
    current_chunk = []
    current_topic = None

    for sentence in nltk.sent_tokenize(text):
        try:
            processed_sentence = preprocess_text(sentence)  # Assume this function is defined
            bow = corpora.Dictionary(processed_sentence)  # Convert to bag-of-words format
            topic_distribution = lda_model.get_document_topics(bow)[0]
            dominant_topic = topic_distribution[0][0]

            if current_topic is None or topic_distribution[0][1] < threshold:
                if current_chunk:  # Avoid appending empty chunks
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_topic = dominant_topic
            else:
                current_chunk.append(sentence)
        except Exception as e:
            print(f"Error processing sentence: {sentence}")
            print(f"Exception: {e}")

    if current_chunk:  # Append the last chunk if it's not empty
        chunks.append(' '.join(current_chunk))
    return chunks

docs = '../utils'
text = import_text_from_directory(docs)



topic_aware_chunking(text)

















# # Function for sentence-level chunking
# def transformer_based_chunking(text):# Load pre-trained model and tokenizer
#     model_name = "bert-base-uncased"  # Adjust based on your needs
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForSequenceClassification.from_pretrained(model_name)
#     sentences = nltk.sent_tokenize(text)  # Extract sentences
#     sentence_embeddings = []
#     for sentence in sentences:
#         encoded_sentence = tokenizer(sentence, return_tensors="pt")  # Tokenize and encode sentence
#         with torch.no_grad():  # Inference mode
#             output = model(**encoded_sentence)
#             embedding = output[1]  # Extract sentence embedding
#             sentence_embeddings.append(embedding.detach().numpy())

#     # Apply clustering (KMeans example)
#     clusters = KMeans(n_clusters=5).fit(sentence_embeddings).labels_  # Adjust cluster number

#     chunks = []
#     current_chunk = []
#     for sentence, cluster in zip(sentences, clusters):
#         if not current_chunk or cluster != clusters[-1]:
#             chunks.append(current_chunk)
#             current_chunk = [sentence]
#         else:
#             current_chunk.append(sentence)
#     chunks.append(current_chunk)  # Append last chunk
#     return chunks


# # Load pre-trained model and tokenizer
# model_name = "bert-base-uncased"  # Adjust based on your needs
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name)

# # Function for word-level chunking
# def word_transformer_based_chunking(text):
#     words = text.split()  # Simple word tokenization (adjust for complex cases)
#     word_embeddings = []
#     word_indices = []  # Keep track of word positions for chunk reconstruction
#     for i, word in enumerate(words):
#         encoded_word = tokenizer.encode(word, return_tensors="pt")  # Tokenize and encode word
#         with torch.no_grad():  # Inference mode
#             output = model(**encoded_word)
#             word_embedding = output[1].squeeze(0).detach().numpy()  # Extract word embedding
#             word_embeddings.append(word_embedding)
#             word_indices.append(i)  # Store word index

#     # Apply clustering (KMeans example)
#     clusters = KMeans(n_clusters=5).fit(word_embeddings).labels_  # Adjust cluster number

#     chunks = []
#     current_chunk_words = []
#     current_chunk_indices = []
#     for word_index, cluster in zip(word_indices, clusters):
#         if not current_chunk_words or cluster != clusters[-1]:
#             chunks.append(" ".join(current_chunk_words))  # Reconstruct chunk from words
#             current_chunk_words = []
#             current_chunk_indices = []
#         current_chunk_words.append(words[word_index])
#         current_chunk_indices.append(word_index)
#     chunks.append(" ".join(current_chunk_words))  # Append last chunk
#     return chunks





# def topic_aware_chunking_han(text, model, threshold=0.5):
#     # Define HAN model architecture
#     inputs = layers.Input(shape=(max_length,))
#     embedding = layers.Embedding(vocab_size, embedding_dim)(inputs)

#     # Word-level attention
#     word_encoder = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(embedding)
#     word_attention = layers.Attention()([word_encoder, word_encoder])

#     # Sentence-level attention
#     sentence_encoder = layers.Bidirectional(layers.LSTM(64))(word_attention)
#     sentence_attention = layers.Attention()([sentence_encoder, sentence_encoder])

#     # Output layer for chunk prediction (replace with your desired approach)
#     outputs = layers.Dense(num_topics, activation='softmax')(sentence_attention)
#     model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
#     chunks = []
#     current_chunk = []
#     current_topic = None

#     # Preprocess text:
#     tokenizer = Tokenizer()
#     tokenizer.fit_on_texts([text])
#     word_indices = tokenizer.texts_to_sequences([text])[0]
#     padded_sequences = pad_sequences([word_indices], maxlen=max_length)

#     # Obtain sentence-level topic predictions:
#     sentence_topic_predictions = model.predict(padded_sequences)[0]

#     # Chunk segmentation based on topic shifts:
#     for i, sentence in enumerate(text.split("\n")):
#         dominant_topic = np.argmax(sentence_topic_predictions[i])

#         if current_topic is None or sentence_topic_predictions[i][dominant_topic] < threshold:
#             chunks.append(current_chunk)
#             current_chunk = [sentence]
#             current_topic = dominant_topic
#         else:
#             current_chunk.append(sentence)

#     chunks.append(current_chunk)  # Append the last chunk
#     return chunks



# def crnn_chunking(text, model):


#     def preprocess_text_and_get_embeddings(text):
#         # Replace with your preprocessing logic to obtain word embeddings
#         # Example:
#         word_embeddings = []  # Assuming you have a word embedding model
#         for word in text.split():
#             word_embedding = word_embedding_model.get_embedding(word)
#             word_embeddings.append(word_embedding)
#         return np.array(word_embeddings)

#     # Define CRNN model architecture
#     inputs = layers.Input(shape=(max_length, feature_dim))  # Input shape for word embeddings

#     # Convolutional layers for local feature extraction
#     conv1 = layers.Conv1D(filters=64, kernel_size=3, activation='relu')(inputs)
#     pool1 = layers.MaxPooling1D(pool_size=2)(conv1)
#     conv2 = layers.Conv1D(filters=128, kernel_size=3, activation='relu')(pool1)
#     pool2 = layers.MaxPooling1D(pool_size=2)(conv2)

#     # Flatten and pass to RNN
#     flat = layers.Flatten()(pool2)
#     rnn = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(flat)

#     # Output layer for chunk prediction (replace with your desired approach)
#     outputs = layers.Dense(num_chunks, activation='softmax')(rnn)
#     model = tf.keras.Model(inputs=inputs, outputs=outputs)

#     word_embeddings = preprocess_text_and_get_embeddings(text)
#     predictions = model.predict(word_embeddings)

#     chunks = []
#     current_chunk = []
#     previous_chunk = None
#     for i, prediction in enumerate(predictions[0]):
#         predicted_chunk = np.argmax(prediction)
#         if i == 0 or predicted_chunk != previous_chunk:
#             chunks.append(current_chunk)
#             current_chunk = []
#         current_chunk.append(text.split()[i])
#         previous_chunk = predicted_chunk
#     chunks.append(current_chunk)
#     return chunks

# # Example usage (assuming model is trained)
# text = "... (Your text here) ..."
# chunks = crnn_chunking(text, model)
# print(chunks)




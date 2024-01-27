from flask import current_app
from gensim import models
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertModel
from sklearn.cluster import KMeans
import torch
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Function for topic-aware chunking
def topic_aware_chunking(text, threshold=0.1):
    """Splits text into chunks based on topic shifts using a pre-trained LDA model."""
    current_app.logger.info(f"About to chunk text: {text}")

    def preprocess_text(text):
        """Preprocesses text for LDA analysis:
        - Converts to lowercase
        - Tokenizes into words
        - Removes stop words
        """
        current_app.logger.info("About to preprocess text")
        stop_words = set(stopwords.words("english"))  # Adjust stop words as needed
        tokens = word_tokenize(text.lower())
        filtered_tokens = [token for token in tokens if token not in stop_words]
        return filtered_tokens

    # Create a dictionary and corpus for LDA model
    common_dictionary = Dictionary(common_texts)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]

    # Train the LDA model on the corpus
    lda_model = models.LdaModel(common_corpus, num_topics=10)

    chunks = []
    current_chunk = []
    current_topic = None

    for sentence in nltk.sent_tokenize(text):
        try:
            processed_sentence = preprocess_text(sentence)
            bow = common_dictionary.doc2bow(processed_sentence)
            topic_distribution = lda_model.get_document_topics(bow)
            if not topic_distribution:
                continue  # Skip sentences where LDA can't assign topic (e.g., no content after preprocessing)
            dominant_topic = topic_distribution[0][0]

            if current_topic is None or topic_distribution[0][1] < threshold:
                if current_chunk:  # Avoid appending empty chunks
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_topic = dominant_topic
            else:
                current_chunk.append(sentence)
        except Exception as e:
            current_app.logger.exception(f"Error processing sentence: {sentence}")
            current_app.logger.exception(f"Exception: {e}")

    if current_chunk:  # Append the last chunk if it's not empty
        chunks.append(current_chunk)

    return chunks



#  Using transformers for chunking
    #  "bert-base-uncased"
    # gpt2
    # distilbert-base-uncased
    # roberta-base
    # t5-small
    # xlnet-base-cased
    # bert-large-uncased
def transformer_based_chunking(text, max_length=512):
    model_name = "bert-base-uncased"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)

    # Split the text into tokens and then into chunks of max_length tokens
    tokenized_text = tokenizer.tokenize(text)
    token_chunks = [tokenized_text[i:i + max_length] for i in range(0, len(tokenized_text), max_length)]

    sentence_embeddings = []
    for chunk in token_chunks:
        # Convert tokens to their IDs and pad if necessary
        encoded_chunk = tokenizer.convert_tokens_to_ids(chunk)
        encoded_chunk = torch.tensor([encoded_chunk])  # Convert to PyTorch tensors
        with torch.no_grad():  # Inference mode
            output = model(encoded_chunk)
            hidden_states = output.last_hidden_state
            # Extract embeddings (e.g., mean pooling)
            sentence_embedding = torch.mean(hidden_states, dim=1).squeeze()
            sentence_embeddings.append(sentence_embedding.numpy())

    # Apply clustering (KMeans example)
    clusters = KMeans(n_clusters=5).fit(sentence_embeddings).labels_  # Adjust cluster number as needed

    # Reconstruct chunks based on clustering
    chunks = []
    current_chunk = []
    for chunk, cluster in zip(token_chunks, clusters):
        sentences = nltk.sent_tokenize(tokenizer.convert_tokens_to_string(chunk))
        if not current_chunk or cluster != clusters[-1]:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentences
        else:
            current_chunk.extend(sentences)
    if current_chunk:
        chunks.append(current_chunk)  # Append last chunk

    return chunks

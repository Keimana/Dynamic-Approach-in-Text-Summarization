import re
import logging
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from rouge import Rouge
from bert_score import score
import torch
from transformers import BertTokenizer, BertModel 
from collections import Counter
import spacy

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewAlgorithmProcessor:
    def __init__(self):
        self.fileContent = ""  # Title
        self.bodyContent = ""  # Body of the article
        self.memo = {}  # Memoization for sentence scores
        self.word_freq_cache = {}  # Cache for word frequencies
        self.generated_summary = ""  # Summary
        self.original_text = ''  # For ROUGE score calculation
        self.rouge = Rouge()  # ROUGE instance
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # BERT tokenizer
        self.model = BertModel.from_pretrained('bert-base-uncased')  # BERT model
        self.nlp = spacy.load("en_core_web_sm")  # Load the English NLP model

        # Metadata attributes
        self.author = ""
        self.literature = ""
        self.date = ""

    def set_content(self, content):
        """Sets the file content and extracts the title and body from the content."""
        try:
            lines = content.strip().split('\n')
            self.fileContent = lines[0]  # First line is the title
            self.bodyContent = self.clean_body_content('\n'.join(lines[1:]))  
            self.extract_metadata(content)  # Extract metadata if needed
        except Exception as e:
            logging.error(f"Error setting content: {e}")

    def clean_body_content(self, body_content):
        """Cleans the body content by removing author, genre, and date information.""" 
        body_content = re.sub(r'^by\s*.+?\n', '', body_content)
        body_content = re.sub(r'^[A-Z\s]+\|[A-Z\s]+\s+\d{1,2},?\s+\d{4}\n', '', body_content)
        return body_content.strip()

    def set_original_text(self, original_text):
        """Sets the original text for ROUGE score calculation.""" 
        try:
            if original_text.strip():
                self.original_text = original_text.strip()
            else:
                raise ValueError("Original text cannot be empty.")
        except Exception as e:
            logging.error(f"Error setting original text: {e}")

    def extract_metadata(self, text):
        """Extracts author, literature, and date from the provided text.""" 
        try:
            author_match = re.search(r'by\s*(.+?)(?:\s+\|)', text)
            literature_match = re.search(r'(\w+)\s*\|\s*(\w+)', text)
            date_match = re.search(r'\| (\w+ \d{1,2}(?:, \d{4})?)', text)

            if author_match:
                self.author = author_match.group(1).strip()
            if literature_match:
                self.literature = literature_match.group(1).strip()
            if date_match:
                self.date = date_match.group(1).strip()
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")

    def reset_caches(self):
        """Reset memoization and word frequency cache.""" 
        self.memo = {}
        self.word_freq_cache = {}

    def get_title(self):
        """Returns the title of the current content.""" 
        return self.fileContent

    def get_body(self):
        """Returns the body of the current content.""" 
        return self.bodyContent

    def get_author(self):
        """Returns the author of the current content.""" 
        return self.author

    def get_literature(self):
        """Returns the literature of the current content.""" 
        return self.literature

    def get_date(self):
        """Returns the date of the current content.""" 
        return self.date

    def tokenize_sentences(self, text):
        """Improved tokenization that handles punctuation and various sentence structures more robustly."""
        sentences = re.split(r'(?<=[.!?]) +', text)
        return [s.strip() for s in sentences if s]  # Clean up any empty strings

    def tokenize_words(self, text):
        """Tokenizes text into words using regex.""" 
        return re.findall(r'\b\w+\b', text.lower())

    def normalize_text(self, text):
        """Normalize the text by removing unnecessary elements and applying additional normalization techniques."""
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\d+', '', text)  # Remove numbers
        text = re.sub(r'[\u2022•●-]', '', text)  # Remove bullet points
        text = re.sub(r'[+:]', '', text)  # Remove plus signs and colons
        text = re.sub(r'\s+[,.|;?!]', lambda match: match.group(0).strip(), text)  # Remove space before punctuation
        text = re.sub(r'(?<!\w)\s+', ' ', text)  # Remove extra spaces
        text = re.sub(r'\s+\(', '(', text)  # Remove space before '('
        text = re.sub(r'\)\s+', ') ', text)  # Space after ')'
        text = re.sub(r'\(\s+', '(', text)  # Remove space after '('
        text = re.sub(r'\s+\)', ')', text)  # Remove space before ')'
        
        # Remove date patterns more comprehensively
        text = re.sub(r'\b(?:\w+\s*\d{1,2}(?:, \d{4})?|(?:\d{1,2}(?:st|nd|rd|th)?\s+\w+)(?:, \d{4})?)\b', '', text, flags=re.IGNORECASE)
        
        text = re.sub(r'\b(?:author|fiction|non-fiction|fictional|narrative)\b', '', text, flags=re.IGNORECASE)  # Remove author and fiction/non-fiction
        text = text.lower().strip()  # Lowercase and trim whitespace
        text = re.sub(r'^\s*(?=\w)', '', text, flags=re.MULTILINE)  # Trim leading whitespace from each line
        text = re.sub(r'\n+', ' ', text)  # Combine lines

        # Ensure sentences end with a period where applicable
        sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
        normalized_sentences = [sentence.strip() + ('.' if not sentence.endswith('.') else '') for sentence in sentences if sentence]

        return ' '.join(normalized_sentences)

    def get_word_frequencies(self):
        """Calculates word frequencies and caches the result.""" 
        if not self.word_freq_cache:
            words = self.tokenize_words(self.bodyContent)
            freq_dist = Counter(words)
            max_frequency = max(freq_dist.values(), default=1)
            self.word_freq_cache = {word: freq / max_frequency for word, freq in freq_dist.items()}
        return self.word_freq_cache

    def get_sentence_score(self, sentence, freq_dist):
        """Returns the score of a sentence based on word frequency, using memoization.""" 
        if sentence in self.memo:
            return self.memo[sentence]
        
        words = self.tokenize_words(sentence)
        score = sum(freq_dist.get(word, 0) for word in words)
        self.memo[sentence] = score
        return score

    def segment_text_into_chunks(self, text, chunk_size):
        """Segments text with overlapping content between chunks.""" 
        sentences = self.tokenize_sentences(text)
        chunks, current_chunk = [], []

        for sentence in sentences:
            current_chunk.append(sentence)
            if sum(len(s) for s in current_chunk) > chunk_size:
                chunks.append(' '.join(current_chunk[:-1]))  # Remove last sentence to overlap
                current_chunk = [current_chunk[-1]]  # Start a new chunk with the last sentence

        if current_chunk:
            chunks.append(' '.join(current_chunk))  # Append any remaining sentences as the last chunk
        return chunks

    def clean_summary_formatting(self, summary):
        """Cleans the formatting of the generated summary to ensure readability."""
        # Remove extra spaces before punctuation and ensure proper spacing
        summary = re.sub(r'\s+([,.|;?!])', r'\1', summary)  # Remove space before punctuation
        summary = re.sub(r'([,.|;?!])\s+', r'\1 ', summary)  # Ensure single space after punctuation
        summary = re.sub(r'\s+', ' ', summary)  # Replace multiple spaces with a single space
        summary = summary.strip()  # Trim leading and trailing whitespace
        
        return summary

    def generate_summary(self, percentage_top=0.3):
        """Generate a summary with dynamically adjusted threshold and semantic similarity in the third person."""
        try:
            if not self.bodyContent:
                raise ValueError("No content available to summarize.")

            # Normalize and tokenize body content
            normalized_body = self.normalize_text(self.bodyContent)

            # Segment the normalized body into chunks for processing
            chunks = self.segment_text_into_chunks(normalized_body, chunk_size=512)  # Adjust chunk_size as necessary

            all_sentence_scores = []
            for chunk in chunks:
                sentences = self.tokenize_sentences(chunk)
                # Compute word frequencies and semantic embeddings
                freq_dist = self.get_word_frequencies()
                doc_embedding = self.compute_doc_embedding(chunk)

                # Calculate scores for sentences in the current chunk
                for sentence in sentences:
                    score = self.get_sentence_score(sentence, freq_dist)
                    similarity_score = self.get_semantic_similarity(sentence, doc_embedding)
                    total_score = score + similarity_score
                    all_sentence_scores.append((sentence, total_score))

            # Sort by score and select top percentage
            all_sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_n = int(len(all_sentence_scores) * percentage_top)
            top_sentences = [sentence for sentence, _ in all_sentence_scores[:top_n]]

            # Combine top sentences in original order for coherence
            combined_summary = ' '.join(top_sentences)
            
            # Convert to third-person before evaluation
            self.generated_summary = self.convert_to_third_person(combined_summary)
            
            # Clean the summary formatting
            self.generated_summary = self.clean_summary_formatting(self.generated_summary)
            
            # Normalize parentheses in the summary
            self.generated_summary = self.normalize_text(self.generated_summary)

            return self.generated_summary

        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return "An error occurred while generating the summary."






    def convert_to_third_person(self, summary):
        """Converts the summary to third-person point of view using spaCy."""
        doc = self.nlp(summary)

        # Create a list to store the modified tokens
        modified_tokens = []

        for token in doc:
            # Replace first-person pronouns with "the person"
            if token.text.lower() in ["i", "my", "mine", "me"]:
                modified_tokens.append("the person")
            # Replace second-person pronouns with "the reader"
            elif token.text.lower() in ["you", "your", "yours"]:
                modified_tokens.append("the reader")
            # Replace plural first-person pronouns with "they"
            elif token.text.lower() in ["we", "our", "us"]:
                modified_tokens.append("they")
            # Replace references to "author" with "the character"
            elif token.text.lower() == "author":
                modified_tokens.append("the character")
            else:
                modified_tokens.append(token.text)

        # Join the modified tokens into a single string
        return ' '.join(modified_tokens)


    def compute_doc_embedding(self, text):
        """Computes the document embedding for semantic analysis using BERT."""
        tokens = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)

        # Log the number of tokens generated
        num_tokens = tokens['input_ids'].shape[1]
        logging.info(f"Number of tokens: {num_tokens}")

        if num_tokens > 512:
            logging.warning(f"Input text exceeds token limit. Truncating from {num_tokens} to 512 tokens.")

        with torch.no_grad():
            embeddings = self.model(**tokens)

        return embeddings.last_hidden_state.mean(dim=1)


    def get_semantic_similarity(self, sentence, doc_embedding):
        """Calculates the semantic similarity of a sentence to the document embedding.""" 
        sentence_embedding = self.compute_doc_embedding(sentence)
        cosine_similarity = torch.cosine_similarity(sentence_embedding, doc_embedding)
        return cosine_similarity.item()  # Convert to a Python float

    def get_rouge_scores(self, decimal_places=3):
        """Calculates and returns the ROUGE scores between the generated summary and the original text."""
        if not self.original_text:
            raise ValueError("Original text is empty. Please set the original text before calculating ROUGE scores.")

        # Calculate ROUGE scores
        scores = self.rouge.get_scores(self.generated_summary, self.original_text)

        # Round the scores to the specified number of decimal places
        for score in scores:
            for metric, values in score.items():
                values['p'] = round(values['p'], decimal_places)  # Precision
                values['r'] = round(values['r'], decimal_places)  # Recall
                values['f'] = round(values['f'], decimal_places)  # F1 score

        return scores

    def calculate_bertscore(self, generated_summary, reference_summary):
        """Calculates BERTScore for generated summary against a reference summary."""
        P, R, F1 = score([generated_summary], [reference_summary], lang='en', verbose=True)
        return {
            'precision': P.mean().item(),
            'recall': R.mean().item(),
            'f1': F1.mean().item()
        }
    
    def compression_ratio(self, original_text, summary):
        return len(summary) / len(original_text)
    
    def semantic_correlation(self, sentence_a, sentence_b):
        """Calculates semantic correlation between two sentences using BERT embeddings."""
        
        # Tokenize inputs with truncation and padding
        inputs_a = self.tokenizer(sentence_a, return_tensors='pt', truncation=True, padding=True, max_length=512)
        inputs_b = self.tokenizer(sentence_b, return_tensors='pt', truncation=True, padding=True, max_length=512)

        # Log the tokenized shapes
        print(f"Input A shape: {inputs_a['input_ids'].shape}, tokens: {inputs_a['input_ids']}")
        print(f"Input B shape: {inputs_b['input_ids'].shape}, tokens: {inputs_b['input_ids']}")

        # Get embeddings without gradients
        with torch.no_grad():
            embedding_a = self.model(**inputs_a).last_hidden_state.mean(dim=1)
            embedding_b = self.model(**inputs_b).last_hidden_state.mean(dim=1)

        # Log the shapes of embeddings
        print(f"Embedding A shape: {embedding_a.shape}")
        print(f"Embedding B shape: {embedding_b.shape}")

        # Check for dimension compatibility before calculating cosine similarity
        if embedding_a.shape != embedding_b.shape:
            print("Error: Embedding shapes do not match!")
            print(f"Embedding A: {embedding_a.shape}, Embedding B: {embedding_b.shape}")
            return None  # Or handle the error as needed

        # Calculate cosine similarity
        similarity = torch.nn.functional.cosine_similarity(embedding_a, embedding_b)
        return similarity.item()



    
    def calculate_reference_free_score(self, summary):
        """Calculates a reference-free score for the generated summary."""
        self.generated_summary = summary  # Set the generated summary
        if self.original_text and self.generated_summary:
            sem_corr = self.semantic_correlation(self.original_text, self.generated_summary)
            comp_ratio = self.compression_ratio(self.original_text, self.generated_summary)
            # Combine the metrics, adjust the weights as needed
            alpha = 0.5
            final_score = (sem_corr ** alpha) * (comp_ratio ** (1 - alpha))
            return final_score
        return None

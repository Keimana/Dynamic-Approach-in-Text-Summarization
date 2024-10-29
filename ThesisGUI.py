import heapq
import re
import logging
import time
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from rouge import Rouge
from bert_score import score
import torch
from transformers import BertTokenizer, BertModel 

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewAlgorithmProcessor:
    def __init__(self):
        self.fileContent = ""  # This will store the title
        self.bodyContent = ""  # This will store the body of the article
        self.memo = {}  # Memoization table to store sentence scores
        self.word_freq_cache = {}  # Cache for word frequencies
        self.generated_summary = ""  # Initialize generated summary attribute
        self.original_text = ''  # Initialize original_text
        self.rouge = Rouge()  # Initialize Rouge instance for ROUGE score calculation
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Use the BERT tokenizer
        self.model = BertModel.from_pretrained('bert-base-uncased')  # Use the BERT model
        
        # New attributes for author, genre, and date
        self.author = ""
        self.genre = ""
        self.date = ""

    def set_content(self, content):
        """Sets the file content and extracts the title and body from the content."""
        # Split the content into title and body (assuming a specific format)
        try:
            lines = content.strip().split('\n')
            self.fileContent = lines[0]  # Assuming the first line is the title
            self.bodyContent = '\n'.join(lines[1:])  # The rest is the body
            self.extract_metadata(content)  # Extract author, genre, and date if needed
        except Exception as e:
            logging.error(f"Error setting content: {e}")

    def set_original_text(self, original_text):
        """Sets the original text for ROUGE score calculation."""
        try:
            if original_text.strip():  # Ensure the original text is not empty
                self.original_text = original_text.strip()
            else:
                raise ValueError("Original text cannot be empty.")
        except Exception as e:
            logging.error(f"Error setting original text: {e}")

    def extract_metadata(self, text):
        """Extracts author, genre, and date from the provided text."""
        try:
            author_match = re.search(r'by\s*(.+?)(?:\s+\|)', text)
            genre_match = re.search(r'(\w+)\s*\|\s*(\w+)', text)
            date_match = re.search(r'\| (\w+ \d{1,2}(?:, \d{4})?)', text)

            if author_match:
                self.author = author_match.group(1).strip()
            if genre_match:
                self.genre = genre_match.group(1).strip()
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

    def get_genre(self):
        """Returns the genre of the current content."""
        return self.genre

    def get_date(self):
        """Returns the date of the current content."""
        return self.date

    def tokenize_sentences(self, text):
        """Tokenizes text into sentences using NLTK's sent_tokenize."""
        return sent_tokenize(text)

    def tokenize_words(self, text):
        """Tokenizes text into words using NLTK's word_tokenize."""
        return word_tokenize(text.lower())

    def normalize_text(self, text):
        """Normalize the text by removing unnecessary elements."""
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\d+', '', text)  # Remove numbers
        text = re.sub(r'[\u2022•●-]', '', text)  # Remove bullet points
        text = re.sub(r'[+:]', '', text)  # Remove plus signs and colons
        return text.strip()

    def get_word_frequencies(self):
        """Calculates word frequencies and caches the result."""
        if not self.word_freq_cache:  # If cache is empty, calculate frequencies
            words = self.tokenize_words(self.bodyContent)
            freq_dist = FreqDist(words)
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
        """Segments text into manageable chunks."""
        sentences = self.tokenize_sentences(text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if sum(len(s) for s in current_chunk) > chunk_size:
                chunks.append(' '.join(current_chunk[:-1])) 
                current_chunk = [current_chunk[-1]]

        if current_chunk: 
            chunks.append(' '.join(current_chunk))
        return chunks

    def generate_summary(self, num_sentences=5, chunk_size=1000):
        """Generates a summary by selecting the top sentences based on their scores."""
        try:
            if not self.bodyContent:
                raise ValueError("No content available to summarize.")

            normalized_body = self.normalize_text(self.bodyContent)
            chunks = self.segment_text_into_chunks(normalized_body, chunk_size)

            summaries = []

            for chunk in chunks:
                sentences = self.tokenize_sentences(chunk) 
                freq_dist = self.get_word_frequencies()

                sentence_scores = {sentence: self.get_sentence_score(sentence, freq_dist) for sentence in sentences}

                # Pruning: discard sentences with low scores compared to the best-known score
                best_known_score = max(sentence_scores.values(), default=0)
                filtered_sentences = {s: score for s, score in sentence_scores.items() if score >= best_known_score * 0.5}

                # Get the top N sentences based on their scores
                top_sentences = heapq.nlargest(num_sentences, filtered_sentences, key=filtered_sentences.get)
                summaries.append(' '.join(top_sentences))

            final_summary = ' '.join(summaries)
            self.generated_summary = self.format_summary(final_summary)  # Store the summary
            return self.format_output()  # Return the formatted output including metadata
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return "An error occurred while generating the summary."

    def format_summary(self, summary):
        """Formats the summary by removing unnecessary elements."""
        formatted_summary = []
        lines = summary.splitlines()
        
        for line in lines:
            line = line.strip()  # Remove leading and trailing spaces
            # Skip empty lines
            if line:
                formatted_summary.append(line)
        
        return "\n".join(formatted_summary)

    def format_output(self):
        """Formats the output to include the summary, author, genre, and date."""
        output = f"Title: {self.fileContent}\n"
        output += f"Author: {self.author}\n"
        output += f"Genre: {self.genre}\n"
        output += f"Date: {self.date}\n"
        output += f"Summary:\n{self.generated_summary}"
        return output
    
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

    def print_summary(self):
        """Print the generated summary."""
        try:
            print(self.format_output())
        except Exception as e:
            logging.error(f"Error printing summary: {e}")

    def __str__(self):
        return f"NewAlgorithmProcessor(title={self.fileContent}, author={self.author}, genre={self.genre}, date={self.date})"

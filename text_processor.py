import re
from collections import Counter
from rouge import Rouge
from transformers import BertTokenizer, BertModel  # Import the tokenizer and model
from bert_score import score  # Import the BERTScore function
import torch

class TextProcessor:
    def __init__(self):
        self.fileContent = ''
        self.memo = {}  # Memoization table to store sentence scores
        self.table = []  # Table for Bottom-Up approach
        self.title = ''  # Title attribute
        self.character_list = []  # List to store characters found
        self.original_text = ''  # Initialize original_text
        self.generated_summary = ''  # Initialize generated_summary
        self.rouge = Rouge()  # Initialize Rouge instance for ROUGE score calculation
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Use the BERT tokenizer
        self.model = BertModel.from_pretrained('bert-base-uncased')  # Use the BERT model

    def set_content(self, content, title=''):
        """Sets the content of the text processor and optionally a title."""
        self.fileContent = content
        self.memo = {}  # Reset memoization table
        self.table = []  # Reset table for Bottom-Up approach
        self.title = title  # Set the title
        self.character_list = self.extract_characters()  # Extract characters and update the list
        self.set_original_text(content)  # Set original text for ROUGE calculation

    def get_content(self):
        """Returns the current content of the text processor."""
        return self.fileContent

    def extract_characters(self):
        """Extracts character names from the file content."""
        characters = re.findall(r'\b[A-Z][a-z]*\b', self.fileContent)
        return list(set(characters))  # Remove duplicates

    def get_characters(self):
        """Returns the list of extracted characters."""
        return self.character_list

    def tokenize_sentences(self, text):
        """Splits text into sentences using regular expressions."""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def tokenize_words(self, text):
        """Splits text into words using regular expressions."""
        return re.findall(r'\w+', text.lower())

    def get_word_frequencies(self):
        """Calculates word frequencies and normalizes them."""
        words = self.tokenize_words(self.fileContent)
        word_frequencies = Counter(words)
        max_frequency = max(word_frequencies.values(), default=1)
        return {word: freq / max_frequency for word, freq in word_frequencies.items()}

    def get_sentence_score(self, sentence, freq_dist):
        """Returns the score of a sentence based on word frequency, using memoization."""
        if sentence in self.memo:
            return self.memo[sentence]  # Return pre-computed score
        
        words = self.tokenize_words(sentence)
        score = sum(freq_dist.get(word, 0) for word in words)
        self.memo[sentence] = score  # Store computed score
        return score

    def generate_summary_top_down(self):
        """Generates a summary using a Top-Down approach (memoization)."""
        if not self.fileContent:
            return "No content available to summarize."
        
        sentences = self.tokenize_sentences(self.fileContent)
        freq_dist = self.get_word_frequencies()

        # Score all sentences and sort them
        sentence_scores = {sentence: self.get_sentence_score(sentence, freq_dist) for sentence in sentences}
        summarized_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)

        # Limit the summary to a specific number of sentences if needed (e.g., top 3)
        top_n_sentences = 3
        self.generated_summary = ' '.join(summarized_sentences[:top_n_sentences])  # Store the generated summary
        return self.generated_summary

    def generate_summary_bottom_up(self):
        """Generates a summary using a Bottom-Up approach (tabulation)."""
        if not self.fileContent:
            return "No content available to summarize."

        sentences = self.tokenize_sentences(self.fileContent)
        freq_dist = self.get_word_frequencies()
        num_sentences = len(sentences)

        # Define a table for storing scores
        self.table = [0] * num_sentences
        
        # Fill the table with sentence scores
        for i in range(num_sentences):
            self.table[i] = self.get_sentence_score(sentences[i], freq_dist)

        # Create a list of (score, sentence) pairs and sort
        scored_sentences = sorted([(self.table[i], sentences[i]) for i in range(num_sentences)], reverse=True)

        # Get top N sentences
        top_n_sentences = 3
        self.generated_summary = ' '.join(sentence for score, sentence in scored_sentences[:top_n_sentences])
        return self.generated_summary

    def set_original_text(self, original_text):
        """Set the original text for ROUGE score calculation."""
        self.original_text = original_text

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

    def word_count(self):
        """Calculates and returns the word count of the file content."""
        return len(self.tokenize_words(self.fileContent))

    def summarized_word_count(self):
        """Calculates and returns the word count of the summarized content."""
        summary = self.generate_summary_top_down()  # You can also call generate_summary_bottom_up
        return len(self.tokenize_words(summary))

    def get_reference_summary(self):
        """Returns the original text as the reference summary."""
        return self.original_text
    
    def get_rouge_scores(self, decimal_places=3):
        if not self.original_text:
            raise ValueError("Original text is empty. Please set the original text before calculating ROUGE scores.")

        scores = self.rouge.get_scores(self.generated_summary, self.original_text)

        for score in scores:
            for metric, values in score.items():
                values['p'] = round(values['p'], decimal_places)
                values['r'] = round(values['r'], decimal_places)
                values['f'] = round(values['f'], decimal_places)

        return scores

    def calculate_bertscore(self, generated_summary, reference_summary):
        P, R, F1 = score([generated_summary], [reference_summary], lang='en', verbose=True)
        return {
            'precision': P.mean().item(),
            'recall': R.mean().item(),
            'f1': F1.mean().item()
        }
    
    def semantic_correlation(self, sentence_a, sentence_b):
        inputs_a = self.tokenizer(sentence_a, return_tensors='pt', truncation=True, padding=True, max_length=512)
        inputs_b = self.tokenizer(sentence_b, return_tensors='pt', truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            embedding_a = self.model(**inputs_a).last_hidden_state.mean(dim=1)
            embedding_b = self.model(**inputs_b).last_hidden_state.mean(dim=1)

        if embedding_a.shape != embedding_b.shape:
            print("Error: Embedding shapes do not match!")
            return 0.0

        similarity = torch.nn.functional.cosine_similarity(embedding_a, embedding_b)
        return similarity.item()

    def compression_ratio(self, original_text, summary):
        return len(summary) / len(original_text)

    def calculate_reference_free_score(self, summary):
        self.generated_summary = summary
        if self.original_text and self.generated_summary:
            sem_corr = self.semantic_correlation(self.original_text, self.generated_summary)
            comp_ratio = self.compression_ratio(self.original_text, self.generated_summary)
            alpha = 0.5
            final_score = (sem_corr ** alpha) * (comp_ratio ** (1 - alpha))
            return final_score
        return None

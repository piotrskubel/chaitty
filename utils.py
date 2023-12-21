import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import time

class LanguageModel:
    def __init__(self, endpoint, headers, data):
        self.endpoint = endpoint
        self.headers = headers
        self.data = data

    def get_response(self, json_data=True):
        """Send a POST request to the endpoint and return the response."""
        if json_data:
            response = requests.post(self.endpoint, headers=self.headers, json=self.data)
        else:
            response = requests.post(self.endpoint, headers=self.headers, data=self.data)

        if response.status_code != 200:
            raise Exception(f'''HTTP request failed with status code {response.status_code}.
Responsible endpoint: {self.endpoint}
{response.json()}''')

        return response
    
class TextSimilarity:
    def __init__(self, elements_in_context=5):
        self.vectorizer = TfidfVectorizer()
        self.elements_in_context = elements_in_context

    def prepare_context(self, filepath, text):
        """Preparing a context for LLM"""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Exclude lines that end with a question mark or are identical to the input text
        lines = [line for line in lines if not line.strip().endswith('?') 
                 and line.strip() != f'User: {text}' and line.strip() != f'Assistant: {text}']

        # If there are less than elements_in_context lines, return all lines
        if len(lines) < self.elements_in_context + 1:
            return [line.strip() for line in lines]

        tfidf_matrix = self.vectorizer.fit_transform(lines + [text])
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix).flatten()

        num_items = min(self.elements_in_context + 1, len(lines))
        top_indices = heapq.nlargest(num_items, range(len(similarity_scores)-1), similarity_scores.take)

        if num_items == self.elements_in_context + 1:
            top_indices = top_indices[1:]

        return [lines[i].strip() for i in top_indices]

def write_to_file(filepath, text):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(text + '\n')

def countdown(n):
    for i in range(n, 0, -1):
        print(i)
        time.sleep(1)

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
        try:
            if json_data:
                response = requests.post(self.endpoint, timeout=10, headers=self.headers, json=self.data)
            else:
                response = requests.post(self.endpoint, timeout=10, headers=self.headers, data=self.data)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            print(f"Timeout occurred. {e}")
            raise e
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            raise http_err

        return response
    

class TextSimilarity:
    def __init__(self, elements_in_context=10):
        self.vectorizer = TfidfVectorizer()
        self.elements_in_context = elements_in_context

    def prepare_context(self, filepath, text):
        """Preparing a context for LLM"""
        with open(filepath, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()

        unique_lines = list(dict.fromkeys(file_lines))

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(unique_lines)

        if len(unique_lines) < self.elements_in_context:
            return [line.strip() for line in unique_lines]

        tfidf_matrix = self.vectorizer.fit_transform(unique_lines + [text])
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix).flatten()

        top_indices = heapq.nlargest(self.elements_in_context, range(len(similarity_scores)-1), similarity_scores.take)
        top_lines = [unique_lines[i].strip() for i in top_indices]

        return top_lines


def write_to_file(filepath, text):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(text + '\n')

def countdown(n):
    for i in range(n, 0, -1):
        print(i)
        time.sleep(1)

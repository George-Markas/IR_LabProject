from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from typing import List

class TextProcessor:
    """Handles text preprocessing"""

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def process(self, text: str) -> List[str]:
        # Convert to lowercase and tokenize
        tokens = word_tokenize(text.lower())

        # Remove non-alphanumeric tokens and stopwords
        tokens = [token for token in tokens
                  if token.isalnum() and token not in self.stop_words]

        # Stem tokens
        tokens = [self.stemmer.stem(token) for token in tokens]

        return tokens
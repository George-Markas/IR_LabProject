import nltk
from nltk.corpus import reuters
from pathlib import Path

DATA_DIR = Path.joinpath(Path(__file__).parent.parent.parent, "./nltk_data")

nltk.data.path.append(DATA_DIR)

def download_datasets():
    try:
        reuters.fileids()
    except LookupError:
        nltk.download('reuters', download_dir=DATA_DIR)
        nltk.download('punkt', download_dir=DATA_DIR)
        nltk.download('stopwords', download_dir=DATA_DIR)
        nltk.download('punkt_tab', download_dir=DATA_DIR)
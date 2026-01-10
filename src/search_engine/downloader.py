import nltk
import kagglehub
from nltk.corpus import reuters


def download_datasets() -> str:
    # Download Reuters
    try:
        reuters.fileids()
    except LookupError:
        nltk.download('reuters')
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab')

    # Download CISI
    return kagglehub.dataset_download("dmaso01dsta/cisi-a-dataset-for-information-retrieval")

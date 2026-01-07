import nltk
import kagglehub
from nltk.corpus import reuters
from pathlib import Path

nltk_dir = Path.joinpath(Path(__file__).parent.parent.parent, "./nltk_data")

nltk.data.path.append(nltk_dir)

def download_datasets():
    # Download Reuters
    try:
        reuters.fileids()
    except LookupError:
        nltk.download('reuters', download_dir=nltk_dir)
        nltk.download('punkt', download_dir=nltk_dir)
        nltk.download('stopwords', download_dir=nltk_dir)
        nltk.download('punkt_tab', download_dir=nltk_dir)

    # Download CISI
    kagglehub.dataset_download("dmaso01dsta/cisi-a-dataset-for-information-retrieval")

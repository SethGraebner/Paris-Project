from xgboost import XGBClassifier
from type_utils import UnprocessedData
from DataLoaders import AbstractDataLoader, GPTCleanedLoader
from Vectorizers import AbstractVectorizer, AdaVectorizer
from tqdm import tqdm
from lxml import etree
import os


DATA_PATH: str = "../william_data/test_xml/" # TODO: replace with your path
CLEANED_PATH: str = "../william_data/cleanedjson/" # TODO: replace with your path
PREPROCESSOR: AbstractDataLoader = GPTCleanedLoader(DATA_PATH, CLEANED_PATH, inference=True)
VECTORIZER: AbstractVectorizer = AdaVectorizer()
MODEL_WEIGHTS_PATH = "classifier_experiments/model_weights.json"
MODEL = XGBClassifier()
MODEL.load_model(MODEL_WEIGHTS_PATH)

def classify_data():
    data: UnprocessedData = PREPROCESSOR.load_and_preprocess_data()
    X, _ = VECTORIZER.vectorize(data)
    model = MODEL

    predictions = model.predict(X) # array of 0 or 1

    clean_files = sorted(os.listdir(DATA_PATH))
    
    idx = 0
    for file_name in tqdm(clean_files):
        full_path = os.path.join(DATA_PATH, file_name)

        full_path = os.path.join(DATA_PATH, "full.xml")
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(full_path, parser)

        for node in tqdm(tree.xpath('//snippet')):
            # set classifier result to the prediction at idx as string (eg map 0, 1 back to good, bad)
            node.set('classifier_result', "good" if predictions[idx] == 0 else "bad")
            idx += 1
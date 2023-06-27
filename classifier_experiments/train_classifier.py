from xgboost import XGBClassifier
from type_utils import UnprocessedData
from DataLoaders import AbstractDataLoader, GPTCleanedLoader
from Vectorizers import AbstractVectorizer, AdaVectorizer

DATA_PATH: str = "../william_data/test_xml/" # TODO: replace with your path
CLEANED_PATH: str = "../william_data/cleanedjson/" # TODO: replace with your path
PREPROCESSOR: AbstractDataLoader = GPTCleanedLoader(DATA_PATH, CLEANED_PATH)
VECTORIZER: AbstractVectorizer = AdaVectorizer()
MODEL = XGBClassifier(colsample_bytree=0.4, learning_rate=0.2, max_depth=2, n_estimators=50, subsample=0.5, gamma=0.7, min_child_weight=1, eta=0.05, reg_alpha=0.1, reg_lambda=0.1)

def train_classifier():
    data: UnprocessedData = PREPROCESSOR.load_and_preprocess_data()
    X, y = VECTORIZER.vectorize(data)
    model = MODEL

    model.fit(X, y)

    # export weights
    model.save_model("classifier_experiments/model_weights.json")

    print("Classifier successfully trained!")
    print("Weights exported to classifier_experiments/model_weights.json")

def main():
    train_classifier()

if __name__ == "__main__":
    main()
from DataLoaders import AbstractDataLoader, GPTCleanedLoader
import os

INPUT_PATH = "../william_data/test_xml/" # TODO: replace with your path, can be absolute or relative
OUTPUT_PATH = "../william_data/cleanedjson/" # TODO: replace with your path, can be absolute or relative

def preprocess_loop(auto_retry: bool = True):
    # check if the file paths exist
    if os.path.exists(INPUT_PATH) == False or os.path.exists(OUTPUT_PATH) == False:
        raise Exception("One of the file paths does not exist. Please check the paths and try again.")

    data_loader = GPTCleanedLoader(INPUT_PATH, OUTPUT_PATH)
    data = data_loader.load_and_preprocess_data()

    if len(data["bad"]) == 0 or len(data["good"]) == 0:
        print("Something went wrong... no data returned by the operation")
        return

    if auto_retry:
        print("Looping through one more to catch straggler server errors...")
        preprocess_loop(auto_retry=False)

    print("Data successfully preprocessed!")

def main():
    preprocess_loop()

if __name__ == "__main__":
    main()



    
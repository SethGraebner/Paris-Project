# WS Spring '23 Work

## Classifier Experiments

The bulk of the experimentation is contained in `experiments.ipynb`. This notebook establishes the expected data science workflow for selecting a performant classifier and all associated tools. Notably, we select a method of data preprocessing, a method of vectorization, and a classifier. Note that each of these elements is a statistically significant change, but due to the expected outsized performance gains of the former two methods, we only conduct real performance metric collection on the classifiers.

`DataLoaders.py` defines the `AbstractDataLoader` class, which provides a modular framework for importing our data with a variety of different schemas, listed in the notebook and implemented in the python file. `Vectorizers.py` does a similar thing for `AbstractVectorizer`, defining a variety of vectorization techniques ranging from BOW to pre-trained W2V to `ada` as methods. These output a consistent data schema that can be used by the rest of the process. Some work on visualization of this process is conducted in `datavis.ipynb` and observability work is done in `vec_experiments.ipynb`.

### Replicating Experiments

This should be relatively simple: point the dataloader at your data source, supply the vectorizer with a binary for the weights or an OpenAI key, and run through the notebook. Install the newest versions of the imported packages to your conda environment, or use the `environment.yaml` file committed in this folder to clone my exact environment (which contains a superset of the required packages).

### Results

See the notebook for detailed results, but in short:

- XGBoost is the most performant simple classifier, and requires little tuning
- OCR errors are prevalent enough in the original dataset, to the point where our vectorization process is hindered
  - This can be assuaged by re-OCRing the data using Google Cloud Vision, as demonstrated in `ocr_all_pdfs_in_folder.py`, a script defining the automated process to do this given an original pdf folder and outputting XML (albeit with some minor tagging issues at the moment)
  - Alternatively, `GPTCleanedLoader` seeks to preprocess our text with instructions to remove and correct OCR errors, which works quite well (albeit being a time-intensive and minorly costly initiative)
- Ada should be the strongest vectorizer, but it may be worth checking out Anthropic's alternatives.
- Again, the largest next step is in relation to data quality. A large majority of our labels are "bad" which in addition to being potentially eroneous, can skew our classifiers towards overfitting.

### Next Steps

Performance is still gated by data quality. A more serious subproject should be undertaken to collect and label a larger source. Our classifier still overfits, suggesting a data quality issue. An additional gain of this initiative would be ability to more towards stronger classifiers, eg bespoke neural nets. Data quality can also be raised by a more complete pass of re-OCRing or language model correction. The current demos offer a simple way of doing this, but experimentation can continue with other tools (particularly, I'd consider looking at `claude-instant` for the language model).

I'd recommend a three-fold process, if possible. First, improve all existing data with improved OCR / AI pre-processing. Secondly, examine previous labeling quality and collect more data. Thirdly, and if possible, examine other methodologies than just using a basic classifier. I'm not convinced this is actually the best way to approach things: I think there's a chance we can examine this as an unsupervised problem and determine the quality of these excerpts using either foundation models, embedding similarity metrics, or other clustering tools. However, it's also worth continuing with the classifier method - and likely easier if engineering help is scarce.

## Usage Guide

General usage patterns for each step of the process, approximately in the order of the workflow.

### OCR PDFs

1. Create a Google Cloud (henceforth GCP) account.
2. Enable the Cloud Vision project on the GCP portal, and then follow the instructions to link your local machine to GCP. This is typically running a command through the GCP CLI to auth your local machine and then is pretty hands off. I'd recommend this to manual SSH keys or something of the like.
3. Create a Storage bucket, and keep track of the name. Within that bucket, create a folder `pdfs` and `ocr_output`. On your machine, create a directory you want to store your data, and create folders of the same name in that directory.
4. Specify your local directory and the GCP bucket name in `ocr_all_pdfs_in_folder.py` file's global variables.
5. Activate your conda environment, and run `python ocr_all_pdfs_in_folder.py`. This will initiate the process of uploading your pdfs to the bucket, then passing them into the OCR tool, then retrieving them from the bucket to your local machine. This __will__ charge your associated credit card, both for the Vision API usage and then on a monthly basis for file storage. I'd recommend choosing a destination for your files and keeping them there, be it the local for cost efficiency or the bucket for memory efficiency. At each step, the script checks if a local copy of work already done exists, or if a file is already uploaded, and skips as necessary to save on costs. As the process completes, you will see txt files populate to your local directory that can be converted to XML via existing scripts in this project.

### Pre-Process Raw Data (for training)

This is contained in training a classifier, and using a classifier (as seen below) but can also be done independently.

1. Obtain an `OPENAI_API_KEY` from their website (requires account creation and credit card), and attach this to the .env file (You will not see this presently, as it is gitignored for key security reasons. You need to make one in the main directory of the project and DO NOT UPLOAD IT TO GITHUB!).
2. Configure your input and output paths in `preprocess_with_ai.py` in the global variables. Run the file with `python preprocess_with_ai.py`. Note: this is __slow__, and can error out due to server load. However, the process will continue to the next sample if this happens, and flag the failed one for revision. This can also be batched, as after every XML file is complete, it will write the results to your local folder and on successive calls to the function, it will retrieve this from the cache if possible (and at this point, correct errored-out calls). If all the files are complete, it will quickly load the data from a `.pkl` file created by the program.
   1. Alternatively, either in the `experiments.ipynb` notebook, or anywhere else of your choosing, define a `GPTCleanedLoader` object and specify your source `data_path` and your destination `cleaned_path`. The tool expects XML in and outputs JSON files that are of the form of a list of dictionaries, with the properties `label`, `text` and `cleaned`. This will give you a little more manual control of the process.
   2. Run the `load_and_preprocess_data()` call to start the process.
3. Once your data is loaded, this can be used to either train a new classifier, or simply to feed into the model to classify the sample.

### Train a Classifier

1. `train_classifier.py` combines the data-preprocessing and vectorization steps, then trains an XGBoost classifier with the tuned hyperparameters. Specify your paths in the file, and then run using `python train_classifier.py`
2. Your weights will be exported to a `.json` file to use later on. The path will be printed to the terminal.

### Use a Trained Classifier

1. `classify_data.py` combines data-preprocessing and vectorization, then loads specified weights and applies the XGBoost classifier for said weights.
2. Note: this writes to the XML files with the `<snippet>` property, so if you don't want this getting changed, make a copy of your XML directory and feed your data there.

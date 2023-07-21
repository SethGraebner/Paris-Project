'''
    Script to run batches of PDFs through OCR on Google Cloud Platform (GCP) using Cloud Vision. Requires an account on GCP with a project created, Cloud Vision's API enabled, and a storage bucket in Google Cloud Storage, containing folders "PDFS" and "OCR_OUTPUT."
    
    Iteratively scans through folder, uploads PDF documents to Google Cloud Storage, OCRs the documents with Cloud Vision, then downloads the OCRed texts as .txt files.

    Expects to find on local machine a folder, named at "DATA_FOLDER" below, containing subfolders "PDFS" and "OCR_OUTPUT"; this folder must be located in same parent folder of folder containing this script.

    Checks for existing files at each step to avoid duplicate work. For large-scale operations, consider eliminating the read-back of txt files to the local, and seperating the upload and OCR steps into seperate scripts.
'''

import os
from tqdm import tqdm
import json
import re
from google.cloud import vision
from google.cloud import storage
import time

DATA_FOLDER = '/2023' # PATH TO FOLDER CONTAINING "PDFS" and "OCR_OUTPUT." MUST BE IN SAME PARENT FOLDER as FOLDER w/ THIS SCRIPT

PDFS_PATH = os.path.join(DATA_FOLDER, 'pdfs')
TXT_PATH = os.path.join(DATA_FOLDER, 'ocr_output') 
GCP_BUCKET = 'paris_ocr' # NAME OF "BUCKET" WITHIN THE PROJECT ON GOOGLE CLOUD PLATFORM, WHICH MUST CONTAIN FOLDERS "PDFS" AND "OCR_OUTPUT."


def OCR_document(name):
    filename = f'{name}.pdf'
    """OCR with PDF/TIFF as source files on GCS. Loads files to GCS, does not load back to local"""
    gcs_source_uri = f"gs://{GCP_BUCKET}/pdfs/{filename}"
    gcs_destination_uri = f"gs://{GCP_BUCKET}/ocr_output/{name}.json"

    # check if file already exists. It will be in the format filename.jsonoutput-{pages}.json, so match on a file starting with filename
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(GCP_BUCKET)
    blobs = bucket.list_blobs(prefix='ocr_output')
    for blob in blobs:
        if blob.name.startswith(f'ocr_output/{name}'):
            print(f"File {filename} already exists, skipping")
            return

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    batch_size = 100

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)
    

    operation = client.async_batch_annotate_files(
        requests=[async_request], timeout=50)

    print('Waiting for Cloud Vision to finish OCR operation.')

    if operation.running():
        time.sleep(10)
    
    if operation.done():
        print("done")

    

def preprocess(text: str) -> str:
    # replace '-\n' with ''
    text = re.sub(r'-\n', '', text)
    
    text = re.sub(r'[^\s0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàâäæçèéêëîïñôùûüÿœ̀ÀÂÄÆÇÈÉËÎÏÑÔÙÛÜŸŒœ\'.,!?:;-]', ' ', text)

    # replace all misc whitespace with ' '
    text = re.sub(r'\s+', ' ', text)

    # ex. 'pour75' -> 'pour 75', but keep '2e'
    text = re.sub(r'(?<=[a-zA-Z])\d', ' ', text)

    # ex. 'mo-75 narchie' -> 'monarchie' 
    #  Louis XIV avait trop bien combiné les dimensions de sa bâtisse pour qu'elle pût subsister sans lui, pour qu'une autre mo-123 narchie
    text = re.sub(r'(?<=[a-zA-Z])-\d+\s', '', text)
    return text

def read_doc_from_gcs(name: str):
    filename = f'{name}.pdf'
    # first, check if a results file already exists locally
    if os.path.exists(f'{TXT_PATH}/{name}.txt'):
        print(f"File {filename} already exists, skipping")
        return

    storage_client = storage.Client()

    # look for file in GCS, in ocr_outputs/filename.jsonoutput-{pages}.json
    bucket = storage_client.get_bucket(GCP_BUCKET)
    blobs = bucket.list_blobs(prefix='ocr_output')
    
    blob_list = []
    for blob in blobs:
        if blob.name.startswith(f'ocr_output/{name}'):
            blob_list.append(blob)

    def compare_names(name: str):
        # names of form res.jsonoutput-x-to-y.json
        # we want to sort by x
        return int(name.split('-')[1])

    text = ""
    for blob in sorted(blob_list, key=lambda x: compare_names(x.name)):
        # print(blob)
        print(blob.name)

        json_string = blob.download_as_bytes().decode("utf-8")
        responses = json.loads(json_string)['responses']
        for response in responses:
            if 'fullTextAnnotation' in response.keys():
                text += response['fullTextAnnotation']['text']


    text = preprocess(text)

    # save text to [destination_specified_above]/ocr_output/{name}.txt
    with open(f"../{TXT_PATH}/{name}.txt", "w") as f:
        f.write(text)

    print('Output complete')

def upload_pdf_to_gcs(name):
    filename = f'{name}.pdf'
    full_path = f'../{PDFS_PATH}/{filename}'

    # check if file already exists locally
    if os.path.exists(f'../{TXT_PATH}/{name}.txt'):
        print(f"File {filename} already done, skipping")
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_BUCKET)

    # check if file already exists in the pdfs folder
    if len(list(bucket.list_blobs(prefix=f'pdfs/{filename}'))) > 0:
        print(f'File {filename} already exists in {GCP_BUCKET}.')
        return

    # save to 'pdfs' folder in the bucket
    blob = bucket.blob(f'pdfs/{filename}')
    blob.upload_from_filename(full_path)

    print(f'File {filename} uploaded to {GCP_BUCKET}.')


def __main__():
    '''
    Iteratively scans through folder, uploads PDF documents to Google Cloud Storage, OCRs the documents using Cloud Vision, then downloads the OCRed texts as .txt files.

    Checks for existing files at each step to avoid duplicate work. For large-scale operations, consider eliminating the read-back of txt files to the local, and separating the upload and OCR steps into seperate scripts. 
    
    '''
    for filename in tqdm(os.listdir(f'../{PDFS_PATH}')):
        if filename.endswith('.pdf'):
            print(f'uploading {filename}')
            name = filename.split('.')[0]

            if os.path.exists(f'../{TXT_PATH}/{name}.txt'):
                print(f"File {filename} already done, skipping")
                continue

            # upload to GCS
            upload_pdf_to_gcs(name)

            # process on GCS with Cloud Vision
            OCR_document(name)

    #After sending all files in batch through Cloud Vision, wait 45 seconds after reported completion so we're sure JSONS are present in GCS bucket
    print("Waiting for 45s to ensure files are ready...")
    time.sleep(45)
    
    #Move results from GCS bucket to local machine as .txt files
    for filename in tqdm(os.listdir(f'../{PDFS_PATH}')):
         if filename.endswith('.pdf'):
                print(f'processing {filename}')
                name = filename.split('.')[0]
            
                read_doc_from_gcs(name)


if __name__ == "__main__":
    __main__()

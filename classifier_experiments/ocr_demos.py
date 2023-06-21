'''
Demo script to test various OCR tools. DO NOT USE - instead use `ocr_all_pds_in_folder.py` to process all PDFs in a folder.
'''

import os
from tqdm import tqdm
# from pdf2image import convert_from_path, convert_from_bytes
import json
import re
from google.cloud import vision
from google.cloud import storage

def ocr_with_kraken(img: str, output_path: str):
    """
    Run OCR on a PDF file using Kraken.
    """
    os.system(f"kraken -i {img} {output_path} segment -bl ocr -m HTR-United-Manu_McFrench.mlmodel")


def process_doc(gcs_source_uri, gcs_destination_uri):
    """OCR with PDF/TIFF as source files on GCS. Loads files to GCS, does not load back to local"""
 

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
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

    print("completed")

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

def read_doc_from_gcs(name):
    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client()
    # storage_client.

    # match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    # if match == None:
    #     raise ValueError(f"Invalid GCS URI: {gcs_destination_uri}")
    
    bucket_name = "parisprojsink" # match.group(1)
    prefix = "res" #match.group(2)

    print('above')
    bucket = storage_client.get_bucket(bucket_name, timeout=20)

    print('here')

    # List objects with the given prefix, filtering out folders.
    blob_list = [blob for blob in list(bucket.list_blobs(
        prefix=prefix)) if not blob.name.endswith('/')]
    print('Output files:')

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

    # save text to william_data/ocr_output/{name}.txt
    with open(f"william_data/ocr_output/{name}.txt", "w") as f:
        f.write(text)

    print('Output complete')

def __main__():
    # process_doc("gs://parisprojsource/Balzac_1841_bpt6k1133819.pdf", "gs://parisprojsink/res.json")
    read_doc_from_gcs("res")


if __name__ == "__main__":
    __main__()
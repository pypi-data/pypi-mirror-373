"""Example of using the SROIE dataset for receipt information extraction evaluation.

This example requires the dotevals-datasets plugin to be installed:
    pip install dotevals-datasets

The SROIE dataset contains receipt images with annotations for:
- company: The business name on the receipt
- date: The transaction date
- address: The business address
- total: The total amount

Note: This example uses a placeholder function for receipt extraction.
In practice, you would use a multimodal model or OCR system.
"""

import json

from dotevals import Result, foreach
from dotevals.evaluators import valid_json


def extract_receipt_info(prompt):
    """placeholder for the receipt info extraction"""
    return json.dumps(
        {"company": "", "date": "", "address": "", "total": ""}, sort_keys=True
    )


@foreach.sroie("test")
def eval_sroie(images, address, company, date, total):
    prompt = """<|im_start|>system
        You are an expert in receipt OCR and information extraction. You will be presented with an image of a receipt and asked to extract specific information from it.

        Your task is to extract the following information from the receipt image:
        - company: The name of the company or business that issued the receipt
        - date: The date when the receipt was issued (in DD/MM/YYYY format)
        - address: The address of the business or store location
        - total: The total amount paid
        """
    result = extract_receipt_info(prompt)
    json_score = valid_json(result)

    return Result(prompt, scores=[json_score])

import re
from time import sleep

import requests
from loguru import logger

from phylodata.errors import BlastError

BLAST_URL = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
WAIT_TIME_S = 5
MAX_BATCH_SIZE = 32


def run_blast(
    sequences: list[str], parameters: dict, max_length_considered: int
) -> list:
    """Runs BLAST for the given sequences and parameters.
    Note that the QUERY parameter is added by this method.
    Returns the BLAST API results."""
    results = []

    for i in range(0, len(sequences), MAX_BATCH_SIZE):
        batch = sequences[i : i + MAX_BATCH_SIZE]

        fasta_data = build_fasta_data(batch, max_length_considered)
        parameters["QUERY"] = fasta_data

        request_id, _ = initiate_blast_request(fasta_data, parameters)
        wait_until_ready(request_id)

        results += fetch_results(request_id)["BlastOutput2"]

    return results


def build_fasta_data(sequences: list[str], max_length_considered: int) -> str:
    fasta_data = ""

    for i, seq in enumerate(sequences):
        fasta_data += f">{i}\n{seq[:max_length_considered]}\n"

    return fasta_data


def initiate_blast_request(fasta_data: str, parameters: dict) -> tuple[str, int]:
    response = requests.post(BLAST_URL, data=parameters)
    if response.status_code != 200:
        logger.error("BLAST submission failed: " + response.text)
        raise BlastError("BLAST submission failed.")

    request_id = re.search(r"RID = (\S+)", response.text)
    wait_time_s = re.search(r"RTOE = (\d+)", response.text)

    if not request_id or not wait_time_s:
        logger.error("Failed to parse BLAST response: " + response.text)
        raise BlastError("Failed to parse BLAST response.")

    request_id = request_id.group(1)
    wait_time_s = int(wait_time_s.group(1))

    return request_id, wait_time_s


def wait_until_ready(request_id: str):
    result_params = {
        "CMD": "Get",
        "RID": request_id,
    }

    response = requests.get(BLAST_URL, params=result_params)
    status = re.findall("Status=(.*)", response.text)[0]

    match status:
        case "READY":
            return
        case "WAITING":
            logger.info("Keep waiting for BLAST results...")
            sleep(WAIT_TIME_S)
            wait_until_ready(request_id)
        case _:
            logger.error(
                f"BLAST submission failed with status {status}: {response.text}"
            )
            raise Exception(f"BLAST submission failed: {status}")


def fetch_results(request_id: str) -> dict:
    result_params = {
        "CMD": "Get",
        "RID": request_id,
        "FORMAT_TYPE": "JSON2_S",
        "ALIGNMENTS": 1,
        "DESCRIPTIONS": 1,
    }

    response = requests.get(BLAST_URL, params=result_params)

    try:
        result = response.json()
    except Exception:
        logger.error(f"Failed to parse BLAST results: {response.text}")
        raise BlastError("Failed to parse BLAST results.")

    return result


def extract_taxon_ids(blast_json: list) -> list[int | None]:
    taxon_ids = []

    for result in blast_json:
        try:
            taxon_id = result["report"]["results"]["search"]["hits"][0]["description"][
                0
            ]["taxid"]
            taxon_id = int(taxon_id)
        except (KeyError, IndexError):
            taxon_id = None

        taxon_ids.append(taxon_id)

    return taxon_ids

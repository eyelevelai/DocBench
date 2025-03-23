from datetime import datetime
from pathlib import Path
from groundx import Document, GroundX

from gx_config import BUCKET_ID, GX_KEY

if not GX_KEY:
    raise ValueError("\n\n\tGX_KEY is not set\n")

ACTIVE_BUCKET = BUCKET_ID

def scan_data_folder(data_path: Path):
    pdf_files = []
    jsonl_files = []

    for folder in data_path.rglob("*"):
        if folder.is_dir():
            pdfs = list(folder.glob("*.pdf"))
            jsonls = list(folder.glob("*.jsonl"))
            if len(pdfs) != 1 or len(jsonls) != 1:
                raise ValueError(f"Folder {folder} does not contain exactly one PDF and one JSONL file")
            pdf_files.append(pdfs[0])
            jsonl_files.append(jsonls[0])
    
    return pdf_files, jsonl_files

def prompt_bucket_action(bucket_id: int):
    global ACTIVE_BUCKET

    if bucket_id == 0:
        answer = input("Bucket ID is 0. Do you want to create a new bucket? (y/n): ").strip().lower()
        if answer not in ("y", "yes"):
            print("Bucket creation not confirmed. Exiting.")
            exit(1)
        else:
            print("Bucket creation confirmed.")
    else:
        answer = input(f"Bucket ID is set to {bucket_id}. Do you want to upload to bucket {bucket_id}? (y/n): ").strip().lower()
        if answer not in ("y", "yes"):
            answer = input("Do you want to create a new bucket? (y/n): ").strip().lower()
            if answer not in ("y", "yes"):
                print("Exiting.")
                exit(1)
            ACTIVE_BUCKET = 0
        else:
            print("Bucket upload confirmed.")

gx_client = GroundX(api_key=GX_KEY)

skip = []

if __name__ == "__main__":
    data_folder = Path("data")
    
    if not data_folder.exists():
        print(f"Data folder '{data_folder}' does not exist!")
        exit(1)

    print()
    prompt_bucket_action(ACTIVE_BUCKET)

    bucket_id = ACTIVE_BUCKET
    if ACTIVE_BUCKET < 1:
        current_date = datetime.now().strftime("%Y_%d_%m_%H_%M")
        bucket_name = f"DocBench_{current_date}"

        res = gx_client.buckets.create(name=bucket_name)
        bucket_id = res.bucket.bucket_id
        print(f"\ncreated bucket: [{bucket_name}]\n\n\tset BUCKET_ID = {bucket_id} in gx_config.py before running tests\n")

    docs = []
    pdfs, jsonls = scan_data_folder(data_folder)
    for pdf_path in pdfs:
        if pdf_path not in skip:
            docs.append(
                Document(
                    bucket_id=bucket_id,
                    file_path=str(pdf_path),
                )
            )

    res = gx_client.ingest(
        documents=docs,
        wait_for_complete=True,
        batch_size=25,
    )
    print("\n\ningest complete\n")
    if ACTIVE_BUCKET < 1 and bucket_id > 0:
        print(f"\tremember to set BUCKET_ID = {bucket_id} in gx_config.py before running tests\n")

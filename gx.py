import glob, json, time
from pathlib import Path

from groundx import GroundX
from openai import OpenAI

GX_DEBUG = False

class GXClient():
    def __init__(
        self,
        api_key: str,
        bucket_id: int,
        openai_key: str,
        completion_model: str = "chatgpt-4o-latest",
    ):
        self.bucket_id = bucket_id
        self.client = GroundX(api_key=api_key)
        self.completion_model = completion_model
        self.doc_map = {}
        self.oai = OpenAI(api_key=openai_key)

        res = self.client.documents.lookup(id=bucket_id, n=300)
        if res and res.documents:
            print(f"\n\n\tdocs [{len(res.documents)}]\n")
            for d in res.documents:
                self.doc_map[d.file_name] = d.document_id

        while res.next_token is not None:
            res = self.client.documents.lookup(id=bucket_id, n=300, next_token=res.next_token)
            if res and res.documents:
                for d in res.documents:
                    self.doc_map[d.file_name] = d.document_id

        print(f"\n\n\tdoc_map [{len(self.doc_map)}]\n")

    def query(
        self,
        query: str,
        doc_id: str,
    ):
        retrievals = None
        tasktime = time.time()
        for _ in range(3):
            reqtime = time.time()
            try:
                retrievals = self.client.search.documents(query=query, document_ids=[doc_id], verbosity=0)
                break
            except Exception as e:
                print(f"gx error, trying again [{time.time() - reqtime:.4f}]")
                print(e)
                print(type(e))
                time.sleep(5)

        if GX_DEBUG:
            print(f"gx done [{time.time() - tasktime:.4f}]")

        if retrievals is None or retrievals.search is None or retrievals.search.text is None:
            return ""

        source = str(retrievals.search.text)
        if source == "":
            return ""

        print(f"\n\n\tlen source [{len(source)}]\n")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that helps users answer questions based on the given document.",
            },
            {
                "role": "system",
                "content": source,
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        tasktime = time.time()
        for _ in range(3):
            reqtime = time.time()
            try:
                result = (
                    self.oai.chat.completions.create(
                        model=self.completion_model,
                        messages=messages,
                        temperature=1.0,
                        top_p=0.7,
                    )
                    .choices[0]
                    .message.content
                )
                if result is not None:
                    break
                else:
                    print(
                        f"openAI result is none, trying again [{time.time() - reqtime:.4f}]"
                    )
                    time.sleep(5)
            except Exception as e:
                print(f"error, trying again [{time.time() - reqtime:.4f}]")
                print(e)
                print(type(e))
                time.sleep(5)

        if GX_DEBUG:
            print(f"openAI done [{time.time() - tasktime:.4f}]")

        return str(result)

    def process_folder(
        self,
        folder: str,
    ):
        pdf_path_str = glob.glob(f'./data/{folder}/*.pdf')[0]
        pdf_path = Path(pdf_path_str)
        if pdf_path.name not in self.doc_map:
            raise ValueError(f"\n\n\t[{pdf_path.name}] was not ingested by GroundX\n")

        answers = ""
        jsonlines = open(f'./data/{folder}/{folder}_qa.jsonl', 'r').readlines()
        for i, line in enumerate(jsonlines):
            question = json.loads(line)['question']

            if i > 0:
                answers += "\n"
            answers += f"{i+1}. {self.query(query=question, doc_id=self.doc_map[pdf_path.name])}"

        return answers
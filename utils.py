from openai import OpenAI
from secret_key import OPENAI_API_KEY

oai_key = OPENAI_API_KEY
try:
    from gx_config import OPENAI_API_KEY as gx_oai_key

    if gx_oai_key != "":
        oai_key = gx_oai_key
except Exception:
    1

def get_gpt_response_openai(text, engine='gpt-4-0125-preview', system_content='You are a helpful assistant.' ,json_format=False):
    global oai_key

    client = OpenAI(
        base_url="https://api.openai.com/v1", api_key=oai_key
    )
    if json_format:
        completion = client.chat.completions.create(
            model=engine,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                {"role": "user", "content": text},
            ],
        )
    else:
        completion = client.chat.completions.create(
            model=engine,
            messages=[
                {
                    "role": "system",
                    "content": system_content,
                },
                {"role": "user", "content": text},
            ],
        )

    text_response = completion.choices[0].message.content
    # print(text_response)

    response_dict = completion.json()
    # print(response_dict)
    # record(response_dict)
    return text_response
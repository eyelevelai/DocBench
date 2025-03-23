# DocBench: A Benchmark for Evaluating LLM-based Document Reading Systems
Paper Link: _[DocBench: A Benchmark for Evaluating LLM-based Document Reading Systems](https://arxiv.org/pdf/2407.10701)_

## EyeLevel

### Pre-Requisites

Run `pip install -r requirements.txt` to install dependencies.

It is recommended that you use python version 3.10.0+.

### Uploading Files

- [Download the DocBench data files](#data) and unzip at the base of this project
  - The unzipped files should be at `./data`
- Copy/Paste `gx_config.sample.py` to `gx_config.py`
  - Add your `GX_KEY` and `OPENAI_API_KEY`
  - If you wish to upload files to an existing bucket, set `BUCKET_ID`
- Run the `upload.py` script to upload files to GroundX
```bash
python upload.py
```

### Running Tests

Use the DocBench script `run.py` to execute the DocBench tests. To run the tests using GroundX, use the following command:

```bash
# runs all tests using GroundX: 1,102 test questions for 229 documents
python run.py --system gx
```

To run the tests for a single PDF, use the following command options:

```bash
# runs the tests in folder 53 using GroundX: 5 test questions for inditex_2021.pdf
python run.py --system gx --initial_folder 53 --total_folder_number 53
```

To run the tests using one of the other systems (e.g. gpt-4o), use the following command:

```bash
# runs all tests using GPT-4o + the agent file search tool: 1,102 test questions for 229 documents
python run.py --system gpt-4o
```

```bash
# runs the tests in folder 53 using GPT-4o + the agent file search tool: 5 test questions for inditex_2021.pdf
python run.py --system gpt-4o --initial_folder 53 --total_folder_number 53
```

The DocBench test scripts will save the responses to a file within each test folder according to the following naming convention: `data/{test_number}/{system}_results.txt`


### Evaluating Results

Use the DocBench script `evaluate.py` to execute the DocBench auto-evaluation scripts. To run the tests using GroundX, use the following command:

### Changes

We made the following changes:

- Added GroundX (`gx`) as a system option to: run and evaluate
- Added `gx.py`, which contains the logic to produce completions based on GroundX RAG retrievals for `run.py`
- Added `upload.py`, which contains logic to upload files to GroundX
- Added a `gx_config.py` containing GroundX-specific configs
- Added a `requirements.txt` to install dependencies (was only tested on system options `gpt-4o` and `gx`)
- Added a `--result_dir` option to `evaluate.py` where result files can be saved
- Moved `eval_result.ipynb` to `eval_result.py`, added command line options, and prettified the outputs
- Added a `.gitignore`

## Introduction

**DocBench** is a benchmark that takes raw PDF files and accompanying questions as inputs, with the objective of generating corresponding textual answers. It includes 229 real documents and 1,102 questions, spanning across five different domains and four major types of questions.

The construction pipeline consists of three pahses: (a) Document Collection; (b) QA-pair Generation; (c) Quality Check.

![](figs/intro.png)



## Dataset Overview

![](figs/dataset.png)

## Data

Data can be downloaded from: https://drive.google.com/drive/folders/1yxhF1lFF2gKeTNc8Wh0EyBdMT3M4pDYr?usp=sharing

## Implementations

We need keys from Hugging Face and OpenAI. (get your own keys to replace the `HF_KEY` and `OPENAI_API_KEY` in `secret_key.py`)

### a. Download

Download the models to evaluate: 

```
bash download.sh
```

- ```YOUR_OWN_DIR```: where to save the downloaded models
- ```MODEL_TO_DOWNLOAD```: model name from hugging face

### b. Run

First, we deploy vLLM as a server:

```bash
python -m vllm.entrypoints.openai.api_server --model your_merged_model_output_path --served-model-name my_model --worker-use-ray --tensor-parallel-size 8 --port 8081 --host 0.0.0.0 --trust-remote-code --max-model-len 8192
```

Second, we run the models for inference:

```
python run.py \
  --system gpt4 \
  --model_dir MODEL_DIR \	#comment this line if we use api-based models
  --initial_folder 0
```

### c. Evaluate

Evaluate the results:

```bash
python evaluate.py \
  --system gpt4 \
  --resume_id 0
```

Notice: there could be some warnings for unexpected outputs. We could check the outputs according to the warning hint.


## Citation
If you find this work useful, please kindly cite our paper:
```
@misc{zou2024docbenchbenchmarkevaluatingllmbased,
      title={DOCBENCH: A Benchmark for Evaluating LLM-based Document Reading Systems}, 
      author={Anni Zou and Wenhao Yu and Hongming Zhang and Kaixin Ma and Deng Cai and Zhuosheng Zhang and Hai Zhao and Dong Yu},
      year={2024},
      eprint={2407.10701},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.10701}, 
}
```

<!---
Copyright 2024 tony9402. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Huggingface NAS

## Installation

```bash
pip3 install huggingface_nas
```

## How to use

### Huggingface to Synology NAS (Model)

```python
from huggingface_nas import upload_model

upload_model(
    name="<huggingface model ex. meta-llama/Llama-3.3-70B-Instruct>",
    base_folder="<synology folder>",
    token="<huggingface token>",
    ip_address="<synology ip>",
    port="<synology port>",
    username="<synology username>",
    password="<synology password>"
)
```

### Huggingface to Synology NAS (Dataset)

```python
from huggingface_nas import upload_dataset

upload_dataset(
    name="<huggingface dataset ex. meta-llama/Llama-3.3-70B-Instruct-evals>",
    base_folder="<synology folder>",
    token="<huggingface token>",
    ip_address="<synology ip>",
    port="<synology port>",
    username="<synology username>",
    password="<synology password>"
)
```

### Load dataset from Synology NAS

```python
from huggingface_nas import load_dataset_nas

data = load_dataset_nas(
    path="<model path such as meta-llama/Llama-3.3-70B-Instruct-evals>",
    base_path="<share folder in synology NAS>",
    ip_address="<synology ip>",
    port="<synology port>",
    username="<synology username>",
    password="<synology password>"
)
```

### Load Model from Synology NAS

```python
from transformers import AutoModel
from huggingface_nas import prepare_model_from_nas

model_download_path = prepare_model_from_nas(
    path="<model path such as meta-llama/Llama-3.3-70B-Instruct>",
    base_path="<share folder in synology NAS>",
    ip_address="<synology ip>",
    port="<synology port>",
    username="<synology username>",
    password="<synology password>"
)
AutoModel.from_pretrained(model_download_path)
```


# DDDOCR-py

Python client for the [3DOCR.com](https://3docr.com) OCR service.

## Install
```bash
pip install dddocr-py
```
## Quick start

```python
from dddocr_py import OCRService

service = OCRService(api_key="YOUR_API_KEY", auto_download=True)
job = service.convert(
    input_file_path="sample.pdf",
    options={"output_type": "pdf", "language": "eng"},
    save_path="sample_ocr.pdf",
)
print(job)  # status will update in background
```
## Manual download

```python
if job.status == "completed":
    job.download("output.pdf")
```
import json
import requests
import time
from threading import Thread
from typing import List, Dict, Optional


class OCRService:
    """
    A Python library to interact with the 3DOCR.com OCR service. Provides methods for creating OCR Jobs

    """

    def __init__(self, api_key: str, auto_download: bool = False):
        """
        Initialize the OCRService instance.

        Args:
            api_key (str): The authentication token for accessing the API.
            auto_download (bool): Whether to automatically download completed jobs. Defaults to False.
        """
        self.base_url: str = "https://3docr.com"
        self.headers: Dict[str, str] = {
            "X-API-KEY": api_key,
        }
        self.active_jobs: Dict[str, OCRJob] = {}
        self.auto_download: bool = auto_download

        self.polling_thread = Thread(target=self._poll_jobs, daemon=True)
        self.polling_thread.start()

    def convert(self, input_file_path: str, save_path: Optional[str] = None,options: Dict = {}) -> "OCRJob":
        """
        Initiates an OCR conversion job.

        Args:
            input_file_path (str): Path to the file to be uploaded for OCR.
            save_path (Optional[str]): Path to save the downloaded file if auto-download is enabled.
            options (Dict, optional): Options for OCR processing, such as output type, language, or deskew.

        Returns:
            OCRJob: The OCRJob instance representing the initiated job.

        Raises:
            ValueError: If auto_download is enabled but save_path is not provided.
        """
        if self.auto_download and not save_path:
            raise ValueError("save_path must be provided if the auto_download feature is enabled.")

        url = f"{self.base_url}/ocr/convert"
        files = {"file": open(input_file_path, "rb")}
        data = {"options": json.dumps(options)}

        response = requests.post(url, headers=self.headers, files=files, data=data)
        response.raise_for_status()

        job_data = response.json()
        job = OCRJob(self)
        job._from_convert_json(job_data)
        job.save_path = save_path
        job.options = options

        self.active_jobs[job.job_id] = job
        return job

    def _poll_jobs(self) -> None:
        """
        Polls active jobs every 10 seconds and downloads results of completed jobs if auto-download is enabled.
        """
        while True:
            time.sleep(10)

            if not self.active_jobs:
                continue

            scannable_jobs = [job_id for job_id, job in self.active_jobs.items() if not job.downloaded]

            if not scannable_jobs:
                continue

            for i in range(0, len(scannable_jobs), 100):
                batch = scannable_jobs[i:i + 100]
                statuses = self._status(batch)

                for status in statuses:
                    job_id = status.get("job_id")
                    if not job_id:
                        continue

                    job_reference = self.active_jobs.get(job_id)
                    if not job_reference:
                        continue

                    job_reference._update_from_status_json(status)

                    if job_reference.status == "completed" and not job_reference.downloaded:
                        try:
                            job_reference.download()
                        except Exception as e:
                            print(f"Failed to download job {job_id}: {e}")

                for job_id in batch:
                    if job_id not in self.active_jobs:
                        continue

                    job_reference = self.active_jobs[job_id]
                    if job_reference.status == "expired":
                        job_reference.expired = True
                        del self.active_jobs[job_id]

    def _status(self, job_ids: List[str]) -> List[Dict]:
        """
        Retrieves the processing status of multiple OCR jobs.

        Args:
            job_ids (List[str]): List of job IDs to check the status of.

        Returns:
            List[Dict]: A list of dictionaries containing job statuses.
        """
        url = f"{self.base_url}/ocr/status"
        payload = {"job_ids": job_ids}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get("statuses", [])



class OCRJob:
    def __init__(self, parent: OCRService):
        """
        Initializes an OCRJob instance.

        Args:
            parent (OCRService): The OCRService instance managing this job.
        """
        self.job_id: str = ""
        self.save_path: Optional[str] = None
        self.status: str = ""
        self.options: Dict = {}
        self.parent: OCRService = parent
        self.expired: bool = False
        self.downloaded: bool = False

    def _from_convert_json(self, json_data: Dict):
        """
        Populates the job attributes from the conversion response JSON.

        Args:
            json_data (Dict): The response JSON from the OCR conversion request.
        """
        self.job_id = json_data.get("job_id", "")
        self.status = json_data.get("status", "")

    def _update_from_status_json(self, json_data: Dict):
        """
        Updates the job status from the status response JSON.

        Args:
            json_data (Dict): The response JSON from the status check request.
        """
        self.status = json_data.get("status", "")

    def download(self, save_path: Optional[str] = None) -> None:
        """
        Downloads the result of a completed OCR job.

        Args:
            save_path (Optional[str]): Path to save the downloaded file. If not provided, uses the job's save_path attribute.

        Raises:
            RuntimeError: If the job is not in a state where it can be downloaded.
        """
        if self.status != "completed":
            if self.status == "error":
                raise RuntimeError(
                    f"OCRJob with job_id = {self.job_id} encountered a server-side error. The uploaded file might be corrupt."
                )
            elif self.status == "expired":
                raise RuntimeError(
                    f"OCRJob with job_id = {self.job_id} has expired. Jobs expire within 1 hour of completion."
                )
            else:
                raise RuntimeError(
                    f"OCRJob with job_id = {self.job_id} cannot be downloaded as processing has not completed."
                )

        url = f"{self.parent.base_url}/ocr/download/{self.job_id}"
        response = requests.get(url, headers=self.parent.headers, allow_redirects=True)
        response.raise_for_status()

        output_path = save_path or self.save_path
        if not output_path:
            raise ValueError("A valid save path must be provided for the download.")

        with open(output_path, "wb") as f:
            f.write(response.content)

        self.downloaded = True

    def __repr__(self):
        return (
            f"OCRJob(job_id='{self.job_id}', save_path='{self.save_path}', "
            f"status='{self.status}', options={self.options})"
        )




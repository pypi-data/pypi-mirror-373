import os
import shutil
from typing import Optional, Union

from datasets import load_dataset, Split
from datasets.utils.version import Version
from huggingface_hub import Repository
from synology_api.exceptions import FileStationError

from .webapi import WebAPI



def upload_local_model(
    local_dir: str,
    base_path: str,
    target_folder: str,
    token: Optional[str] = None,
    *,
    ip_address: Optional[str] = None,
    port: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    secure: bool = False,
    cert_verify: bool = False,
    dsm_version: int = 7,
    debug: bool = True,
    otp_code: Optional[str] = None,
    interactive_output: bool = True,
):
    if not os.path.exists(local_dir):
        raise FileNotFoundError(f"{local_dir} 경로를 찾지 못했습니다")

    try:
        fi = WebAPI(
            ip_address=ip_address,
            port=port,
            username=username,
            password=password,
            secure=secure,
            cert_verify=cert_verify,
            dsm_version=dsm_version,
            debug=debug,
            otp_code=otp_code,
            interactive_output=interactive_output,
        )
        try:
            model_name = target_folder
            remote_folder = os.path.join(base_path, model_name)
            res = fi.get_file_list(folder_path=remote_folder)
            if res["success"] and any(file["path"] for file in res["data"]["files"] if remote_folder in file["path"]):
                raise Exception("이미 존재하는 파일입니다")
        except FileStationError as e:
            if e.error_code != 408:
                raise FileStationError(error_code=e.error_code)

        for root, dirs, files in os.walk(local_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if ".cache" in file_path:
                    continue
                dest_path = os.path.join(base_path, target_folder, os.path.relpath(file_path, local_dir))
                dest_path = os.path.split(dest_path)[0]
                fi.upload_file(
                    dest_path=dest_path,
                    file_path=file_path,
                    create_parents=True,
                    overwrite=False,     # default로 False로
                    verify=False,
                    progress_bar=True,
                )
    except Exception as e:
        raise e

import os
from typing import Optional

from datasets import load_from_disk

from .webapi import WebAPI


def download_files(
    webapi: WebAPI,
    remote_path,
    dest_path,
):
    folders = [(remote_path, dest_path)]
    while folders:
        current_folder, current_path = folders.pop(-1)
        res = webapi.get_file_list(folder_path=current_folder)
        for file in res["data"]["files"]:
            if file["isdir"]:
                folders.append((file["path"], os.path.join(current_path, file["name"])))
            else:
                webapi.get_file(
                    path=file["path"],
                    mode="download",
                    dest_path=current_path,
                )


def load_dataset_nas(
    path: str,
    cache_dir: str = ".cache/huggingface_nas/datasets",
    base_path: Optional[str] = None,
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
    cache_dir = os.path.join(os.getenv("HOME", "./"), cache_dir)
    dataset_path = os.path.join(cache_dir, path)

    if not os.path.exists(dataset_path):
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
        remote_folder = os.path.join(base_path, path)
        download_files(
            fi,
            remote_folder,
            dataset_path,
        )

    return load_from_disk(dataset_path)


def prepare_model_from_nas(
    path: str,
    cache_dir: str = ".cache/huggingface_nas/models",
    base_path: Optional[str] = None,
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
) -> str:
    cache_dir = os.path.join(os.getenv("HOME", "./"), cache_dir)
    model_path = os.path.join(cache_dir, path)

    if not os.path.exists(model_path):
        remote_folder = os.path.join(base_path, path)
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
        download_files(
            fi,
            remote_folder,
            model_path,
        )

    return model_path

import io
import os
import sys
from typing import Optional
from urllib import parse

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from synology_api.filestation import FileStation
from tqdm.auto import tqdm


class WebAPI(FileStation):
    def upload_file(self,
                    dest_path: str,
                    file_path: str,
                    create_parents: bool = True,
                    overwrite: bool = True,
                    verify: bool = False,
                    progress_bar: bool = True
                    ) -> str | tuple[int, dict[str, object]]:
        api_name = 'SYNO.FileStation.Upload'
        info = self.file_station_list[api_name]
        api_path = info['path']
        filename = os.path.basename(file_path)

        session = requests.session()

        with open(file_path, 'rb') as payload:
            url = ('%s%s' % (self.base_url, api_path)) + '?api=%s&version=%s&method=upload&_sid=%s' % (
                api_name, info['minVersion'], self._sid)

            encoder = MultipartEncoder({
                'path': dest_path,
                'create_parents': str(create_parents).lower(),
                'overwrite': str(overwrite).lower(),
                'files': (filename, payload, 'application/octet-stream')
            })

            if progress_bar:
                bar = tqdm(
                    desc=f'Uploading {filename}',
                    total=encoder.len,
                    dynamic_ncols=True,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024
                )

                monitor = MultipartEncoderMonitor(encoder, lambda monitor: bar.update(monitor.bytes_read - bar.n))

                r = session.post(
                    url,
                    data=monitor,
                    verify=verify,
                    headers={"X-SYNO-TOKEN": self.session._syno_token, 'Content-Type': monitor.content_type}
                )

            else:
                r = session.post(
                    url,
                    data=encoder,
                    verify=verify,
                    headers={"X-SYNO-TOKEN": self.session._syno_token, 'Content-Type': encoder.content_type}
                )

        session.close()
        if r.status_code != 200 or not r.json()['success']:
            return r.status_code, r.json()

        return r.json()

    def get_file(self,
                 path: str,
                 mode: str,
                 dest_path: str = ".",
                 chunk_size: int = 8192,
                 verify: bool = False
                 ) -> Optional[str]:

        api_name = 'SYNO.FileStation.Download'
        info = self.file_station_list[api_name]
        api_path = info['path']

        if path is None:
            return 'Enter a valid path'

        session = requests.session()

        url = ('%s%s' % (self.base_url, api_path)) + '?api=%s&version=%s&method=download&path=%s&mode=%s&_sid=%s' % (
            api_name, info['maxVersion'], parse.quote_plus(path), mode, self._sid)

        if mode is None:
            return 'Enter a valid mode (open / download)'

        if mode == r'open':
            with session.get(url, stream=True, verify=verify, headers={"X-SYNO-TOKEN": self.session._syno_token}) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        sys.stdout.buffer.write(chunk)

        if mode == r'download':
            with session.get(url, stream=True, verify=verify, headers={"X-SYNO-TOKEN": self.session._syno_token}) as r:
                r.raise_for_status()
                if not os.path.isdir(dest_path):
                    os.makedirs(dest_path)

                file_size = int(r.headers["Content-Length"])

                pbar = tqdm(
                    desc=f"Downloading {os.path.basename(path)}",
                    total=file_size,
                    dynamic_ncols=True,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024
                )
                with open(dest_path + "/" + os.path.basename(path), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            pbar.update(len(chunk))
                pbar.close()

        if mode == r'serve':
            with session.get(url, stream=True, verify=verify, headers={"X-SYNO-TOKEN": self.session._syno_token}) as r:
                r.raise_for_status()
                return io.BytesIO(r.content)

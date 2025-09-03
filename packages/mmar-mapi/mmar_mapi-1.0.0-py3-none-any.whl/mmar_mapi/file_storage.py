import string
from hashlib import md5
from pathlib import Path
from zipfile import ZipFile, is_zipfile


ResourceId = str
ASCII_DIGITS = set(string.ascii_lowercase + string.digits)
SUFFIX_DIR = ".dir"


def _validate_exist(files_dir):
    if not files_dir.exists():
        err = f"Failed to access file-storage directory: {files_dir}"
        raise OSError(err)


def _validate_dtype(dtype: str):
    if all(map(ASCII_DIGITS.__contains__, dtype)):
        return
    raise ValueError(f"Bad dtype: {dtype}")


def generate_fname(content, dtype):
    fname_hash = md5(content).hexdigest()
    fname = f"{fname_hash}.{dtype}"
    return fname


class FileStorage:
    def __init__(self, files_dir):
        self.files_dir = Path(files_dir)
        self.files_dir.mkdir(exist_ok=True, parents=True)
        _validate_exist(self.files_dir)

    def _generate_fname_path(self, content: bytes, dtype: str):
        fpath = self.files_dir / generate_fname(content, dtype)
        return fpath

    def upload_maybe(self, content: bytes | None, dtype: str) -> ResourceId | None:
        if not content:
            return None
        resource_id = self.upload(content, dtype)
        return resource_id

    def upload(self, content: bytes | str, dtype: str) -> ResourceId:
        _validate_dtype(dtype)
        if isinstance(content, str):
            content = content.encode()
        fpath = self._generate_fname_path(content, dtype)
        fpath.write_bytes(content)
        return str(fpath)

    def upload_dir(self, resource_ids: list[ResourceId]) -> ResourceId:
        content = "\n".join(resource_ids)
        res = self.upload(content, "dir")
        return res

    def download(self, resource_id: ResourceId) -> bytes:
        return Path(resource_id).read_bytes()

    def download_text(self, resource_id: ResourceId) -> str:
        return Path(resource_id).read_text(encoding="utf-8")

    def read_dir_or_none(self, resource_id: ResourceId) -> list[ResourceId] | None:
        if not self.is_dir(resource_id):
            return None
        res = self.download_text(resource_id).split("\n")
        return res

    def _get_path(self, resource_id: ResourceId | None) -> Path | None:
        if not resource_id:
            return None
        path = Path(resource_id)
        return path if (path.exists() and path.is_file()) else None

    def is_valid(self, resource_id: ResourceId | None) -> bool:
        path = self._get_path(resource_id)
        return path is not None

    def is_file(self, resource_id: ResourceId | None) -> bool:
        path = self._get_path(resource_id)
        return path and path.suffix != SUFFIX_DIR

    def is_dir(self, resource_id: ResourceId | None) -> bool:
        path = self._get_path(resource_id)
        return path and path.suffix == SUFFIX_DIR

    def get_dtype(self, resource_id: ResourceId | None) -> str | None:
        return resource_id and resource_id.rsplit(".")[-1]

    def unzip_file(self, resource_id: str) -> ResourceId:
        """ takes resource_id which refer to zip-archive, unpacks it and returns directory ResourceId with content of zip-archive """
        path = self._get_path(resource_id)
        if not path:
            raise ValueError(f"Not found path: {resource_id}")
        if not is_zipfile(resource_id):
            raise ValueError(f"Expected zip archive but found: {resource_id}")

        resource_ids = []

        with ZipFile(path, mode='r') as zip_file:
            files_info = zip_file.filelist

            for file_info in zip_file.filelist:
                file_dtype = file_info.filename.rsplit('.')[-1]
                file_bytes = zip_file.read(file_info)
                rid = self.upload(file_bytes, file_dtype)
                resource_ids.append(rid)

        res = self.upload_dir(resource_ids)
        return res
                

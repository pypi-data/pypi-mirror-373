import os
import shutil
import zipfile
import json
from urllib.request import urlopen, Request
import io
from typing import Generator, TypeVar, Any, Optional
import logging

from amulet.utils.task_manager import AbstractProgressManager, VoidProgressManager
from amulet.resource_pack import JavaResourcePack

T = TypeVar("T")

log = logging.getLogger(__name__)

launcher_manifest: Optional[dict] = None
INCLUDE_SNAPSHOT = False


def get_launcher_manifest() -> dict:
    global launcher_manifest
    if launcher_manifest is None:
        log.info("Downloading java launcher manifest file.")
        with urlopen(
            "https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=20
        ) as manifest:
            launcher_manifest = json.load(manifest)
        log.info("Finished downloading java launcher manifest file.")
    return launcher_manifest


def get_latest(
    progress_manager: AbstractProgressManager = VoidProgressManager(),
) -> JavaResourcePack:
    """Download the latest resource pack if required.

    :return: The loaded Java resource pack.
    """
    vanilla_rp_path = os.path.join(
        os.environ["CACHE_DIR"], "resource_packs", "java", "vanilla"
    )
    try:
        if INCLUDE_SNAPSHOT:
            new_version = get_launcher_manifest()["latest"]["snapshot"]
        else:
            new_version = get_launcher_manifest()["latest"]["release"]
    except Exception as e:
        if os.path.isdir(vanilla_rp_path):
            log.error(
                "Could not download the launcher manifest. The resource pack seems to be present so using that."
            )
        else:
            raise e
    else:
        has_new_pack = False
        if os.path.isfile(os.path.join(vanilla_rp_path, "version")):
            with open(os.path.join(vanilla_rp_path, "version")) as f:
                old_version = f.read()
            has_new_pack = old_version == new_version

        if not has_new_pack:
            _remove_and_download(vanilla_rp_path, new_version, progress_manager)
    return JavaResourcePack(vanilla_rp_path)


_java_vanilla_fix: Optional[JavaResourcePack] = None
_java_vanilla_latest: Optional[JavaResourcePack] = None


def get_java_vanilla_fix() -> JavaResourcePack:
    global _java_vanilla_fix
    if _java_vanilla_fix is None:
        _java_vanilla_fix = JavaResourcePack(
            os.path.join(os.path.dirname(__file__), "java_vanilla_fix")
        )
    return _java_vanilla_fix


def get_java_vanilla_latest(
    progress_manager: AbstractProgressManager = VoidProgressManager(),
) -> JavaResourcePack:
    global _java_vanilla_latest
    if _java_vanilla_latest is None:
        _java_vanilla_latest = get_latest(progress_manager)
    return _java_vanilla_latest


def _remove_and_download(
    path: str,
    version: str,
    progress_manager: AbstractProgressManager = VoidProgressManager(),
) -> None:
    # try downloading the new resources to a temporary location
    temp_path = os.path.join(os.path.dirname(path), "_temp_")
    # clear the temporary location
    if os.path.isfile(temp_path):
        os.remove(temp_path)
    elif os.path.isdir(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)

    _download_resources(temp_path, version, progress_manager)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)

    shutil.move(temp_path, path)

    with open(os.path.join(path, "version"), "w") as f:
        f.write(version)


def _download_with_retry(
    url: str,
    chunk_size: int = 4096,
    attempts: int = 5,
    progress_manager: AbstractProgressManager = VoidProgressManager(),
) -> bytes:
    content_length_found = 0
    content = []

    for _ in range(attempts):
        request = Request(url, headers={"Range": f"bytes={content_length_found}-"})
        with urlopen(request, timeout=20) as response:
            content_length = int(response.headers["content-length"].strip())
            while content_length_found < content_length:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                content.append(chunk)
                content_length_found += len(chunk)
                progress_manager.update_progress(
                    min(1.0, content_length_found / content_length)
                )
        if content_length == content_length_found:
            break
    else:
        raise RuntimeError(f"Failed to download")
    return b"".join(content)


def _download_resources(
    path: str,
    version: str,
    progress_manager: AbstractProgressManager = VoidProgressManager(),
    chunk_size: int = 4096,
) -> None:
    log.info(f"Downloading Java resource pack for version {version}")
    version_url = next(
        (v["url"] for v in get_launcher_manifest()["versions"] if v["id"] == version),
        None,
    )
    if version_url is None:
        raise Exception(f"Could not find Java resource pack for version {version}.")

    try:
        with urlopen(version_url, timeout=20) as vm:
            version_manifest = json.load(vm)
        version_client_url = version_manifest["downloads"]["client"]["url"]

        progress_manager_child_1 = progress_manager.get_child(0.0, 0.5)

        data = _download_with_retry(
            version_client_url,
            chunk_size=chunk_size,
            progress_manager=progress_manager_child_1,
        )

        client = zipfile.ZipFile(io.BytesIO(data))
        paths: list[str] = [
            fpath for fpath in client.namelist() if fpath.startswith("assets/")
        ]
        path_count = len(paths)
        progress_manager_child_2 = progress_manager.get_child(0.5, 1.0)
        for path_index, fpath in enumerate(paths):
            if not path_index % 30:
                progress_manager_child_2.update_progress(path_index / path_count)
            if fpath.endswith("/"):
                continue
            os.makedirs(
                os.path.dirname(os.path.abspath(os.path.join(path, fpath))),
                exist_ok=True,
            )
            client.extract(fpath, path)
        if "pack.mcmeta" in client.namelist():
            client.extract("pack.mcmeta", path)
        else:
            # TODO: work out proper version support for this
            with open(os.path.join(path, "pack.mcmeta"), "w") as f:
                f.write(
                    '{"pack": {"description": "The default data for Minecraft","pack_format": 7}}'
                )
        if "pack.png" in client.namelist():
            client.extract("pack.png", path)

    except Exception as e:
        log.error(
            f"Failed to download and extract the Java resource pack for version {version}.",
            exc_info=True,
        )
        raise e
    log.info(f"Finished downloading Java resource pack for version {version}")

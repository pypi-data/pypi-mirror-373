"""Direct asset download.

Downloads assets directly from arknights servers.
Unfortunately assets are stored as unity files, so they need to be extracted.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import pathlib
import re
import shlex
import subprocess
import tempfile
import typing
import warnings
import zipfile

from arkprts import network as netn

from . import base, git

__all__ = ("BundleAssets",)

LOGGER = logging.getLogger("arkprts.assets.bundle")

PathLike = typing.Union[pathlib.Path, str]
# unfortunately UnityPy lacks typing
UnityPyAsset = typing.Any
UnityPyObject = typing.Any

UPDATED_FBS = {"cn": False, "yostar": False, "tw": False}


def _read_extra_length(data: typing.Union[bytes, bytearray, memoryview], cur_pos: int, max_pos: int) -> tuple[int, int]:
    length = 0
    while cur_pos < max_pos:
        b = data[cur_pos]
        length += b
        cur_pos += 1
        if b != 0xFF:
            break
    return length, cur_pos


# https://github.com/isHarryh/Ark-Unpacker/blob/b8b959c7df5a37d172e520c90b1845dac5008880/src/lz4ak/Block.py
# algorithm made by Kengxxiao and adapted by Harry Huang
def decompress_lz4ak(compressed_data: typing.Union[bytes, bytearray, memoryview], uncompressed_size: int) -> bytes:
    """Decompresses the given data block using LZ4AK algorithm."""
    import lz4
    import lz4.block

    ip = 0
    op = 0
    fixed_compressed_data = bytearray(compressed_data)
    compressed_size = len(compressed_data)

    while ip < compressed_size:
        # Sequence token
        literal_length = fixed_compressed_data[ip] & 0xF
        match_length = (fixed_compressed_data[ip] >> 4) & 0xF
        fixed_compressed_data[ip] = (literal_length << 4) | match_length
        ip += 1

        # Literals
        if literal_length == 0xF:
            length, ip = _read_extra_length(fixed_compressed_data, ip, compressed_size)
            literal_length += length
        ip += literal_length
        op += literal_length
        if op >= uncompressed_size:
            break  # End of block

        # Match copy
        offset = (fixed_compressed_data[ip] << 8) | fixed_compressed_data[ip + 1]
        fixed_compressed_data[ip] = offset & 0xFF
        fixed_compressed_data[ip + 1] = (offset >> 8) & 0xFF
        ip += 2
        if match_length == 0xF:
            length, ip = _read_extra_length(fixed_compressed_data, ip, compressed_size)
            match_length += length
        match_length += 4  # Min match
        op += match_length

    return lz4.block.decompress(fixed_compressed_data, uncompressed_size)  # type: ignore


def asset_path_to_server_filename(path: str) -> str:
    """Take a path to a zipped unity asset and return its filename on the server."""
    if path == "hot_update_list.json":
        return path

    filename = path.replace("/", "_").replace("#", "__").rsplit(".", 1)[0] + ".dat"
    return filename


def unzip_only_file(stream: io.BytesIO | bytes) -> bytes:
    """Unzip a single file from a zip archive."""
    if not isinstance(stream, io.BytesIO):
        stream = io.BytesIO(stream)

    with zipfile.ZipFile(stream) as archive:
        return archive.read(archive.namelist()[0])


def resolve_unity_asset_cache(filename: str, server: netn.ArknightsServer) -> pathlib.Path:
    """Resolve a path to a cached arknights ab file."""
    path = netn.TEMP_DIR / "ArknightsAB" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.with_suffix(".ab")


def load_unity_file(stream: io.BytesIO | bytes) -> typing.Sequence[UnityPyAsset]:
    """Load an unzipped arknights unity .ab file."""
    import UnityPy
    import UnityPy.streams

    env: typing.Any = UnityPy.load(io.BytesIO(stream))  # pyright: ignore
    return [
        asset_file
        for bundle_file in env.files.values()
        for asset_file in bundle_file.files.values()
        if not isinstance(asset_file, UnityPy.streams.EndianBinaryReader)  # type: ignore
    ]


def decrypt_aes_text(data: bytes, *, rsa: bool = True) -> bytes:
    """Decrypt aes text."""
    from Crypto.Cipher import AES

    mask = bytes.fromhex("554954704169383270484157776e7a7148524d4377506f6e4a4c49423357436c")

    if rsa:
        data = data[128:]

    aes_key = mask[:16]
    aes_iv = bytearray(b ^ m for b, m in zip(data[:16], mask[16:]))
    aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)  # pyright: ignore[reportUnknownMemberType]

    decrypted_padded = aes.decrypt(data[16:])
    decrypted = decrypted_padded[: -decrypted_padded[-1]]
    return decrypted


def run_flatbuffers(
    fbs_path: PathLike,
    fbs_schema_path: PathLike,
    output_directory: PathLike,
) -> pathlib.Path:
    """Run the flatbuffers cli. Returns the output filename."""
    args = [
        "flatc",
        "-o",
        str(output_directory),
        str(fbs_schema_path),
        "--",
        str(fbs_path),
        "--json",
        "--strict-json",
        "--natural-utf8",
        "--defaults-json",
        "--unknown-json",
        "--raw-binary",
        "--no-warnings",
        "--force-empty",
    ]
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)  # noqa: S603, UP022
    if result.returncode != 0:
        file = pathlib.Path(tempfile.mktemp(".log", dir=netn.TEMP_DIR / "flatbufferlogs"))
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(result.stdout + b"\n\n\n\n" + result.stderr)
        raise ValueError(
            f"flatc failed with code {result.returncode}: {file} `{shlex.join(args)}` (random exit code likely means a faulty FBS file was provided)",
        )

    return pathlib.Path(output_directory) / (pathlib.Path(fbs_path).stem + ".json")


def resolve_fbs_schema_directory(
    server: typing.Literal["cn", "yostar", "tw"],
    prefer_guess: bool = True,
) -> pathlib.Path:
    """Resolve the flatbuffers schema directory."""
    if server == "tw" or (server == "yostar" and prefer_guess):
        return netn.APPDATA_DIR / "ArknightsFlatbuffers" / server

    core_path = netn.APPDATA_DIR / "ArknightsFBS"
    core_path.mkdir(parents=True, exist_ok=True)
    path = core_path / server / "OpenArknightsFBS" / "FBS"
    return path


async def update_fbs_schema(*, force: bool = False) -> None:
    """Download or otherwise update FBS files."""
    for server, branch in [("cn", "main"), ("yostar", "YoStar")]:
        assert server in ("cn", "yostar")  # pyright regression
        if UPDATED_FBS[server] and not force:
            continue

        UPDATED_FBS[server] = True
        directory = resolve_fbs_schema_directory(server, prefer_guess=False).parent
        await git.download_repository("MooncellWiki/OpenArknightsFBS", directory, branch=branch, force=force)

    if not UPDATED_FBS["tw"] or force:
        UPDATED_FBS["tw"] = True
        await git.download_repository(
            "ArknightsAssets/ArknightsFlatbuffers",
            netn.APPDATA_DIR / "ArknightsFlatbuffers",
            force=force,
        )


def recursively_collapse_keys(obj: typing.Any) -> typing.Any:
    """Recursively collapse arknights flatc dictionaries."""
    if isinstance(obj, list):
        obj = typing.cast("typing.Any", obj)
        if all(isinstance(item, dict) and item.keys() == {"key", "value"} for item in obj):
            return {item["key"]: recursively_collapse_keys(item["value"]) for item in obj}

        if all(isinstance(item, dict) and item.keys() == {"Key", "Value"} for item in obj):
            return {item["Key"]: recursively_collapse_keys(item["Value"]) for item in obj}

        return [recursively_collapse_keys(item) for item in obj]

    if isinstance(obj, dict):
        obj = typing.cast("typing.Any", obj)
        return {k: recursively_collapse_keys(v) for k, v in obj.items()}

    return obj


def decrypt_fbs_file(
    data: bytes,
    table_name: str,
    server: netn.ArknightsServer,
    *,
    rsa: bool = True,
    normalize: bool = False,
) -> bytes:
    """Decrypt fbs json file."""
    if rsa:
        data = data[128:]

    tempdir = netn.TEMP_DIR / "ArknightsFBS" / server
    tempdir.mkdir(parents=True, exist_ok=True)

    fbs_path = tempdir / (table_name + ".bytes")
    fbs_path.write_bytes(data)
    ser = "cn" if server in ("cn", "bili") else "tw" if server == "tw" else "yostar"
    fbs_schema_path = resolve_fbs_schema_directory(ser) / (table_name + ".fbs")
    output_directory = tempdir / "output"

    output_path = run_flatbuffers(fbs_path, fbs_schema_path, output_directory)

    parsed_data = output_path.read_text(encoding="utf-8")
    parsed_data = recursively_collapse_keys(json.loads(parsed_data))
    if len(parsed_data) == 1:
        parsed_data, *_ = parsed_data.values()

    return json.dumps(parsed_data, indent=4 if normalize else None, ensure_ascii=False).encode("utf-8")


def decrypt_arknights_text(
    data: bytes,
    name: str,
    server: netn.ArknightsServer,
    *,
    rsa: bool = True,
    normalize: bool = False,
) -> bytes:
    """Decrypt arbitrary arknights data."""
    if match := re.search(r"(\w+_(?:table|data|const|database|text))[0-9a-fA-F]{6}", name):
        return decrypt_fbs_file(data, match[1], rsa=rsa, server=server, normalize=normalize)

    return decrypt_aes_text(data, rsa=rsa)


def load_json_or_bson(data: bytes) -> typing.Any:
    """Load json or possibly bson."""
    if b"\x00" in data[:256]:
        import bson

        return bson.loads(data)  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]

    return json.loads(data)


def normalize_json(data: bytes, *, indent: int = 4, lenient: bool = True) -> bytes:
    """Normalize a json format."""
    if lenient and b"\x00" not in data[:256]:
        return data

    json_data = load_json_or_bson(data)
    return json.dumps(json_data, indent=indent, ensure_ascii=False).encode("utf-8")


def match_container(regex: str, container: str) -> typing.Optional[re.Match[str]]:
    return re.match(r"dyn/" + regex, container) or re.match(r"assets/torappu/dynamicassets/" + regex, container)


def find_ab_assets(
    asset: UnityPyAsset,
    *,
    server: netn.ArknightsServer,
    normalize: bool = False,
) -> typing.Iterable[tuple[str, bytes]]:
    """Yield relative paths and data for a unity asset."""
    for container, obj in asset.container.items():
        if obj.type.name == "TextAsset":
            data = obj.read()
            script, name = data.m_Script.encode("utf-8", "surrogateescape"), data.m_Name

            if match := match_container(r"(.+\.txt)", container):
                yield (match[1], script)

            elif match := match_container(r"((gamedata/)?.+?\.json)", container):
                yield (match[1], normalize_json(bytes(script), lenient=not normalize))

            elif match := match_container(r"(gamedata/.+?)\.lua\.bytes", container):
                text = decrypt_aes_text(script)
                yield (match[1] + ".lua", text)

            elif match := match_container(r"(gamedata/levels/(?:obt|activities)/.+?)\.bytes", container):
                try:
                    text = normalize_json(bytes(script)[128:], lenient=not normalize)
                except UnboundLocalError:  # effectively bson's "type not recognized" error
                    text = decrypt_fbs_file(script, "prts___levels", server=server)

                yield (match[1] + ".json", text)

            elif "gamedata/battle/buff_template_data.bytes" in container:
                text = normalize_json(script)
                yield ("gamedata/battle/buff_template_data.json", text)

            elif match := match_container(r"(gamedata/.+?)(?:[a-fA-F0-9]{6})?\.bytes", container):
                text = decrypt_arknights_text(
                    script,
                    name=name,
                    server=server,
                    normalize=normalize,
                )
                yield (match[1] + ".json", normalize_json(text, lenient=not normalize))

            else:
                warnings.warn(f"Unrecognized container: {container}")


def extract_ab(
    ab_path: PathLike,
    save_directory: PathLike,
    *,
    server: netn.ArknightsServer,
    normalize: bool = False,
) -> typing.Sequence[pathlib.Path]:
    """Extract an AB file and save files. Returns a list of found files."""
    ab_path = pathlib.Path(ab_path)
    save_directory = pathlib.Path(save_directory)
    assets = load_unity_file(ab_path.read_bytes())

    paths: list[pathlib.Path] = []
    for asset in assets:
        for unpacked_rel_path, unpacked_data in find_ab_assets(asset, server=server, normalize=normalize):
            savepath = save_directory / server / unpacked_rel_path
            savepath.parent.mkdir(exist_ok=True, parents=True)
            savepath.write_bytes(unpacked_data)

            LOGGER.debug("Extracted asset %s from %s for server %s", unpacked_rel_path, ab_path.name, server)
            paths.append(savepath)

    return paths


def get_outdated_hashes(hot_update_now: typing.Any, hot_update_before: typing.Any) -> typing.Sequence[str]:
    """Compare hashes and return all files that need to be updated."""
    before_hashes = {info["name"]: info["hash"] for info in hot_update_before["abInfos"]}
    return [info["name"] for info in hot_update_now["abInfos"] if info["hash"] != before_hashes.get(info["name"])]


class BundleAssets(base.Assets):
    """Game assets client downloaded as unity files from arknights servers."""

    network: netn.NetworkSession
    """Network session."""
    directory: pathlib.Path
    """Directory where assets are stored."""

    def __init__(
        self,
        directory: PathLike | None = None,
        *,
        default_server: netn.ArknightsServer | None = None,
        network: netn.NetworkSession | None = None,
        json_loads: typing.Callable[[bytes], typing.Any] = json.loads,
    ) -> None:
        try:
            # ensure optional dependencies have been installed
            import bson  # noqa: F401 # type: ignore
            import Crypto.Cipher.AES  # noqa: F401 # type: ignore
            import PIL  # noqa: F401 # type: ignore
            import UnityPy  # noqa: F401 # type: ignore
        except ImportError as e:
            raise ImportError("Cannot use BundleAssets without arkprts[assets]") from e
        try:
            cmd = ["flatc", "--version"]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)  # noqa: S603
        except OSError as e:
            raise ImportError("Cannot use BundleAssets without a flatc executable") from e

        from UnityPy.helpers import CompressionHelper
        from UnityPy.enums.BundleFile import CompressionFlags

        CompressionHelper.DECOMPRESSION_MAP[CompressionFlags.LZHAM] = decompress_lz4ak

        super().__init__(default_server=default_server or (network and network.default_server), json_loads=json_loads)

        self.directory = pathlib.Path(directory or netn.APPDATA_DIR / "ArknightsResources")
        self.network = network or netn.NetworkSession(default_server=self.default_server)

    async def _download_asset(self, path: str, *, server: netn.ArknightsServer | None = None) -> bytes:
        """Download a raw zipped unity asset."""
        server = server or self.default_server
        if not self.network.versions[server]:
            await self.network.load_version_config(server)

        url = (
            self.network.domains[server]["hu"]
            + f"/Android/assets/{self.network.versions[server]['resVersion']}/"
            + asset_path_to_server_filename(path)
        )

        async with self.network.session.get(url) as response:
            response.raise_for_status()
            return await response.read()

    async def _get_hot_update_list(self, server: netn.ArknightsServer) -> typing.Any:
        """Get a list of files to download."""
        data = await self._download_asset("hot_update_list.json", server=server)
        return json.loads(data)

    def _get_current_hot_update_list(self, server: netn.ArknightsServer) -> typing.Any | None:
        """Get the current stored hot_update_list.json for a server."""
        path = self.directory / server / "hot_update_list.json"
        if not path.exists():
            return None

        try:
            with path.open("r") as file:
                return json.load(file)
        except Exception:
            return None

    async def _download_unity_file(
        self,
        path: str,
        *,
        server: netn.ArknightsServer | None = None,
    ) -> pathlib.Path:
        """Download an asset and return its path."""
        LOGGER.debug("Downloading and unzipping asset %s for server %s", path, server)
        zipped_data = await self._download_asset(path, server=server)
        data = unzip_only_file(zipped_data)
        cache_path = resolve_unity_asset_cache(path, server=server or self.default_server)
        cache_path.write_bytes(data)
        return cache_path

    async def update_assets(
        self,
        *,
        server: netn.ArknightsServer | typing.Literal["all"] | None = None,
        force: bool = False,
        normalize: bool = False,
    ) -> None:
        """Update game data."""
        server = server or self.default_server or "all"
        if server == "all":
            for server in netn.NETWORK_ROUTES:
                await self.update_assets(server=server, force=force, normalize=normalize)

            return

        hot_update_list = await self._get_hot_update_list(server)
        old_hot_update_list = self._get_current_hot_update_list(server)

        requested_names = [
            info["name"] for info in hot_update_list["abInfos"] if info.get("meta") or "gamedata" in info["name"]
        ]
        if old_hot_update_list and not force:
            outdated_names = set(get_outdated_hashes(hot_update_list, old_hot_update_list))
            requested_names = [name for name in requested_names if name in outdated_names]

        await update_fbs_schema()

        # download and extract assets
        ab_file_paths = await asyncio.gather(
            *(self._download_unity_file(name, server=server) for name in requested_names),
        )
        for path in ab_file_paths:
            try:
                extract_ab(path, self.directory, server=server, normalize=normalize)
            except Exception as e:
                LOGGER.exception("Failed to extract asset %s for server %s", path.name, server, exc_info=e)

        # save new hot_update_list
        hot_update_list_path = self.directory / server / "hot_update_list.json"
        hot_update_list_path.parent.mkdir(parents=True, exist_ok=True)
        with hot_update_list_path.open("w") as file:
            json.dump(hot_update_list, file, indent=4, ensure_ascii=False)

        self.loaded = True

    def get_file(self, path: str, *, server: netn.ArknightsServer | None = None) -> bytes:
        """Get an extracted asset file. If server is None any server is allowed with preference for default server."""
        return (self.directory / (server or self.default_server) / path).read_bytes()

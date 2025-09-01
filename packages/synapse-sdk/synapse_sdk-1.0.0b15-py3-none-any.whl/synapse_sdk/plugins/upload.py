import subprocess
import tempfile
from pathlib import Path

from synapse_sdk.i18n import gettext as _
from synapse_sdk.utils.file import calculate_checksum, download_file
from synapse_sdk.utils.storage import get_storage


def archive(source_path, archive_path):
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    command = f'git ls-files --others --exclude-standard --cached  | zip -q --names-stdin {archive_path}'
    subprocess.run(command, cwd=source_path, shell=True, check=True, stdout=subprocess.DEVNULL)


def download_and_upload(source_url, url):
    storage = get_storage(url)
    with tempfile.TemporaryDirectory() as temp_path:
        file_path = str(download_file(source_url, temp_path))
        checksum = calculate_checksum(file_path)
        # TODO 중복 체크
        return storage.upload(file_path, f'dev-{checksum}.zip')


def archive_and_upload(source_path, url):
    storage = get_storage(url)
    dist_path = Path(source_path, 'dist')
    archive_path = dist_path / 'archive.zip'

    archive(source_path, archive_path)
    checksum = calculate_checksum(archive_path)
    checksum_archive_path = dist_path / f'dev-{checksum}.zip'

    if checksum_archive_path.exists():
        # TODO 실제 스토리지 있는지 확인
        return storage.get_url(checksum_archive_path.name)

    archive_path.rename(checksum_archive_path)
    for file_path in dist_path.glob('*.zip'):
        if file_path.name != checksum_archive_path.name:
            file_path.unlink()
    return storage.upload(str(checksum_archive_path), checksum_archive_path.name)


def build_and_upload(source_path, url, virtualenv_path='.venv'):
    storage = get_storage(url)
    dist_path = Path(source_path, 'dist')
    archive_path = dist_path / 'archive.zip'

    archive(source_path, archive_path)
    checksum = calculate_checksum(archive_path)
    checksum_archive_path = dist_path / f'dev-{checksum}.zip'

    if checksum_archive_path.exists():
        # TODO 실제 스토리지 있는지 확인
        wheel_path = next(dist_path.glob('*.whl'), None)
        return storage.get_url(wheel_path.name)

    # wheel file 빌드 진행
    for file_path in dist_path.glob('*.whl'):
        file_path.unlink()

    print(_('Building {}...').format(Path(source_path).name))
    subprocess.run(
        f'{virtualenv_path}/bin/python -m build --wheel',
        cwd=source_path,
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    wheel_path = next(dist_path.glob('*.whl'), None)

    # whl 파일 버전이 동일한 이슈를 해결하기 위해 checksum으로 build명 변경
    checksum_wheel_path = wheel_path.with_name(change_build_from_whl_name(wheel_path.name, checksum))
    wheel_path.rename(checksum_wheel_path)

    archive_path.rename(checksum_archive_path)

    for file_path in dist_path.glob('*.zip'):
        if file_path.name != checksum_archive_path.name:
            file_path.unlink()
    return storage.upload(str(checksum_wheel_path), checksum_wheel_path.name)


def change_build_from_whl_name(whl_name, build):
    components = whl_name.split('-')
    version = components[1].split('+')[0]
    components[1] = f'{version}+{build}'
    return '-'.join(components)

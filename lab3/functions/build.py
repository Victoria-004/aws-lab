import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
STAGE = DIST / "_stage"

FUNCTIONS = {
    "ingest": [],
    "upload_url": [],
    "history": ["pymysql==1.1.1"],
    "processor": ["pymysql==1.1.1"],
}
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def build(name, requirements):
    stage = STAGE / name
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)

    for source in (ROOT / name).glob("*.py"):
        shutil.copy(source, stage / source.name)
    shutil.copytree(ROOT / "common", stage / "common",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    if requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-compile",
                               "--target", str(stage), *requirements])

    archive = DIST / f"{name}.zip"
    files = sorted(p for p in stage.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and ".dist-info" not in str(p))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(stage).as_posix(), date_time=FIXED_TIME)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())
    print(f"{archive.name}: {archive.stat().st_size / 1024:.0f} KB, {len(files)} files")


def main():
    DIST.mkdir(exist_ok=True)
    for name, requirements in FUNCTIONS.items():
        build(name, requirements)
    shutil.rmtree(STAGE, ignore_errors=True)


if __name__ == "__main__":
    main()

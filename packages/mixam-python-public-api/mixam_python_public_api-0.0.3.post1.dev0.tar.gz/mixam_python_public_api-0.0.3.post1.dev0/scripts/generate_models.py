#!/usr/bin/env python3
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen

SCHEMA_URL = "https://mixam.co.uk/v3/api-docs/public"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
SCHEMA_PATH = CACHE / "openapi.public.json"
OUT = ROOT / "src" / "mixam_public_api" / "models.py"

GEN_FLAGS = [
    "--input", str(SCHEMA_PATH),
    "--input-file-type", "openapi",
    "--output", str(OUT),  # models.py (file)
    "--target-python-version", "3.12",
    "--output-model-type", "pydantic_v2.BaseModel",
    "--use-double-quotes",
    "--disable-timestamp",
    "--strict-nullable",
    "--openapi-scopes", "schemas",
    "--use-annotated"
]

# Match a full class header whose base is RootModel[...], across multiple lines.
# We capture leading indent and the class name so we can rebuild a clean header.
_ROOTMODEL_CLASS_HEADER = re.compile(
    r"(?m)^(?P<indent>\s*)class\s+(?P<name>\w+)\s*\(\s*RootModel\s*\[\s*.+?\s*\]\s*\)\s*:\s*$",
    flags=re.DOTALL,
)

_FORWARD_REFS_PATCH = """
# --- Auto-resolve forward refs (added by generator script) ---
try:
    from pydantic import BaseModel, RootModel  # type: ignore
    _g = globals()
    _models = []
    for _name, _obj in list(_g.items()):
        try:
            if isinstance(_obj, type) and issubclass(_obj, (BaseModel, RootModel)) and _obj.__module__ == __name__:
                _models.append(_obj)
        except Exception:
            pass
    for _m in _models:
        try:
            _m.model_rebuild(_types_namespace=_g)  # type: ignore[attr-defined]
        except Exception:
            pass
except Exception:
    pass
# --- End forward refs patch ---
""".lstrip()


def fetch_schema() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    headers = {
        "Accept": "application/json",
        "User-Agent": "mixam-public-api-modelgen/1.0 (+github-actions)",
    }
    req = Request(SCHEMA_URL, headers=headers)
    with urlopen(req, timeout=60) as r:  # nosec
        SCHEMA_PATH.write_bytes(r.read())
    print(f"✓ Schema saved to {SCHEMA_PATH}")


def ensure_pkg_dir() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    init_py = OUT.parent / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# Auto-generated models package.\n", encoding="utf-8")


def _rewrite_rootmodel_bases(src: str) -> str:
    # Replace entire "class X(RootModel[...]):" with "class X(BaseModel):"
    return _ROOTMODEL_CLASS_HEADER.sub(
        lambda m: f"{m.group('indent')}class {m.group('name')}(BaseModel):",
        src,
    )


def _append_forward_refs_patch_if_missing() -> None:
    text = OUT.read_text(encoding="utf-8")
    if "# --- Auto-resolve forward refs" not in text:
        OUT.write_text(text.rstrip() + "\n\n" + _FORWARD_REFS_PATCH, encoding="utf-8")
        print("• Appended forward-ref rebuild patch")


def _compile_sanity() -> None:
    # Fail fast with a helpful snippet if we introduced a syntax issue
    text = OUT.read_text(encoding="utf-8")
    try:
        compile(text, str(OUT), "exec")
    except SyntaxError as e:
        start = max(0, (e.lineno or 1) - 6)
        lines = text.splitlines()
        snippet = "\n".join(
            f"{i+1:>6} | {lines[i]}" for i in range(start, min(len(lines), start + 12))
        )
        raise SystemExit(
            f"\n[compile check] SyntaxError in generated file:\n{e}\n\nContext:\n{snippet}\n"
        )


def post_process() -> None:
    original = OUT.read_text(encoding="utf-8")
    rewritten = _rewrite_rootmodel_bases(original)
    if rewritten != original:
        OUT.write_text(rewritten, encoding="utf-8")
        print("• Rewrote RootModel[...] bases → BaseModel")
    _append_forward_refs_patch_if_missing()
    _compile_sanity()


def main() -> int:
    fetch_schema()
    ensure_pkg_dir()
    cmd = [sys.executable, "-m", "datamodel_code_generator"] + GEN_FLAGS
    print("→ Running:", " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        print("Model Build Failed", OUT)
        return rc

    post_process()
    print("Models Generated At:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import os
import re
from typing import Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

_ENV_NAME_RE = re.compile(r"^\$?[A-Z_][A-Z0-9_]*$")

def _normalize_discover_arg(discover_packages) -> str | None:
    """
    Accepts: None | bool | str | list[str]
    - None/True  -> infer from project (return None to indicate 'infer')
    - False      -> explicitly disable discovery (return "")
    - "true"/"false" (strings) -> treated like booleans (agent sometimes sends these)
    - str       -> trimmed as-is (CSV)
    - list      -> comma-joined
    """
    if isinstance(discover_packages, str):
        low = discover_packages.strip().lower()
        if low in ("true", "1", "yes"):
            return None
        if low in ("false", "0", "no"):
            return ""
        return discover_packages.strip()

    if discover_packages is None or discover_packages is True:
        return None
    if discover_packages is False:
        return ""
    if isinstance(discover_packages, (list, tuple)):
        return ",".join(x.strip() for x in discover_packages if str(x).strip())
    return str(discover_packages).strip()

def _resolve_ini_url_value(database_url: Optional[str]) -> str:
    """
    For alembic.ini:
    - If a literal URL is passed -> write it.
    - If an ENV name like 'DATABASE_URL' or '$DATABASE_URL' or None -> write empty string,
      and let env.py override from os.getenv at runtime.
    """
    if not database_url:
        return ""
    if _ENV_NAME_RE.fullmatch(database_url):
        return ""
    return database_url

def _get_env_value_from_name(name: str) -> Optional[str]:
    """
    If name looks like an env var (DATABASE_URL or $DATABASE_URL), return its os.getenv value.
    Otherwise return the name itself (assume literal URL).
    """
    if not name:
        return None
    if _ENV_NAME_RE.fullmatch(name):
        key = name[1:] if name.startswith("$") else name
        return os.getenv(key)
    return name  # literal URL

def _ensure_sslmode_required(url: str) -> str:
    """
    If URL is Postgres and has no sslmode, add sslmode=require for common managed hosts.
    No change for non-Postgres URLs.
    """
    if not url:
        return url
    parsed = urlparse(url)
    scheme = parsed.scheme or ""
    if not scheme.startswith("postgres"):
        return url

    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in q:
        # Heuristic: managed PGs often require SSL. Safe to default to require.
        q["sslmode"] = "require"

    new_query = urlencode(q, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def _normalize_db_url_for_alembic(url: Optional[str]) -> Optional[str]:
    """
    Normalize DB url for Alembic tooling (not env.py mapping).
    - Keep as-is for most cases.
    - If postgres async driver is present, we still let env.py downshift to psycopg2.
    - Ensure sslmode=require for Postgres if missing.
    """
    if not url:
        return url
    # normalize postgres:// -> postgresql:// (some clients output postgres://)
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return _ensure_sslmode_required(url)

def _load_dotenv_if_present(project_root) -> None:
    """
    Load .env from the project root if present. No hard dependency on python-dotenv.
    Silently no-op if python-dotenv is not installed.
    """
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    from pathlib import Path
    root = Path(project_root).resolve()
    for candidate in (root / ".env", root.parent / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)
            break
# rattingtax/esi.py
import logging
from typing import Iterable, Tuple, Optional
from datetime import datetime, timezone as dt_tz
from decimal import Decimal
from esi.clients import EsiClientProvider

ESI_BASE = "https://esi.evetech.net/latest"
esi = EsiClientProvider()
logger = logging.getLogger(__name__)


def _to_utc_dt(val):
    """Accept ISO8601 string or datetime and return timezone-aware UTC datetime, else None."""
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=dt_tz.utc)
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=dt_tz.utc)
        except Exception:
            return None
    return None


def _result_with_optional_response(op) -> Tuple[object, Optional[object]]:
    """Call op.result() handling both return shapes: data or (data, response)."""
    try:
        data, resp = op.result(with_response=True)  # some clients support this kwarg
        return data, resp
    except TypeError:
        pass
    except ValueError:
        pass

    out = op.result()
    if isinstance(out, tuple) and len(out) == 2:
        data, resp = out
        return data, resp
    return out, None


def _authed_headers(token):
    """Return Authorization header using a valid access token (auto-refresh if needed)."""
    try:
        at = token.valid_access_token()  # django-esi refreshes if expired
        return {"Authorization": f"Bearer {at}"}
    except Exception:
        logger.exception("Could not obtain a valid access token for token id=%s", getattr(token, "id", "n/a"))
        raise


def iter_corp_wallet_journal(token, corporation_id: int, division: int = 1) -> Iterable[dict]:
    """
    Iterate corporation wallet journal entries for a given division, newest→older.
    Uses token.valid_access_token() (auto-refresh) and retries once on 401.
    Honors X-Pages when provided; otherwise paginates until a short page.
    """
    def fetch_page(page: int, headers):
        op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
            corporation_id=corporation_id,
            division=division,
            page=page,
            _request_options={"headers": headers},
        )
        return _result_with_optional_response(op)

    # --- first page ---
    headers = _authed_headers(token)
    try:
        data, resp = fetch_page(1, headers)
    except Exception as e:
        code = getattr(e, "status", None) or getattr(e, "status_code", None)
        if code == 401:
            # one-shot retry with a fresh token
            headers = _authed_headers(token)
            data, resp = fetch_page(1, headers)
        else:
            logger.warning("Wallet journal fetch failed: corp=%s div=%s page=1 code=%s", corporation_id, division, code)
            return

    if not data:
        return

    for row in data:
        yield row

    # How many pages?
    total_pages = None
    try:
        if resp and hasattr(resp, "headers"):
            total_pages = int(resp.headers.get("X-Pages", "1"))
    except Exception:
        total_pages = None

    # --- remaining pages ---
    if total_pages and total_pages > 1:
        for page in range(2, total_pages + 1):
            try:
                data, _ = fetch_page(page, headers)
            except Exception as e:
                code = getattr(e, "status", None) or getattr(e, "status_code", None)
                logger.warning("Wallet journal fetch failed: corp=%s div=%s page=%s code=%s",
                               corporation_id, division, page, code)
                break
            if not data:
                break
            for row in data:
                yield row
    else:
        # fallback heuristic pagination when X-Pages missing
        page = 2
        while True:
            try:
                data, _ = fetch_page(page, headers)
            except Exception as e:
                code = getattr(e, "status", None) or getattr(e, "status_code", None)
                logger.warning("Wallet journal fetch failed: corp=%s div=%s page=%s code=%s",
                               corporation_id, division, page, code)
                break
            if not data:
                break
            for row in data:
                yield row
            if len(data) < 1000:  # ESI page size is typically 1000
                break
            page += 1


def fetch_corp_public(corp_id: int) -> dict:
    """Fetch public corporation info."""
    return esi.client.Corporation.get_corporations_corporation_id(
        corporation_id=corp_id
    ).result()

def corp_logo_url(corp_id: int, size: int = 128) -> str:
    """Build CCP image server URL for corp logo."""
    return f"https://images.evetech.net/corporations/{corp_id}/logo?size={size}"


import logging
from typing import Iterator
import requests
from django.utils import timezone
from datetime import datetime

from esi.clients import EsiClientProvider

logger = logging.getLogger(__name__)

ESI_BASE = "https://esi.evetech.net/latest"
esi = EsiClientProvider()

def fetch_corp_public(corp_id: int) -> dict:
    """Fetch public corporation info."""
    return esi.client.Corporation.get_corporations_corporation_id(
        corporation_id=corp_id
    ).result()

def corp_logo_url(corp_id: int, size: int = 128) -> str:
    """Build CCP image server URL for corp logo."""
    return f"https://images.evetech.net/corporations/{corp_id}/logo?size={size}"

def _to_utc_dt(date_str: str):
    """Parse ESI datetime string into a timezone-aware UTC datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None

def iter_corp_wallet_journal(token, corporation_id: int, division: int = 1) -> Iterator[dict]:
    """
    Iterate through all pages of a corporation wallet journal division.

    This function:
    - Requests division pages until the end.
    - Uses 'X-Pages' header if provided to determine total pages.
    - Falls back to probing sequential pages until no data is returned.
    - Yields raw rows (dicts) from ESI.

    Args:
        token: django-esi Token instance (with access_token).
        corporation_id: ID of the corporation.
        division: Wallet division number (1–7).
    """
    headers = {"Authorization": f"Bearer {token.access_token}"}
    base_url = f"{ESI_BASE}/corporations/{corporation_id}/wallets/{division}/journal/"

    # Try to detect number of pages via X-Pages
    page = 1
    max_pages = None

    while True:
        resp = requests.get(base_url, headers=headers, params={"page": page})
        if resp.status_code == 404:
            break
        if resp.status_code != 200:
            logger.warning("Wallet journal fetch failed: corp=%s div=%s page=%s code=%s",
                           corporation_id, division, page, resp.status_code)
            break

        try:
            rows = resp.json()
        except Exception:
            logger.exception("Failed to decode JSON for corp=%s div=%s page=%s",
                             corporation_id, division, page)
            break

        if not rows:
            break

        for row in rows:
            yield row

        if max_pages is None:
            try:
                max_pages = int(resp.headers.get("X-Pages", ""))
            except Exception:
                max_pages = None

        if max_pages and page >= max_pages:
            break

        page += 1

def sum_corp_bounty_tax_for_month(token, corporation_id: int, year: int, month: int):
    """
    Diagnostic helper: iterate wallet journals directly from ESI and sum accepted ref_types
    for the given month. This is NOT used in production anymore once DB ingestion is enabled,
    but remains useful for testing and debugging.

    Returns: (total Decimal, debug_sample_rows)
    """
    from decimal import Decimal
    accepted = {"bounty_prizes", "bounty_prize", "ess_escrow_payment"}
    sample_rows = []

    total = Decimal("0")
    for division in range(1, 8):
        for row in iter_corp_wallet_journal(token, corporation_id, division=division):
            dt = _to_utc_dt(row.get("date"))
            if not dt:
                continue
            if dt.year != year or dt.month != month:
                continue
            ref_type = (row.get("ref_type") or "").strip().lower()
            if ref_type not in accepted:
                continue
            try:
                amt = Decimal(str(row.get("amount")))
            except Exception:
                continue
            total += amt
            if len(sample_rows) < 5:
                sample_rows.append(row)

    return total, sample_rows

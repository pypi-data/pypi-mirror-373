import logging
from decimal import Decimal
from datetime import datetime
from calendar import monthrange

from celery import shared_task
from django.utils import timezone
from django.db import transaction, connections
from django.core.exceptions import FieldError

from esi.models import Token

from .models import (
    Corporation,
    CorpMonthStat,
    CorpTokenLink,
    CorpJournalEntry,
)
from .esi import iter_corp_wallet_journal, _to_utc_dt

logger = logging.getLogger(__name__)

# Accepted ref_types to count – normalized to lowercase before comparison
ACCEPTED_REF_TYPES = {
    "bounty_prizes",
    "bounty_prize",
    "ess_escrow_payment",
}


# ----------------
# HELPERS
# ----------------

def _month_bounds(year: int, month: int):
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


def _normalize_ref_type(ref_type: str) -> str:
    return (ref_type or "").strip().lower()


def _get_token_for_corp(corp: Corporation):
    """
    Return newest django-esi Token for any character linked to this corp
    that HAS the required corp-wallet scope. Fallback to newest-any if none found.
    """
    REQUIRED_SCOPE = "esi-wallet.read_corporation_wallets.v1"

    char_ids = list(
        CorpTokenLink.objects.filter(corp=corp).values_list("character_id", flat=True)
    )
    if not char_ids:
        return None

    try:
        # 1) prefer tokens, które mają właściwy scope (join po nazwie scopa)
        qs_scoped = (
            Token.objects
            .filter(character_id__in=char_ids, scopes__name=REQUIRED_SCOPE)
            .distinct()
        )
        tok = qs_scoped.order_by("-created").first()
        if tok:
            return tok

        # 2) fallback – najnowszy dowolny token (może skończyć się 401/403)
        logger.warning(
            "No token with scope %s for corp %s; falling back to newest-any token",
            REQUIRED_SCOPE, corp.corporation_id
        )
        qs_any = Token.objects.filter(character_id__in=char_ids)
        try:
            return qs_any.order_by("-created").first()
        except FieldError:
            return qs_any.order_by("-id").first()
    except Exception as e:
        logger.exception("Token lookup failed for corp %s: %s", corp.corporation_id, e)
        return None



# ----------------
# INGEST (with diagnostics)
# ----------------

def ingest_corp_journal_since(token, corp_pk: int, eve_corporation_id: int, cutoff_dt: datetime) -> dict:
    """
    Ingest wallet journal rows since cutoff_dt (inclusive), per division (1..7).
    Stops iterating a division once a row older than cutoff is reached.
    Only inserts rows with ref_type in ACCEPTED_REF_TYPES.

    Returns dict with diagnostics:
      {
        "total_attempts": int,         # total rows batched (accepted) across divisions
        "total_inserted": int,         # rows actually inserted (bulk + fallback)
        "per_div": { div: {"attempts": int, "inserted": int, "pre_count": int, "post_count": int} }
      }
    """
    diag = {"total_attempts": 0, "total_inserted": 0, "per_div": {}}

    for division in range(1, 8):
        # count before
        pre_count = CorpJournalEntry.objects.filter(
            corp_id=corp_pk, division=division, date__gte=cutoff_dt
        ).count()

        batch = []
        for row in iter_corp_wallet_journal(token, eve_corporation_id, division=division):
            dt = _to_utc_dt(row.get("date"))
            if not dt:
                continue
            # ESI returns newest first — bail out below cutoff
            if dt < cutoff_dt:
                break

            ref_type = _normalize_ref_type(row.get("ref_type"))
            if ref_type not in ACCEPTED_REF_TYPES:
                continue

            try:
                amount = Decimal(str(row.get("amount")))
            except Exception:
                continue

            jid = row.get("id") or row.get("journal_id")
            context_id = row.get("context_id")
            reason = row.get("reason") or ""

            batch.append(CorpJournalEntry(
                corp_id=corp_pk,           # FK to our Corporation table (PK)
                division=division,
                journal_id=jid,
                date=dt,
                ref_type=ref_type,
                amount=amount,
                context_id=context_id,
                reason=reason,
            ))

        attempts = len(batch)
        diag["total_attempts"] += attempts
        inserted = 0

        if attempts:
            # helpful sample in logs
            sample = batch[0]
            logger.debug(
                "Division %s sample: jid=%s ref=%s dt=%s amt=%s",
                division, sample.journal_id, sample.ref_type, sample.date, sample.amount
            )

            # First try bulk insert (fast path)
            try:
                CorpJournalEntry.objects.bulk_create(batch, ignore_conflicts=True)
            except Exception as e:
                logger.warning(
                    "bulk_create failed corp=%s div=%s: %s – falling back to get_or_create",
                    eve_corporation_id, division, e
                )
                # fallback to row-by-row
                for ent in batch:
                    try:
                        _, created = CorpJournalEntry.objects.get_or_create(
                            corp_id=ent.corp_id,
                            division=ent.division,
                            journal_id=ent.journal_id,
                            defaults=dict(
                                date=ent.date,
                                ref_type=ent.ref_type,
                                amount=ent.amount,
                                context_id=ent.context_id,
                                reason=ent.reason,
                            ),
                        )
                        if created:
                            inserted += 1
                    except Exception:
                        # ignore one-off failures
                        continue

            # measure after bulk (or after fallback)
            post_count = CorpJournalEntry.objects.filter(
                corp_id=corp_pk, division=division, date__gte=cutoff_dt
            ).count()

            # if bulk succeeded but no fallback was used, infer inserted = delta
            if inserted == 0:
                inserted = max(0, post_count - pre_count)

            diag["total_inserted"] += inserted
            diag["per_div"][division] = {
                "attempts": attempts,
                "inserted": inserted,
                "pre_count": pre_count,
                "post_count": post_count,
            }
            logger.info(
                "Ingest corp=%s div=%s attempts=%s inserted=%s (pre=%s → post=%s)",
                eve_corporation_id, division, attempts, inserted, pre_count, post_count
            )
        else:
            diag["per_div"][division] = {"attempts": 0, "inserted": 0, "pre_count": pre_count, "post_count": pre_count}

    return diag


# ----------------
# AGGREGATION
# ----------------

def aggregate_month(corp: Corporation, year: int, month: int) -> Decimal:
    start, end = _month_bounds(year, month)
    qs = (
        CorpJournalEntry.objects
        .filter(
            corp=corp,
            date__gte=start,
            date__lte=end,
            ref_type__in=ACCEPTED_REF_TYPES,
        )
        .values_list("amount", flat=True)
    )
    total = sum(qs, Decimal("0"))
    return total


# ----------------
# TASKS
# ----------------

@shared_task(bind=True, ignore_result=True)
def pull_month_for_corp(self, corporation_id: int, year: int, month: int):
    from django.conf import settings
    logger.info("DB default ENGINE=%s NAME=%s", settings.DATABASES["default"]["ENGINE"], settings.DATABASES["default"]["NAME"])

    now = timezone.now()
    is_current = (year == now.year and month == now.month)
    logger.info("Running pull_month_for_corp corp=%s y-m=%s-%s", corporation_id, year, month)

    try:
        corp = Corporation.objects.get(corporation_id=corporation_id)
    except Corporation.DoesNotExist:
        logger.warning("pull_month_for_corp: corp %s does not exist", corporation_id)
        return

    token = _get_token_for_corp(corp)
    if not token:
        logger.warning("pull_month_for_corp: no token for corp %s", corporation_id)
        return

    start, _ = _month_bounds(year, month)

    # 1) INGEST with diagnostics
    try:
        # pass both corp PK (FK) and EVE corporation_id (for ESI)
        diag = ingest_corp_journal_since(token, corp.pk, corp.corporation_id, start)
        logger.debug("Ingest diag: %s", diag)
        logger.info(
            "Ingest summary corp=%s y-m=%s-%s attempts=%s inserted=%s",
            corporation_id, year, month, diag["total_attempts"], diag["total_inserted"]
        )
    except Exception as e:
        logger.exception("ingest failed corp=%s y-m=%s-%s: %s",
                         corporation_id, year, month, e)
        return

    # 2) AGGREGATE
    total = aggregate_month(corp, year, month)
    logger.info("Aggregate corp=%s y-m=%s-%s total=%s", corporation_id, year, month, total)

    # 3) SAVE STAT
    with transaction.atomic():
        stat, _ = CorpMonthStat.objects.select_for_update().get_or_create(
            corp=corp, year=year, month=month, defaults={"corp_bounty_tax_amount": total}
        )

        is_closed = getattr(stat, "closed", False)

        if is_closed and not is_current:
            logger.info("Month is closed for corp=%s y-m=%s-%s – skipping update", corporation_id, year, month)
            return

        changed = (stat.corp_bounty_tax_amount != total)
        stat.corp_bounty_tax_amount = total

        if not is_current:
            if hasattr(stat, "closed"):
                stat.closed = True
                stat.save(update_fields=["corp_bounty_tax_amount", "closed"])
            else:
                stat.save(update_fields=["corp_bounty_tax_amount"])
        else:
            if hasattr(stat, "closed") and stat.closed:
                stat.closed = False
                stat.save(update_fields=["corp_bounty_tax_amount", "closed"])
            elif changed:
                stat.save(update_fields=["corp_bounty_tax_amount"])

    logger.info("pull_month_for_corp finished corp=%s y-m=%s-%s", corporation_id, year, month)


@shared_task(bind=True, ignore_result=True)
def daily_refresh_current_month(self):
    now = timezone.now()
    y, m = now.year, now.month
    for link in CorpTokenLink.objects.select_related("corp").all():
        corp = link.corp
        tok = _get_token_for_corp(corp)
        if not tok:
            logger.info("daily_refresh_current_month: no token for corp %s", corp.corporation_id)
            continue
        logger.info("Queue pull: corp=%s year=%s month=%s", corp.corporation_id, y, m)
        pull_month_for_corp.delay(corp.corporation_id, y, m)


@shared_task(bind=True, ignore_result=True)
def close_previous_months(self):
    """
    Queue a pull for the previous month for all corporations that have a token.
    pull_month_for_corp sam ustawi 'closed=True' dla miesięcy nie-bieżących.
    """
    now = timezone.now()
    y, m = now.year, now.month
    prev_y, prev_m = (y, m - 1) if m > 1 else (y - 1, 12)

    queued = 0
    for link in CorpTokenLink.objects.select_related("corp").all():
        corp = link.corp
        tok = _get_token_for_corp(corp)
        if not tok:
            logger.info("close_previous_months: no token for corp %s", corp.corporation_id)
            continue
        pull_month_for_corp.delay(corp.corporation_id, prev_y, prev_m)
        queued += 1

    logger.info("close_previous_months queued %s corp-month pulls for %04d-%02d", queued, prev_y, prev_m)

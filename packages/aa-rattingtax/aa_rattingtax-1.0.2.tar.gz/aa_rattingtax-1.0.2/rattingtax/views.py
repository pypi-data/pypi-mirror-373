from decimal import Decimal
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _t
from django.utils import timezone
from django.utils.formats import date_format

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required
from esi.clients import EsiClientProvider

from .models import Corporation, CorpTokenLink, TaxConfig, CorpMonthStat, AllianceSettings
from .tasks import pull_month_for_corp
from .esi import fetch_corp_public, corp_logo_url

logger = get_extension_logger(__name__)
esi = EsiClientProvider()

APP_LABEL = "rattingtax"
PERM_VIEW_ALL = f"{APP_LABEL}.view_all"
PERM_BASIC = f"{APP_LABEL}.basic_access"


def _fmt_percent(dec: Decimal) -> str:
    """Return '10' for 10.00; keep up to 2 decimals otherwise (e.g., '10.5')."""
    if dec == dec.to_integral_value():
        return str(int(dec))
    return ('{:f}'.format(dec.quantize(Decimal('0.01'))).rstrip('0').rstrip('.'))


def _visible_corps(user):
    """
    Corporations visible to the user:
    - users with rattingtax.view_all see all corporations
    - others see only corporations linked via CorpTokenLink to their characters
    """
    if user.has_perm(PERM_VIEW_ALL):
        return Corporation.objects.all()

    char_ids = (
        user.character_ownerships.values_list("character_id", flat=True)
    )
    corp_ids = (
        CorpTokenLink.objects.filter(character_id__in=char_ids)
        .values_list("corp_id", flat=True)
    )
    return Corporation.objects.filter(id__in=corp_ids)


@login_required
@permission_required(PERM_BASIC, raise_exception=True)
def dashboard(request):
    """
    Dashboard with filters for corp / year / month.
    Rows are built from CorpMonthStat (ingested & aggregated by tasks).
    """
    corps = list(_visible_corps(request.user).order_by("name"))

    # Build available (year, month) pairs from existing stats for visible corps
    avail = (
        CorpMonthStat.objects
        .filter(corp__in=corps)
        .values_list("year", "month")
        .distinct()
        .order_by("-year", "-month")
    )
    years = sorted({y for y, m in avail}, reverse=True)
    months_for_year = {}
    for y, m in avail:
        months_for_year.setdefault(y, set()).add(m)

    now = timezone.now()

    # Selected filters (fallback to "latest available" or current)
    selected_year = int(request.GET.get("year") or (years[0] if years else now.year))
    months = sorted(months_for_year.get(selected_year, {now.month}), reverse=True)
    selected_month = int(request.GET.get("month") or (months[0] if months else now.month))

    # Month options with localized month names (e.g., "sierpień")
    month_options = [
        {"value": m, "label": date_format(date(selected_year, m, 1), "F")}
        for m in months
    ]

    # Filter by EVE corporation_id if provided
    try:
        selected_corp = int(request.GET.get("corp") or 0)
    except ValueError:
        selected_corp = 0

    stats_qs = CorpMonthStat.objects.filter(
        year=selected_year, month=selected_month, corp__in=corps
    )
    if selected_corp:
        stats_qs = stats_qs.filter(corp__corporation_id=selected_corp)

    stats = list(stats_qs.select_related("corp").order_by("corp__name"))

    # Alliance/global settings (rate and flat reduction) as Decimals
    try:
        settings_obj = AllianceSettings.get_solo()
        alliance_rate = Decimal(settings_obj.alliance_rate_percent or 0)      # e.g. 10.00 (%)
        tax_reduction = Decimal(settings_obj.flat_tax_reduction or 0)         # flat ISK
    except Exception:
        s = AllianceSettings.objects.first()
        alliance_rate = Decimal(getattr(s, "alliance_rate_percent", 0) or 0) if s else Decimal("0")
        tax_reduction = Decimal(getattr(s, "flat_tax_reduction", 0) or 0) if s else Decimal("0")

    # Cache for corp public info to avoid duplicate ESI calls
    corp_pub_cache = {}

    # Build table rows
    rows = []
    for st in stats:
        corp = st.corp
        corp_amount = st.corp_bounty_tax_amount or Decimal("0")  # Decimal from DB

        # Corp tax rate from ESI (in-game corp tax)
        corp_pub = corp_pub_cache.get(corp.corporation_id)
        if corp_pub is None:
            try:
                corp_pub = fetch_corp_public(corp.corporation_id)
            except Exception:
                logger.warning("Failed to fetch corp public for %s", corp.corporation_id, exc_info=True)
                corp_pub = {}
            corp_pub_cache[corp.corporation_id] = corp_pub

        raw_rate = corp_pub.get("tax_rate", 0) or 0  # ESI returns fraction (e.g., 0.1)
        corp_rate_pct = (Decimal(str(raw_rate)) * Decimal("100")).quantize(Decimal("1"))
        corp_rate_display = str(int(corp_rate_pct))  # e.g., '10'

        # Alliance tax = max( (corp_amount * alliance_rate%) - tax_reduction, 0 )
        alliance_tax_raw = (corp_amount * (alliance_rate / Decimal("100")))
        alliance_tax = alliance_tax_raw - tax_reduction
        if alliance_tax < 0:
            alliance_tax = Decimal("0")
        alliance_tax = alliance_tax.quantize(Decimal("0.01"))

        rows.append({
            "corp": corp,
            "corp_tax_amount": f"{corp_amount:,.2f}",
            "corp_rate": corp_rate_display,              # e.g., '10'
            "alliance_rate": _fmt_percent(alliance_rate),# e.g., '50' (not '50.00')
            "alliance_tax": f"{alliance_tax:,.2f}",
        })

    context = {
        "corps": corps,
        "years": years or [now.year],
        "months": [opt["value"] for opt in month_options] or [now.month],  # for backward-compat in template logic
        "month_options": month_options,  # preferred: use this for labels
        "selected_year": selected_year,
        "selected_month": selected_month,
        "selected_corp": selected_corp or "",
        "rows": rows,
        "tax_reduction": f"{tax_reduction:,.2f}",
    }
    # IMPORTANT: template should use {% block details %} (base.html defines 'details')
    return render(request, "rattingtax/dashboard.html", context)


@login_required
@permission_required(PERM_BASIC, raise_exception=True)
def pull_history(request, corp_id, year, month):
    """
    Manually queue a pull for a historical month for a specific corporation.
    """
    try:
        corp = Corporation.objects.get(pk=corp_id)
    except Corporation.DoesNotExist:
        messages.error(request, _t("Corporation not found."))
        return redirect("rattingtax:dashboard")

    # Visibility guard for non-view_all users
    if not request.user.has_perm(PERM_VIEW_ALL):
        visible_ids = set(_visible_corps(request.user).values_list("id", flat=True))
        if corp.id not in visible_ids:
            messages.error(request, _t("You don’t have access to this corporation."))
            return redirect("rattingtax:dashboard")

    pull_month_for_corp.delay(corp.corporation_id, int(year), int(month))
    messages.success(request, _t("Pull queued for %(corp)s %(y)s-%(m)s.") % {
        "corp": corp.name, "y": year, "m": str(month).zfill(2)
    })
    return redirect("rattingtax:dashboard")


@login_required
@permission_required(PERM_BASIC, raise_exception=True)
@token_required(scopes=["esi-wallet.read_corporation_wallets.v1"])
def connect_corp_token(request, token):
    """
    Link the selected token's character to its corporation and queue initial sync.
    Does NOT rely on token.character (django-esi Token doesn't have it).
    """
    try:
        char_id = token.character_id
        char_name = getattr(token, "character_name", None)

        # Resolve corporation id:
        corp_id = None
        try:
            ownership = CharacterOwnership.objects.select_related("character").get(
                character__character_id=char_id
            )
            corp_id = getattr(ownership.character, "corporation_id", None)
        except CharacterOwnership.DoesNotExist:
            pass

        if not corp_id:
            # fallback via ESI (characters → corporation_id)
            char_resp = esi.client.Character.get_characters_character_id(
                character_id=char_id
            ).result()
            corp_id = char_resp["corporation_id"]

        # Fetch public corp info for display/name freshness (optional but nice)
        corp_pub = fetch_corp_public(corp_id)
        corp_name = corp_pub.get("name") or f"Corporation {corp_id}"

        # Upsert Corporation
        corp, _ = Corporation.objects.get_or_create(
            corporation_id=corp_id,
            defaults={"name": corp_name},
        )
        if corp.name != corp_name:
            corp.name = corp_name
            corp.save(update_fields=["name"])

        # Upsert link token→corp (add more fields if your model has them)
        CorpTokenLink.objects.update_or_create(
            corp=corp,
            character_id=char_id,
            defaults={},
        )

        # Queue current month sync
        now = timezone.now()
        y, m = now.year, now.month
        pull_month_for_corp.delay(corp.corporation_id, y, m)

        messages.success(
            request,
            f"Linked token for {corp.name}. Initial sync queued." + (f" ({char_name})" if char_name else "")
        )
    except Exception:
        logger.exception("connect_corp_token failed")
        messages.error(request, "Error while connecting corp token.")

    return redirect("rattingtax:dashboard")

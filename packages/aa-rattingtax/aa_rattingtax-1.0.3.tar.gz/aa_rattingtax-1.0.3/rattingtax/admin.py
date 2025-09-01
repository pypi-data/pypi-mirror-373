from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import AllianceSettings

# Keep admin minimal: only a single global setting for alliance tax rate.
@admin.register(AllianceSettings)
class AllianceSettingsAdmin(SingletonModelAdmin):
    """Edit the single global AllianceSettings instance from admin."""
    fieldsets = (
        ("Alliance tax", {
            "fields": ("alliance_rate_percent", "flat_tax_reduction"),
            "description": (
                "Alliance rate is % of corporation-month total. "
                "Flat tax reduction is subtracted from the computed alliance tax per corporation."
            ),
        }),
    )

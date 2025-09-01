# rattingtax/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

class Corporation(models.Model):
    corporation_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=128)
    ticker = models.CharField(max_length=16, blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ("basic_access", "Can use ratting tax module"),
            ("view_all", "Can view all corporations in RattingTax"),
        ]

    def __str__(self):
        return f"{self.name} [{self.ticker}]" if self.ticker else self.name


class TaxConfig(models.Model):
    corp = models.OneToOneField(Corporation, on_delete=models.CASCADE, related_name="tax_cfg")
    corp_tax_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f"{self.corp} (corp {self.corp_tax_rate_percent}%)"


class CorpMonthStat(models.Model):
    corp = models.ForeignKey(Corporation, on_delete=models.CASCADE, related_name="month_stats")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    corp_bounty_tax_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closed = models.BooleanField(default=False, help_text="When true, month is frozen and not recalculated.")


    class Meta:
        default_permissions = ()
        unique_together = ("corp", "year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.corp} {self.year}-{self.month:02d}: {self.corp_bounty_tax_amount}"


class CorpTokenLink(models.Model):
    corp = models.OneToOneField(Corporation, on_delete=models.CASCADE, related_name="token_link")
    character_id = models.BigIntegerField()
    character_name = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f"{self.corp} via {self.character_name}"


class AllianceSettings(SingletonModel):
    """
    Global module settings:
    - alliance_rate_percent: percentage (0–100) the alliance takes from corp bounty tax
    - flat_tax_reduction: flat reduction applied
    """
    alliance_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    flat_tax_reduction = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = "Alliance Settings"
        default_permissions = ()

    def __str__(self):
        return "Alliance Settings"
    
    
class CorpJournalEntry(models.Model):
    """
    Stores individual corporation wallet journal entries that are relevant
    for tax calculations. Ingested incrementally from ESI.
    """
    corp = models.ForeignKey(Corporation, on_delete=models.CASCADE, related_name="journal_entries")
    division = models.PositiveSmallIntegerField()
    journal_id = models.BigIntegerField(null=True, blank=True)
    date = models.DateTimeField(db_index=True)
    ref_type = models.CharField(max_length=64, db_index=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    context_id = models.BigIntegerField(null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["corp", "date"]),
            models.Index(fields=["corp", "ref_type"]),
        ]
        unique_together = (("corp", "division", "journal_id"),)
        default_permissions = ()

    def __str__(self):
        return f"{self.corp_id}/{self.division} #{self.journal_id} {self.ref_type} {self.amount}"


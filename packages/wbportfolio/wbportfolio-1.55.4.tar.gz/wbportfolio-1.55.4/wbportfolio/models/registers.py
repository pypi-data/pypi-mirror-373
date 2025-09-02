from django.db import models
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.models import WBModel

from wbportfolio.import_export.handlers.register import RegisterImportHandler


class Register(ImportMixin, WBModel):
    import_export_handler_class = RegisterImportHandler

    class RegisterStatus(models.TextChoices):
        ACTIVE = ("ACTIVE", "Active")
        INACTIVE = ("INACTIVE", "Inactive")
        WARNING = ("WARNING", "Warning")

    class RegisterInvestorType(models.TextChoices):
        BANK = ("BANK", "Bank and Financial Institution")
        NOMINEE = ("NOMINEE", "Nominee")
        GLOBAL = ("GLOBAL", "Global")
        NON_FINANCIAL_ENTITY = ("NON_FINANCIAL_ENTITY", "Non Financial Entities/Corporate")

    register_reference = models.CharField(max_length=255, unique=True)
    register_name_1 = models.CharField(max_length=255)
    register_name_2 = models.CharField(max_length=255, default="")
    global_register_reference = models.CharField(max_length=255, default="")
    external_register_reference = models.CharField(max_length=255, default="")

    custodian_reference = models.CharField(max_length=255)
    custodian_name_1 = models.CharField(max_length=255)
    custodian_name_2 = models.CharField(max_length=255, default="")
    custodian_address = models.TextField(default="", blank=True)
    custodian_postcode = models.CharField(max_length=255, default="")

    custodian_city = models.ForeignKey(
        "geography.Geography",
        related_name="register_custodian_city_registers",
        on_delete=models.PROTECT,
        limit_choices_to={"level": 3},
        null=True,
        blank=True,
    )
    custodian_country = models.ForeignKey(
        "geography.Geography",
        related_name="register_custodian_country_registers",
        on_delete=models.PROTECT,
        limit_choices_to={"level": 1},
        null=True,
        blank=True,
    )

    sales_reference = models.CharField(max_length=255, default="")
    dealer_reference = models.CharField(max_length=255, default="")

    outlet_reference = models.CharField(max_length=255)
    outlet_name = models.CharField(max_length=255)
    outlet_address = models.TextField(default="", blank=True)
    outlet_postcode = models.CharField(max_length=255, default="")

    outlet_city = models.ForeignKey(
        "geography.Geography",
        related_name="register_outlet_city_registers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"level": 3},
    )
    outlet_country = models.ForeignKey(
        "geography.Geography",
        related_name="register_outlet_country_registers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"level": 1},
    )

    citizenship = models.ForeignKey(
        "geography.Geography",
        related_name="register_citizenship_registers",
        on_delete=models.PROTECT,
        limit_choices_to={"level": 1},
        null=True,
        blank=True,
    )
    residence = models.ForeignKey(
        "geography.Geography",
        related_name="register_residence_registers",
        on_delete=models.PROTECT,
        limit_choices_to={"level": 1},
        null=True,
        blank=True,
    )

    investor_type = models.CharField(
        max_length=24, choices=RegisterInvestorType.choices, default=RegisterInvestorType.BANK
    )
    status = models.CharField(max_length=8, choices=RegisterStatus.choices, default=RegisterStatus.ACTIVE)
    status_message = models.TextField(default="", blank=True)

    opened = models.DateField()
    opened_reference_1 = models.CharField(max_length=255, default="")
    opened_reference_2 = models.CharField(max_length=255, default="")

    updated_reference_1 = models.CharField(max_length=255, default="")
    updated_reference_2 = models.CharField(max_length=255, default="")

    computed_str = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.register_reference}: {self.register_name_1} {self.register_name_2}"

    class Meta:
        verbose_name = "Register"
        verbose_name_plural = "Registers"

    def save(self, *args, **kwargs):
        self.computed_str = str(self)
        super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:register"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:registerrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{computed_str}}"

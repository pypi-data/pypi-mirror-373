from datetime import timedelta
from typing import Generator

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Entry
from wbcrm.models import Account
from wbfdm.models import Classification
from wbfdm.preferences import get_default_classification_group

from wbportfolio.analysis.claims import ConsolidatedTradeSummary
from wbportfolio.models import Product, ProductGroup
from wbportfolio.models.transactions.claim import Claim, ClaimGroupbyChoice
from wbportfolio.serializers import ProductRepresentationSerializer


@register("Account Shares Rule Backend", rule_group_key="sales")
class RuleBackend(backend.AbstractRuleBackend):
    OBJECT_FIELD_NAME: str = "customer"

    customer: Entry

    class FieldChoices(models.TextChoices):
        SHARES = "SHARES", "Shares"
        AUM = "AUM", "AUM"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.end_date = self.evaluation_date
        self.start_date = (self.evaluation_date - pd.tseries.offsets.BDay(self.business_days_interval)).date()

        self.group_by = ClaimGroupbyChoice[self.group_by]
        self.field = self.FieldChoices[self.field]

    def is_passive_evaluation_valid(self) -> bool:
        return Claim.objects.filter_for_customer(self.customer).filter(date__lte=self.evaluation_date).exists()

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Entry)

    def _build_dto_args(self):
        qs = Claim.objects.filter_for_customer(self.customer).filter(
            status=Claim.Status.APPROVED, date__lte=self.evaluation_date
        )
        if self.only_products:
            qs = qs.filter(product__in=self.only_products)
        groupby_map = ClaimGroupbyChoice.get_map(self.group_by.name)
        pivot = groupby_map["pk"]
        pivot_label = groupby_map["title_key"]
        cts_generator = ConsolidatedTradeSummary(
            qs,
            self.start_date,
            self.end_date + timedelta(days=1),  # we shift by one because end date is excluded
            pivot,
            pivot_label,
            classification_group=get_default_classification_group(),
        )
        return (cts_generator,)

    @classmethod
    def get_all_active_relationships(cls) -> models.QuerySet:
        return Entry.objects.annotate(
            has_open_account=models.Exists(Account.open_objects.filter(owner=models.OuterRef("pk")))
        ).filter(has_open_account=True)

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            business_days_interval = wb_serializers.IntegerField(default=7)
            moving_average_window = wb_serializers.IntegerField(default=1)  # 1 means the initial time series

            only_products = wb_serializers.PrimaryKeyRelatedField(
                queryset=Product.objects.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Only Products",
            )
            _only_products = ProductRepresentationSerializer(many=True, source="parameters__only_products")

            group_by = wb_serializers.ChoiceField(
                choices=ClaimGroupbyChoice.choices(),
                default=ClaimGroupbyChoice.ACCOUNT,
                allow_null=True,
                help_text="Choose how to group by shares",
                label="Group By",
            )
            field = wb_serializers.ChoiceField(
                choices=cls.FieldChoices.choices,
                default=cls.FieldChoices.SHARES,
                allow_null=True,
                help_text="Choose which metric to choose",
                label="Field",
            )

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "field",
                    "group_by",
                    "business_days_interval",
                    "moving_average_window",
                    "only_products",
                ]

        return RuleBackendSerializer

    def _process_dto(
        self, cts_generator: ConsolidatedTradeSummary, **kwargs
    ) -> Generator[backend.IncidentResult, None, None]:
        df = cts_generator.get_aum_df()
        if df.empty:
            return
        if self.field == self.FieldChoices.SHARES:
            perf = df["sum_shares_perf"]
            start_df = df["sum_shares_start"]
            end_df = df["sum_shares_end"]
        else:
            perf = df["sum_aum_perf"]
            start_df = df["sum_aum_start"]
            end_df = df["sum_aum_end"]
        perf = perf.dropna()
        if not perf.empty:
            for threshold in self.thresholds:
                numerical_range = threshold.numerical_range
                breached_perf = perf[(perf > numerical_range[0]) & (perf < numerical_range[1])].dropna()
                if not breached_perf.empty:
                    for breached_obj_id, percentage in breached_perf.to_dict().items():
                        breached_obj = None
                        if self.group_by == ClaimGroupbyChoice.PRODUCT:
                            breached_obj = Product.objects.get(id=breached_obj_id)
                        elif self.group_by == ClaimGroupbyChoice.PRODUCT_GROUP:
                            breached_obj = ProductGroup.objects.get(id=breached_obj_id)
                        elif self.group_by == ClaimGroupbyChoice.CLASSIFICATION:
                            breached_obj = Classification.objects.get(id=breached_obj_id)
                        elif self.group_by in [ClaimGroupbyChoice.ACCOUNT, ClaimGroupbyChoice.ROOT_ACCOUNT]:
                            breached_obj = Account.objects.get(id=breached_obj_id)
                        elif self.group_by in [
                            ClaimGroupbyChoice.ACCOUNT_OWNER,
                            ClaimGroupbyChoice.ROOT_ACCOUNT_OWNER,
                        ]:
                            breached_obj = Entry.objects.get(id=breached_obj_id)
                        report_details = {
                            "Period": f"{cts_generator.start_date:%d.%m.%Y} - {cts_generator.end_date:%d.%m.%Y}",
                        }

                        # create report detail template
                        color = "red" if percentage < 0 else "green"
                        number_prefix = ""

                        if self.field == "AUM":
                            key = "AUM Change"
                            number_prefix = "$"
                        else:
                            key = "Shares Change"

                        template = f'{number_prefix}{{}} → {number_prefix}{{}} <span style="color:{color}"><strong>Δ {number_prefix}{{}}</strong></span>'
                        start = intcomma(int(start_df.loc[breached_obj_id].round(0)))
                        end = intcomma(int(end_df.loc[breached_obj_id].round(0)))
                        diff = intcomma(int((end_df.loc[breached_obj_id] - start_df.loc[breached_obj_id]).round(0)))
                        report_details[key] = template.format(start, end, diff)
                        report_details["Group By"] = self.group_by.value
                        yield backend.IncidentResult(
                            breached_object=breached_obj,
                            breached_object_repr=str(breached_obj),
                            breached_value=f'<span style="color:{color}">{percentage:+,.2%}</span>',
                            report_details=report_details,
                            severity=threshold.severity,
                        )

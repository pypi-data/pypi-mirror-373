from datetime import date
from decimal import Decimal

import numpy as np
import pandas as pd
from django.db.models import (
    DecimalField,
    Expression,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.strings import format_number
from wbfdm.models import Instrument, InstrumentPrice, RelatedInstrumentThroughModel

from wbportfolio.filters import (
    PerformanceComparisonFilter,
    PerformancePandasFilter,
    ProductPerformanceNetNewMoneyFilter,
)
from wbportfolio.models import Product, Trade

from .configs import (
    PerformanceComparisonDisplayConfig,
    PerformanceComparisonEndpointConfig,
    PerformanceComparisonTitleConfig,
    PerformancePandasDisplayConfig,
    PerformancePandasEndpointConfig,
    PerformancePandasTitleConfig,
    ProductPerformanceNetNewMoneyDisplayConfig,
    ProductPerformanceNetNewMoneyEndpointConfig,
    ProductPerformanceNetNewMoneyTitleConfig,
)


class PerformancePandasView(InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:performances"

    queryset = Product.objects.all()

    filterset_class = PerformancePandasFilter

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="computed_str", label="Title"),
            pf.CharField(key="currency_symbol", label="Currency Key"),
            pf.BooleanField(key="is_invested", label="Invested"),
            pf.FloatField(key="sum_shares2", label="Shares"),
            pf.FloatField(
                key="n1",
                label="N1",
                precision=2,
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="n2",
                label="N2",
                precision=2,
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="diff",
                label="Difference",
                precision=2,
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(key="perf", label="Performance", precision=2, percent=True),
            pf.FloatField(
                key="n1_usd",
                label="N1 (usd)",
                precision=2,
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="n2_usd",
                label="N2 (usd)",
                precision=2,
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="diff_usd",
                label="Difference (usd)",
                precision=2,
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(key="perf_usd", label="Performance (usd)", precision=2, percent=True),
        )
    )
    display_config_class = PerformancePandasDisplayConfig
    title_config_class = PerformancePandasTitleConfig
    endpoint_config_class = PerformancePandasEndpointConfig

    search_fields = ["computed_str"]
    ordering_fields = ["computed_str", "n1", "n2", "diff", "perf", "n1_usd", "n2_usd", "diff_usd", "perf_usd"]

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            "n1_usd": {"Σ": format_number(df["n1_usd"].sum())},
            "n2_usd": {"Σ": format_number(df["n2_usd"].sum())},
            "diff_usd": {"Σ": format_number(df["diff_usd"].sum())},
        }

    def get_queryset(self):
        d1, d2 = get_date_interval_from_request(self.request, exclude_weekend=True)
        if d1 and d2:
            return (
                super()
                .get_queryset()
                .annotate(
                    d1=Subquery(
                        InstrumentPrice.objects.filter(
                            calculated=False, instrument=OuterRef("pk"), date__gte=d1, date__lte=d2
                        )
                        .order_by("date")
                        .values("date")[:1]
                    ),
                    d2=Subquery(
                        InstrumentPrice.objects.filter(
                            calculated=False, instrument=OuterRef("pk"), date__gte=d1, date__lte=d2
                        )
                        .order_by("-date")
                        .values("date")[:1]
                    ),
                    fx_rate_n1=Coalesce(
                        Subquery(
                            CurrencyFXRates.objects.filter(currency=OuterRef("currency"), date=OuterRef("d1")).values(
                                "value"
                            )[:1]
                        ),
                        Decimal(1),
                    ),
                    fx_rate_n2=Coalesce(
                        Subquery(
                            CurrencyFXRates.objects.filter(currency=OuterRef("currency"), date=OuterRef("d2")).values(
                                "value"
                            )[:1]
                        ),
                        Decimal(1),
                    ),
                    outstanding_shares_n1=Coalesce(
                        InstrumentPrice.subquery_closest_value(
                            "outstanding_shares",
                            instrument_pk_name="pk",
                            date_name="d1",
                            order_by="calculated",
                            calculated_filter_value=None,
                            date_lookup="exact",
                        ),
                        Decimal(0),
                    ),
                    outstanding_shares_n2=Coalesce(
                        InstrumentPrice.subquery_closest_value(
                            "outstanding_shares",
                            instrument_pk_name="pk",
                            date_name="d2",
                            order_by="calculated",
                            calculated_filter_value=None,
                            date_lookup="exact",
                        ),
                        Decimal(0),
                    ),
                    net_value_n1=InstrumentPrice.subquery_closest_value(
                        "net_value", instrument_pk_name="pk", date_name="d1", date_lookup="exact"
                    ),
                    net_value_n2=InstrumentPrice.subquery_closest_value(
                        "net_value", instrument_pk_name="pk", date_name="d2", date_lookup="exact"
                    ),
                )
                .filter(d1__isnull=False, d2__isnull=False)
            )
        return Product.objects.none()

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame(
            queryset.values(
                "id",
                "computed_str",
                "currency__symbol",
                "d1",
                "d2",
                "fx_rate_n1",
                "fx_rate_n2",
                "outstanding_shares_n1",
                "outstanding_shares_n2",
                "net_value_n1",
                "net_value_n2",
            )
        ).rename(columns={"currency__symbol": "currency_symbol"})
        performance_by = self.request.GET.get("performance_by", PerformancePandasFilter.PerformanceBy.PRICE.name)
        if not df.empty:
            if performance_by == PerformancePandasFilter.PerformanceBy.NNM.name:
                df["n1"] = df["outstanding_shares_n1"] * df["net_value_n1"]
                df["n2"] = df["outstanding_shares_n2"] * df["net_value_n1"]
                df["n1_usd"] = df["n1"] / df["fx_rate_n1"]
                df["n2_usd"] = df["n2"] / df["fx_rate_n2"]
            elif performance_by == PerformancePandasFilter.PerformanceBy.AUM.name:
                df["n1"] = df["outstanding_shares_n1"] * df["net_value_n1"]
                df["n2"] = df["outstanding_shares_n2"] * df["net_value_n2"]
                df["n1_usd"] = df["n1"] / df["fx_rate_n1"]
                df["n2_usd"] = df["n2"] / df["fx_rate_n2"]

            elif performance_by == PerformancePandasFilter.PerformanceBy.PRICE.name:
                df["n1"] = df["net_value_n1"]
                df["n2"] = df["net_value_n2"]
                df["n1_usd"] = df["n1"] / df["fx_rate_n1"]
                df["n2_usd"] = df["n2"] / df["fx_rate_n2"]
            else:
                raise ValueError("You need to specify a performance by filter")

            df = df.ffill()
            number_columns = df.columns.difference(["id", "computed_str", "currency_symbol", "d1", "d2"])
            df[number_columns] = df[number_columns].astype(float)
            df["diff"] = df["n2"] - df["n1"]
            df["diff_usd"] = df["n2_usd"] - df["n1_usd"]
            df["perf"] = df["diff"].div(df["n1"])
            df["perf_usd"] = df["diff_usd"].div(df["n1_usd"])
        return df.replace(np.inf, 0)


class ProductPerformanceNetNewMoneyListViewSet(InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:product-performance-net-new-money"

    filterset_class = ProductPerformanceNetNewMoneyFilter
    queryset = Product.objects.all()

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="computed_str", label="Title"),
            pf.CharField(key="currency_symbol", label="Currency Key"),
            pf.BooleanField(key="is_invested", label="Invested"),
            pf.FloatField(
                key="net_money",
                label="Net New Money",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="net_negative_money",
                label="Net Negative Money",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="net_positive_money",
                label="Net Positive Money",
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.FloatField(
                key="net_money_usd",
                label="Net Money ($)",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="net_negative_money_usd",
                label="Net Negative Money ($)",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
            pf.FloatField(
                key="net_positive_money_usd",
                label="Net Positive Money ($)",
                decorators=[wb_serializers.decorator(decorator_type="text", position="left", value="$")],
            ),
        )
    )

    search_fields = ("computed_str", "isin", "ticker")
    ordering_fields = (
        "computed_str",
        "net_negative_money",
        "net_negative_money_usd",
        "net_positive_money",
        "net_positive_money_usd",
        "net_money",
        "net_money_usd",
    )
    ordering = ["computed_str"]

    display_config_class = ProductPerformanceNetNewMoneyDisplayConfig
    title_config_class = ProductPerformanceNetNewMoneyTitleConfig
    endpoint_config_class = ProductPerformanceNetNewMoneyEndpointConfig

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            "net_money_usd": {"Σ": format_number(df.net_money_usd.sum())},
            "net_negative_money_usd": {"Σ": format_number(df.net_negative_money_usd.sum())},
            "net_positive_money_usd": {"Σ": format_number(df.net_positive_money_usd.sum())},
        }

    @cached_property
    def latest_rate_date(self) -> date:
        try:
            return CurrencyFXRates.objects.latest("date").date
        except CurrencyFXRates.DoesNotExist:
            return date.today()

    def get_queryset(self):
        d1, d2 = get_date_interval_from_request(self.request, exclude_weekend=True)
        d1 = (
            Trade.objects.earliest("transaction_date").transaction_date
            if not d1 and Trade.objects.all().exists()
            else d1
        )
        d2 = (
            Trade.objects.latest("transaction_date").transaction_date
            if not d2 and Trade.objects.all().exists()
            else d2
        )
        products = Product.objects.all().annotate(currency_symbol=F("currency__symbol"))
        if d1 and d2:
            products = products.annotate(
                sum_shares=Trade.subquery_shares_per_underlying_instrument(d1),
                net_money=Trade.subquery_net_money(d1, d2),
                net_negative_money=Trade.subquery_net_money(d1, d2, only_negative=True),
                net_positive_money=Trade.subquery_net_money(d1, d2, only_positive=True),
                fx2=CurrencyFXRates.get_fx_rates_subquery(
                    self.latest_rate_date, currency="currency", lookup_expr="exact"
                ),
                net_money_usd=ExpressionWrapper(F("fx2") * F("net_money"), output_field=FloatField()),
                net_negative_money_usd=ExpressionWrapper(
                    F("fx2") * F("net_negative_money"), output_field=FloatField()
                ),
                net_positive_money_usd=ExpressionWrapper(
                    F("fx2") * F("net_positive_money"), output_field=FloatField()
                ),
            )
        else:
            products = products.annotate(
                sum_shares=Value(0.0),
                net_money=Value(0.0),
                net_negative_money=Value(0.0),
                net_positive_money=Value(0.0),
                fx2=Value(0.0),
                net_money_usd=Value(0.0),
                net_negative_money_usd=Value(0.0),
                net_positive_money_usd=Value(0.0),
            )
        return products.select_related("currency")


class PerformanceComparisonPandasView(InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:performancescomparison"

    queryset = Product.objects.all()
    filterset_class = PerformanceComparisonFilter

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="computed_str", label="Title"),
            pf.CharField(key="benchmark_computed_str", label="Compared benchmark"),
            pf.CharField(key="currency_symbol", label="Currency Key"),
            pf.FloatField(
                key="instrument_last_valuation_price",
                label="N1",
                precision=2,
                decorators=[
                    wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")
                ],
            ),
            pf.DateField(key="inception_date", label="Inception Date"),
            pf.DateField(key="last_valuation_date", label="Last Date Date"),
            pf.FloatField(key="perf_last_day", label="daily", precision=2, percent=True),
            pf.FloatField(key="perf_month_to_date", label="monthly", precision=2, percent=True),
            pf.FloatField(key="perf_year_to_date", label="yearly", precision=2, percent=True),
            pf.FloatField(key="perf_inception", label="inception", precision=2, percent=True),
            pf.FloatField(key="perf_between_dates", label="Perf", precision=2, percent=True),
        )
    )
    display_config_class = PerformanceComparisonDisplayConfig
    title_config_class = PerformanceComparisonTitleConfig
    endpoint_config_class = PerformanceComparisonEndpointConfig

    search_fields = ["computed_str"]
    ordering = ["computed_str"]
    ordering_fields = [
        "computed_str",
        "instrument_last_valuation_price",
        "last_valuation_date",
        "perf_last_day",
        "perf_month_to_date",
        "perf_year_to_date",
        "perf_inception",
        "last_valuation_date",
        "perf_between_dates",
    ]

    @property
    def dates(self):
        if (
            (dates := get_date_interval_from_request(self.request, exclude_weekend=True, date_range_fieldname="dates"))
            and (d1 := dates[0])
            and (d2 := dates[1])
        ):
            return d1, d2

    @property
    def benchmark_label(self) -> ExpressionWrapper:
        comparison_instrument_id = self.request.GET.get("comparison_instrument", None)
        compare_primary_benchmark = self.request.GET.get("compare_primary_benchmark", "false") == "true"
        if comparison_instrument_id or compare_primary_benchmark:
            return (
                Value(comparison_instrument_id)
                if comparison_instrument_id
                else Subquery(
                    RelatedInstrumentThroughModel.objects.filter(
                        instrument=OuterRef("pk"),
                        is_primary=True,
                        related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.BENCHMARK,
                    ).values("related_instrument")[:1]
                )
            )

    def get_queryset(self):
        def _prices_annotation_expressions(
            prefix: str = "instrument", instrument_label: str = "pk", initial_price_label: str = "share_price"
        ) -> dict[str, Expression]:
            """
            Utility function to prepare annotatione expression for the instrument or benchmark
            Args:
                prefix: prefix to use for the annotated field names
                instrument_label: OuterRef instrument label
                initial_price_label: OuterRef initial instrument price
            Returns:
                A dictionary of annotable expressions
            """
            res = {
                f"{prefix}_last_valuation_price": Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef(instrument_label),
                            calculated=False,
                            date=OuterRef("last_valuation_date"),
                        )
                        .exclude(net_value=0)
                        .values("net_value")[:1]
                    ),
                    ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                ),
                f"_{prefix}_initial_price": Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef(instrument_label), calculated=False, date=OuterRef("inception_date")
                        )
                        .exclude(net_value=0)
                        .values("net_value")[:1]
                    ),
                    ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                ),
                f"_{prefix}_valuation_price_t1": Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef(instrument_label), calculated=False, date=OuterRef("_t1")
                        )
                        .exclude(net_value=0)
                        .values("net_value")[:1]
                    ),
                    ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                ),
                f"_{prefix}_valuation_price_m1": Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef(instrument_label), calculated=False, date=OuterRef("_m1")
                        )
                        .exclude(net_value=0)
                        .values("net_value")[:1]
                    ),
                    ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                ),
                f"_{prefix}_valuation_price_y1": Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef(instrument_label),
                            calculated=False,
                            date=OuterRef("_y1"),
                        )
                        .exclude(net_value=0)
                        .values("net_value")[:1]
                    ),
                    ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                ),
                f"_{prefix}_perf_last_day": F(f"{prefix}_last_valuation_price") / F(f"_{prefix}_valuation_price_t1")
                - 1,
                f"_{prefix}_perf_month_to_date": F(f"{prefix}_last_valuation_price")
                / F(f"_{prefix}_valuation_price_m1")
                - 1,
                f"_{prefix}_perf_year_to_date": F(f"{prefix}_last_valuation_price")
                / F(f"_{prefix}_valuation_price_y1")
                - 1,
                f"_{prefix}_perf_inception": F(f"{prefix}_last_valuation_price") / F(f"_{prefix}_initial_price") - 1,
            }
            if self.dates:
                # If dates is available, we also annotate the performance between the specified dates range
                res.update(
                    {
                        f"_{prefix}_last_valuation_price_d1": Coalesce(
                            Subquery(
                                InstrumentPrice.objects.filter(
                                    instrument=OuterRef(instrument_label), calculated=False, date__lte=self.dates[0]
                                )
                                .order_by("-date")
                                .values("net_value")[:1]
                            ),
                            ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                        ),
                        f"_{prefix}_last_valuation_price_d2": Coalesce(
                            Subquery(
                                InstrumentPrice.objects.filter(
                                    instrument=OuterRef(instrument_label),
                                    calculated=False,
                                    date__lte=self.dates[1],
                                )
                                .order_by("-date")
                                .values("net_value")[:1]
                            ),
                            ExpressionWrapper(F(initial_price_label), output_field=DecimalField()),
                        ),
                        f"_{prefix}_perf_between_dates": F(f"_{prefix}_last_valuation_price_d2")
                        / F(f"_{prefix}_last_valuation_price_d1")
                        - 1,
                    }
                )
            else:
                res[f"_{prefix}_perf_between_dates"] = Value(
                    Decimal(0)
                )  # Ensure the key is available to avoid keyerror during evaluation
            return res

        qs = (
            super()
            .get_queryset()
            .annotate(
                currency_symbol=F("currency__symbol"),
                _t1=Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef("pk"), calculated=False, date__lt=OuterRef("last_valuation_date")
                        )
                        .order_by("-date")
                        .values("date")[:1]
                    ),
                    F("inception_date"),
                ),  # t-1 date
                _m1=Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            Q(instrument=OuterRef("pk"))
                            & Q(calculated=False)
                            & ~(
                                Q(date__gte=OuterRef("last_valuation_date"))
                                | (
                                    Q(date__month=OuterRef("last_valuation_date__month"))
                                    & Q(date__year=OuterRef("last_valuation_date__year"))
                                )
                            )
                        )
                        .order_by("-date")
                        .values("date")[:1]
                    ),
                    F("inception_date"),
                ),  # latest previous month date
                _y1=Coalesce(
                    Subquery(
                        InstrumentPrice.objects.filter(
                            instrument=OuterRef("pk"),
                            calculated=False,
                            date__year=OuterRef("last_valuation_date__year") - 1,
                        )
                        .order_by("-date")
                        .values("date")[:1]
                    ),
                    F("inception_date"),
                ),  # latest previous year date
                **_prices_annotation_expressions(),
            )
        )
        if benchmark_label := self.benchmark_label:
            # If benchmark is provided, we annotate their respective price depending on the outer reference POI
            qs = qs.annotate(
                _benchmark_id=benchmark_label,
                benchmark_computed_str=Subquery(
                    Instrument.objects.filter(id=OuterRef("_benchmark_id")).values("computed_str")[:1]
                ),
                benchmark_issue_price=Subquery(
                    Instrument.objects.filter(id=OuterRef("_benchmark_id")).values("issue_price")[:1]
                ),
                _benchmark_last_valuation_price=Subquery(
                    InstrumentPrice.objects.filter(
                        instrument=OuterRef("_benchmark_id"), calculated=False, date=OuterRef("last_valuation_date")
                    ).values("net_value")[:1]
                ),
                **_prices_annotation_expressions(
                    prefix="benchmark", instrument_label="_benchmark_id", initial_price_label="benchmark_issue_price"
                ),
            )
        else:
            qs = qs.annotate(
                benchmark_computed_str=Value(""),
                **{
                    k: Value(Decimal(0.0))
                    for k in [
                        "_benchmark_perf_between_dates",
                        "_benchmark_perf_last_day",
                        "_benchmark_perf_month_to_date",
                        "_benchmark_perf_year_to_date",
                        "_benchmark_perf_inception",
                    ]
                },
            )  # Ensure the key is available to avoid keyerror during evaluation
        return qs.annotate(
            perf_last_day=F("_instrument_perf_last_day") - Coalesce(F("_benchmark_perf_last_day"), Value(Decimal(0))),
            perf_month_to_date=F("_instrument_perf_month_to_date")
            - Coalesce(F("_benchmark_perf_month_to_date"), Value(Decimal(0))),
            perf_year_to_date=F("_instrument_perf_year_to_date")
            - Coalesce(F("_benchmark_perf_year_to_date"), Value(Decimal(0))),
            perf_inception=F("_instrument_perf_inception")
            - Coalesce(F("_benchmark_perf_inception"), Value(Decimal(0))),
            perf_between_dates=F("_instrument_perf_between_dates")
            - Coalesce(F("_benchmark_perf_between_dates"), Value(Decimal(0))),
        )

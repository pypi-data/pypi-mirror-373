from wbcore import filters as wb_filters
from wbfdm.analysis.esg.enums import ESGAggregation

from wbportfolio.models import AssetPosition

from .assets import get_latest_asset_position


class ESGMetricAggregationPortfolioPandasFilterSet(wb_filters.FilterSet):
    date = wb_filters.DateFilter(
        label="Date", lookup_expr="exact", field_name="date", initial=get_latest_asset_position, required=True
    )

    esg_aggregation = wb_filters.ChoiceFilter(
        choices=ESGAggregation.choices(),
        initial=ESGAggregation.GHG_EMISSIONS_SCOPE_1.name,
        required=True,
        method="fake_filter",
    )

    class Meta:
        model = AssetPosition
        fields = {}

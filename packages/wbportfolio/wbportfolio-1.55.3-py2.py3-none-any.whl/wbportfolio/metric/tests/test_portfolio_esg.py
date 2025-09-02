from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from django.contrib.contenttypes.models import ContentType
from faker import Faker
from wbfdm.analysis.esg.enums import ESGAggregation
from wbfdm.contrib.metric.models import InstrumentMetric

from ..backends.portfolio_esg import PortfolioESGMetricBackend

fake = Faker()


@pytest.mark.django_db
class TestPortfolioESGDataloader:
    @pytest.fixture
    def backend(self, weekday):
        return PortfolioESGMetricBackend(weekday)

    @patch.object(PortfolioESGMetricBackend, "_get_metrics_for_esg_aggregation")
    def test_compute_metrics(self, mock_fct, backend, portfolio, instrument_factory, asset_position_factory):
        instruments = instrument_factory.create_batch(2)
        asset_position_factory.create(portfolio=portfolio, is_estimated=False, date=backend.val_date)
        esg_aggregation = pd.DataFrame(
            np.random.randint(1, 100, size=[2, 1]), index=[i.id for i in instruments], columns=["score"]
        )
        mock_fct.return_value = esg_aggregation
        for metric in backend.compute_metrics(portfolio):
            InstrumentMetric.update_or_create_from_metric(metric)

        p_ct = ContentType.objects.get_for_model(portfolio)

        # check that we indeed created and stored a metrics for each esg aggregation and for each instrument
        for esg in ESGAggregation:
            for instrument in instruments:
                assert (
                    InstrumentMetric.objects.get(
                        basket_content_type=p_ct.pk,
                        basket_id=portfolio.id,
                        instrument=instrument,
                        date=backend.val_date,
                        key=f"portfolio_esg_{esg.name.lower()}",
                    ).metrics["score"]
                    == esg_aggregation.loc[instrument.id, "score"]
                )

            # check if the egg aggregated accross the whole portfolio is properly stored
            assert (
                InstrumentMetric.objects.get(
                    basket_content_type=p_ct.pk,
                    basket_id=portfolio.id,
                    instrument__isnull=True,
                    date=backend.val_date,
                    key=f"portfolio_esg_{esg.name.lower()}",
                ).metrics["score"]
                == esg_aggregation.sum(axis=0)["score"]
            )

        #
        # # basic checks
        # assert res[0].basket_id == portfolio.id
        # assert res[0].basket_content_type_id ==
        # assert res[0].key ==
        # assert res[0].metrics ==
        # assert res[0].date ==
        # assert res[0].instrument_id ==
        # assert res[0].dependency_metrics ==

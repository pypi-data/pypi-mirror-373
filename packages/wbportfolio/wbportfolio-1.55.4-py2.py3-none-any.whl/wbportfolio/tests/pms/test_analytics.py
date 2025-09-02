import pandas as pd
import pytest

from wbportfolio.pms.analytics.portfolio import Portfolio


def test_get_next_weights():
    w0 = 0.3
    w1 = 0.5
    w2 = 0.2
    r0 = 0.1
    r1 = 0.05
    r2 = -0.23
    weights = [w0, w1, w2]
    returns = [r0, r1, r2]
    portfolio = Portfolio(X=pd.DataFrame([returns]), weights=pd.Series(weights))
    next_weights = portfolio.get_next_weights()

    assert next_weights[0] == pytest.approx(w0 * (r0 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1)), abs=10e-8)
    assert next_weights[1] == pytest.approx(w1 * (r1 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1)), abs=10e-8)
    assert next_weights[2] == pytest.approx(w2 * (r2 + 1) / (w0 * (r0 + 1) + w1 * (r1 + 1) + w2 * (r2 + 1)), abs=10e-8)


def test_get_next_weights_solve_quantization_error():
    w0 = 0.33333334
    w1 = 0.33333333
    w2 = 0.33333333
    weights = [w0, w1, w2]
    returns = [1.0, 1.0, 1.0]  # no returns
    portfolio = Portfolio(X=pd.DataFrame([returns]), weights=pd.Series(weights))
    next_weights = portfolio.get_next_weights(round_precision=8)  # no rounding as number are all 8 decimals
    assert sum(next_weights.values()) == 1.0
    next_weights = portfolio.get_next_weights(
        round_precision=7
    )  # we expect the weight to be rounded to 6 decimals, which would lead to a total sum of 0.999999

    assert next_weights[0] == 0.3333334
    assert next_weights[1] == 0.3333333
    assert next_weights[2] == 0.3333333


def test_get_estimate_net_value():
    w0 = 0.3
    w1 = 0.5
    w2 = 0.2
    r0 = 0.1
    r1 = 0.05
    r2 = -0.23
    weights = [w0, w1, w2]
    returns = [r0, r1, r2]
    portfolio = Portfolio(X=pd.DataFrame([returns]), weights=pd.Series(weights))
    current_price = 100
    net_asset_value = portfolio.get_estimate_net_value(current_price)
    return net_asset_value == current_price * (1.0 + w0 * r0 + w1 * r1 + w2 * r2)

from pytest_factoryboy import register
from wbcompliance.factories.risk_management import (
    RiskIncidentTypeFactory,
    RiskRuleFactory,
    RuleBackendFactory,
    RuleThresholdFactory,
)
from wbfdm.factories import ControversyFactory
from wbportfolio.tests.conftest import *  # noqa

register(RiskIncidentTypeFactory)
register(RiskRuleFactory)
register(RuleBackendFactory)
register(RuleThresholdFactory)
register(ControversyFactory)

import pytest

from wbportfolio.factories import (
    ManagerPortfolioRoleFactory,
    ProductPortfolioRoleFactory,
)
from wbportfolio.models import PortfolioRole
from wbportfolio.permissions import is_analyst, is_manager, is_portfolio_manager


@pytest.mark.django_db
class TestPortfolioRoleModel:
    def test_init_product_portfolio_role(self, product_portfolio_role):
        assert product_portfolio_role.id is not None

    def test_init_manager_portfolio_role(self, manager_portfolio_role):
        assert manager_portfolio_role.id is not None

    def test_str(self, product_portfolio_role):
        assert (
            str(product_portfolio_role)
            == f"{product_portfolio_role.role_type} {product_portfolio_role.person.computed_str}"
        )

    # test is_manager

    def test_is_manager_portfolio_role(self, user):
        ManagerPortfolioRoleFactory.create(person=user.profile)
        assert PortfolioRole.is_manager(user.profile)

    def test_is_not_manager_portfolio_role(self, user):
        assert not PortfolioRole.is_manager(user.profile)

    def test_is_manager_portfolio_role_superuser(self, superuser):
        superuser.is_superuser = True
        superuser.save()
        assert PortfolioRole.is_manager(superuser.profile)

    # test is_portfolio_manager

    def test_is_portfolio_manager_portfolio_role(self, user, product):
        ProductPortfolioRoleFactory.create(
            person=user.profile, instrument=product, role_type=PortfolioRole.RoleType.PORTFOLIO_MANAGER
        )
        assert PortfolioRole.is_portfolio_manager(user.profile, product)

    def test_is_portfolio_manager_portfolio_role_manager(self, user, product):
        ManagerPortfolioRoleFactory.create(person=user.profile)
        assert PortfolioRole.is_portfolio_manager(user.profile, product)

    def test_is_not_portfolio_manager_portfolio_role(self, user, product):
        assert not PortfolioRole.is_portfolio_manager(user.profile, product)

    def test_is_portfolio_manager_portfolio_role_superuser(self, superuser, product):
        assert PortfolioRole.is_portfolio_manager(superuser.profile, product)

    # test is_analyst

    def test_is_analyst_portfolio_role(self, user, product):
        ProductPortfolioRoleFactory.create(
            person=user.profile, instrument=product, role_type=PortfolioRole.RoleType.ANALYST
        )
        assert PortfolioRole.is_analyst(user.profile, product)

    def test_is_analyst_portfolio_role_manager(self, user, product):
        ManagerPortfolioRoleFactory.create(person=user.profile)
        assert PortfolioRole.is_analyst(user.profile, product)

    def test_is_not_analyst_portfolio_role(self, user, product):
        assert not PortfolioRole.is_analyst(user.profile, product)

    def test_is_analyst_portfolio_role_superuser(self, superuser, product):
        assert PortfolioRole.is_analyst(superuser.profile, product)

    def test_permissions(self, user):
        class Request:
            def __init__(self, user):
                self.user = user

        request = Request(user)
        assert is_manager(request) == PortfolioRole.is_manager(user.profile)
        assert is_analyst(request) == PortfolioRole.is_analyst(user.profile)
        assert is_portfolio_manager(request) == PortfolioRole.is_portfolio_manager(user.profile)

from wbportfolio.models import PortfolioRole


def is_manager(request):
    return PortfolioRole.is_manager(request.user.profile)


def is_portfolio_manager(request):
    return PortfolioRole.is_portfolio_manager(request.user.profile)


def is_analyst(request):
    return PortfolioRole.is_analyst(request.user.profile)

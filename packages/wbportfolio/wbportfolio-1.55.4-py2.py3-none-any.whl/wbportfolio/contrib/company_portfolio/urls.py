from django.urls import include, path
from wbcore.routers import WBCoreRouter

from .viewsets import (
    AssetAllocationModelViewSet,
    AssetAllocationTypeModelViewSet,
    AssetAllocationTypeRepresentationViewSet,
    GeographicFocusModelViewSet,
)

router = WBCoreRouter()

router.register(
    r"assetallocationtyperepresentation",
    AssetAllocationTypeRepresentationViewSet,
    basename="assetallocationtyperepresentation",
)
router.register(r"assetallocationtype", AssetAllocationTypeModelViewSet, basename="assetallocationtype")
router.register(r"assetallocation", AssetAllocationModelViewSet, basename="assetallocation")
router.register(r"geographicfocus", GeographicFocusModelViewSet, basename="geographicfocus")

company_router = WBCoreRouter()
company_router.register(r"companyassetallocation", AssetAllocationModelViewSet, basename="companyassetallocation")
company_router.register(r"companygeographicfocus", GeographicFocusModelViewSet, basename="companygeographicfocus")

urlpatterns = [
    path("", include(router.urls)),
    path("crmcompany/<int:company_id>/", include(company_router.urls)),
]

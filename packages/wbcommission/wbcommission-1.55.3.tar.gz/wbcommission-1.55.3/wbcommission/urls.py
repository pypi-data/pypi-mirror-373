from django.apps import apps
from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbcommission import viewsets

router = WBCoreRouter()

router.register(
    r"rebatemarginalitytable",
    viewsets.RebateProductMarginalityViewSet,
    basename="rebatemarginalitytable",
)
router.register(
    r"rebatetable",
    viewsets.RebatePandasView,
    basename="rebatetable",
)
router.register(
    r"rebate",
    viewsets.RebateModelViewSet,
    basename="rebate",
)
router.register(
    r"commissiontype",
    viewsets.CommissionTypeModelViewSet,
    basename="commissiontype",
)
router.register(
    r"commissiontyperepresentation",
    viewsets.CommissionTypeRepresentationModelViewSet,
    basename="commissiontyperepresentation",
)

if apps.is_installed("wbportfolio"):
    from wbportfolio.viewsets.transactions.claim import ClaimAPIModelViewSet

    router.register(r"claim-api", ClaimAPIModelViewSet, basename="claim-api")

account_router = WBCoreRouter()


urlpatterns = [path("", include(router.urls)), path("account/<int:account_id>/", include(account_router.urls))]

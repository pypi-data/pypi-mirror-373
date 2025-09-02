from django.urls import include, path
from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

# Representations
router.register(r"activityrepresentation", viewsets.ActivityRepresentationViewSet, basename="activityrepresentation")
router.register(r"grouprepresentation", viewsets.GroupRepresentationViewSet, basename="grouprepresentation")
router.register(r"group", viewsets.GroupModelViewSet, basename="group")
router.register(r"activitytype", viewsets.ActivityTypeModelViewSet, basename="activitytype")
router.register(
    r"activitytyperepresentation", viewsets.ActivityTypeRepresentationViewSet, basename="activitytyperepresentation"
)

router.register(r"product", viewsets.ProductModelViewSet, basename="product")
router.register(
    r"productrepresentation",
    viewsets.ProductRepresentationViewSet,
    basename="productrepresentation",
)


# Activity
router.register(r"activity", viewsets.ActivityViewSet, basename="activity")
# used to create new activity instances

router.register(r"activitychart", viewsets.ActivityChartModelViewSet, basename="activitychart")


activity_router = WBCoreRouter()
activity_router.register(
    r"activity-participant",
    viewsets.ActivityParticipantModelViewSet,
    basename="activity-participant",
)

company_router = WBCoreRouter()
company_router.register(
    r"company-interestedproduct",
    viewsets.ProductCompanyRelationshipCompanyModelViewSet,
    basename="company-interestedproduct",
)

router.register(r"account", viewsets.AccountModelViewSet, basename="account")
router.register(r"accountrepresentation", viewsets.AccountRepresentationViewSet, basename="accountrepresentation")
router.register(
    r"accountroletyperepresentation",
    viewsets.AccountRoleTypeRepresentationViewSet,
    basename="accountroletyperepresentation",
)

account_router = WBCoreRouter()
account_router.register(r"childaccount", viewsets.ChildAccountAccountModelViewSet, basename="account-childaccount")
account_router.register(r"accountrole", viewsets.AccountRoleAccountModelViewSet, basename="account-accountrole")
account_router.register(
    r"inheritedrole", viewsets.InheritedAccountRoleAccountModelViewSet, basename="account-inheritedrole"
)

urlpatterns = [
    path("", include(router.urls)),
    path("activity/<int:activity_id>/", include(activity_router.urls)),
    path("company/<int:company_id>/", include(company_router.urls)),
    path("sync/", include(("wbcrm.synchronization.urls", "sync"), namespace="sync")),
    path("account/<int:account_id>/", include(account_router.urls)),
]

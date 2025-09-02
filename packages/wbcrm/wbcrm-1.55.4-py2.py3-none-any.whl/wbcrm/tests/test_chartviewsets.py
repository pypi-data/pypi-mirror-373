import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.test.utils import get_kwargs

from wbcrm.factories import ActivityFactory
from wbcrm.viewsets import ActivityChartModelViewSet, ActivityViewSet


@pytest.mark.django_db
class TestSpecificsChartViewsets:
    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (ActivityChartModelViewSet, ActivityFactory),
        ],
    )
    def test_option_request(self, mvs, factory, superuser):
        request = APIRequestFactory().options("")
        request.user = superuser
        factory()
        kwargs = {"user_id": request.user.id}
        vs = mvs.as_view({"options": "options"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (ActivityChartModelViewSet, ActivityFactory),
        ],
    )
    def test_viewsets(self, mvs, factory, superuser):
        request = APIRequestFactory().get("")
        request.user = superuser
        factory()
        kwargs = {"user_id": request.user.id}
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK
        assert response.data


@pytest.mark.django_db
class TestSpecificsInfiniteViewsets:
    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (
                ActivityViewSet,
                ActivityFactory,
            ),
        ],
    )
    def test_option_request(self, mvs, factory, superuser):
        request = APIRequestFactory().options("")
        request.user = superuser
        obj = factory(participants=(request.user.profile,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = str(obj.start.date())
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"options": "options"})
        kwargs = get_kwargs(obj, mvs, request=request)
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (
                ActivityViewSet,
                ActivityFactory,
            ),
        ],
    )
    def test_viewsets(self, mvs, factory, superuser):
        request = APIRequestFactory().get("")
        request.user = superuser
        obj = factory(participants=(request.user.profile,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = str(obj.start.date())
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (
                ActivityViewSet,
                ActivityFactory,
            ),
        ],
    )
    def test_viewsets_without_date_gte(self, mvs, factory, superuser):
        request = APIRequestFactory().get("")
        request.user = superuser
        factory(participants=(request.user.profile,))
        request.GET = request.GET.copy()
        request.GET["date_gte"] = None
        kwargs = {}
        mvs.request = request
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs).render()
        assert response.status_code == status.HTTP_200_OK
        assert response.data

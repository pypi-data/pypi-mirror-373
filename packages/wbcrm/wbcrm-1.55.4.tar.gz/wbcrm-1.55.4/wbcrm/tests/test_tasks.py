from datetime import timedelta

import pytest
from django.utils import timezone
from faker import Faker
from wbcore.contrib.directory.models import Company

from wbcrm.factories import ActivityTypeFactory
from wbcrm.models import Activity, ActivityType
from wbcrm.tasks import default_activity_heat_calculation

fake = Faker()


@pytest.mark.django_db
class TestSpecificTasks:
    pass


@pytest.mark.django_db
class TestActivityHeatCalculationTasks:
    @pytest.mark.parametrize("end", [fake.date_time()])
    def test_high_activity_heat(self, company_factory, activity_factory, end):
        end = timezone.make_aware(end)

        high_activity_company_a = company_factory(name="Company A", activity_heat=0.0)
        high_activity_company_b = company_factory(name="Company B", activity_heat=0.0)
        high_activity_company_c = company_factory(name="Company C", activity_heat=0.0)
        activity_factory(
            status=Activity.Status.REVIEWED,
            companies=[high_activity_company_a.id, high_activity_company_b.id],
            type=ActivityTypeFactory(score=ActivityType.Score.HIGH),
            start=end - timedelta(hours=2),
            end=end - timedelta(hours=1),
        )

        activity_factory(
            status=Activity.Status.REVIEWED,
            companies=[high_activity_company_b.id],
            type=ActivityTypeFactory(score=ActivityType.Score.LOW),
            start=end - timedelta(hours=2),
            end=end - timedelta(hours=1),
        )

        activity_factory(
            status=Activity.Status.REVIEWED,
            companies=[
                high_activity_company_c.id,
            ],
            type=ActivityTypeFactory(score=ActivityType.Score.HIGH),
            start=end - timedelta(days=1, hours=2),
            end=end - timedelta(days=1, hours=1),
        )

        default_activity_heat_calculation(end)
        high_activity_company_a: Company = Company.objects.get(id=high_activity_company_a.id)
        high_activity_company_b: Company = Company.objects.get(id=high_activity_company_b.id)
        high_activity_company_c: Company = Company.objects.get(id=high_activity_company_c.id)
        date_score = 365 / 365
        target_score_a = (float(ActivityType.Score.HIGH) * date_score) / float(ActivityType.Score.MAX)
        target_score_b = (
            (float(ActivityType.Score.HIGH) * date_score) + (float(ActivityType.Score.LOW) * date_score)
        ) / float(ActivityType.Score.MAX)
        target_score_c = (float(ActivityType.Score.HIGH) * (364 / 365)) / float(ActivityType.Score.MAX)
        assert round(high_activity_company_a.activity_heat, 1) == round(target_score_a, 1)
        assert round(high_activity_company_b.activity_heat, 1) == round(target_score_b, 1)
        assert round(high_activity_company_c.activity_heat, 1) == round(target_score_c, 1)

    @pytest.mark.parametrize("end", [fake.date_time()])
    def test_low_activity_heat(self, company_factory, activity_factory, end):
        end = timezone.make_aware(end)

        low_activity_company_a = company_factory(name="Company A", activity_heat=0.0)
        low_activity_company_b = company_factory(name="Company B", activity_heat=0.0)
        activity_factory(
            status=Activity.Status.REVIEWED,
            companies=[low_activity_company_a.id],
            type=ActivityTypeFactory(score=ActivityType.Score.LOW),
            start=end - timedelta(hours=2),
            end=end - timedelta(hours=1),
        )
        activity_factory(
            status=Activity.Status.REVIEWED,
            companies=[low_activity_company_b.id],
            type=ActivityTypeFactory(score=ActivityType.Score.HIGH),
            start=end - timedelta(hours=2),
            end=end - timedelta(hours=1),
        )

        default_activity_heat_calculation(end)
        low_activity_company_a = Company.objects.get(id=low_activity_company_a.id)
        date_score = (365 - 100) / 365
        target_score_a = (float(ActivityType.Score.LOW) * date_score) / float(ActivityType.Score.MAX)
        assert round(low_activity_company_a.activity_heat, 1) == round(target_score_a, 1)
        assert low_activity_company_b.activity_heat == 0.0

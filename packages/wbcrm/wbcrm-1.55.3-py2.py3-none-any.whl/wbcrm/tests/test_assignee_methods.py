from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.workflow.factories import (
    ProcessStepFactory,
    RandomChildStepFactory,
    UserStepFactory,
)

from wbcrm.workflows.assignee_methods import activity_assignee


@pytest.mark.django_db
class TestAssigneeMethods:
    api_factory = APIRequestFactory()

    def test_activity_assignee(self, activity_factory):
        user = UserFactory()
        activity = activity_factory(assigned_to=user.profile)
        process_step = ProcessStepFactory(process__instance=activity)
        assert activity_assignee(process_step) == user

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    def test_activity_assignee_no_activity(self, mock_failed):
        step = RandomChildStepFactory(exclude_factories=[UserStepFactory])
        process_step = ProcessStepFactory(step=step)
        assert activity_assignee(process_step) is None
        assert mock_failed.call_args.args[0] == process_step

    @patch("wbcore.contrib.workflow.models.step.Step.set_failed")
    def test_activity_assignee_no_user_account(self, mock_failed, activity_factory):
        assignee = PersonFactory()
        activity = activity_factory(assigned_to=assignee)
        step = RandomChildStepFactory(exclude_factories=[UserStepFactory])
        process_step = ProcessStepFactory(step=step, process__instance=activity)
        assert activity_assignee(process_step) is None
        assert mock_failed.call_args.args[0] == process_step

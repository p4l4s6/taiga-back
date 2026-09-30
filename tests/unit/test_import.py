# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos INC

import pytest
import io
from .. import factories as f

from taiga.base.utils import json
from taiga.export_import.services import render_project, store_project_from_dict

pytestmark = pytest.mark.django_db(transaction=True)


def test_import_epic_with_user_stories(client):
    project = f.ProjectFactory()
    project.default_points = f.PointsFactory.create(project=project)
    project.default_issue_type = f.IssueTypeFactory.create(project=project)
    project.default_issue_status = f.IssueStatusFactory.create(project=project)
    project.default_epic_status = f.EpicStatusFactory.create(project=project)
    project.default_us_status = f.UserStoryStatusFactory.create(project=project)
    project.default_task_status = f.TaskStatusFactory.create(project=project)
    project.default_priority = f.PriorityFactory.create(project=project)
    project.default_severity = f.SeverityFactory.create(project=project)

    epic = f.EpicFactory.create(subject="test epic export", project=project, status=project.default_epic_status)
    user_story = f.UserStoryFactory.create(project=project, status=project.default_us_status, milestone=None)
    f.RelatedUserStory.create(epic=epic, user_story=user_story, order=55)
    output = io.BytesIO()
    render_project(user_story.project, output)
    project_data = json.loads(output.getvalue())

    epic.project.delete()

    project = store_project_from_dict(project_data)
    assert project.epics.count() == 1
    assert project.epics.first().ref == epic.ref

    assert project.epics.first().user_stories.count() == 1
    related_userstory = project.epics.first().relateduserstory_set.first()
    assert related_userstory.user_story.ref == user_story.ref
    assert related_userstory.order == 55
    assert related_userstory.epic.ref == epic.ref


def _minimal_project(**kwargs):
    project = f.ProjectFactory(**kwargs)
    project.default_points = f.PointsFactory.create(project=project)
    project.default_issue_type = f.IssueTypeFactory.create(project=project)
    project.default_issue_status = f.IssueStatusFactory.create(project=project)
    project.default_epic_status = f.EpicStatusFactory.create(project=project)
    project.default_us_status = f.UserStoryStatusFactory.create(project=project)
    project.default_task_status = f.TaskStatusFactory.create(project=project)
    project.default_priority = f.PriorityFactory.create(project=project)
    project.default_severity = f.SeverityFactory.create(project=project)
    project.save()
    return project


def test_export_includes_project_code():
    project = _minimal_project(project_code="WD")
    output = io.BytesIO()
    render_project(project, output)
    project_data = json.loads(output.getvalue())
    assert project_data["project_code"] == "WD"


def test_import_project_code_roundtrip_when_no_collision():
    project = _minimal_project(project_code="WD")
    output = io.BytesIO()
    render_project(project, output)
    project_data = json.loads(output.getvalue())

    project.delete()

    imported = store_project_from_dict(project_data)
    assert imported.project_code == "WD"


def test_import_project_code_collision_blanks_code_instead_of_failing():
    # An existing project already owns "WD" and is NOT deleted, so the
    # imported dict's project_code would collide (D33: blank code on
    # collision, import still succeeds rather than failing outright).
    _minimal_project(project_code="WD")

    other_project = _minimal_project(project_code="OTHER")
    output = io.BytesIO()
    render_project(other_project, output)
    project_data = json.loads(output.getvalue())
    other_project.delete()

    # Simulate an export file that (for whatever reason) claims the same
    # code as the still-existing project above.
    project_data["project_code"] = "wd"

    imported = store_project_from_dict(project_data)
    assert imported is not None
    assert imported.project_code is None

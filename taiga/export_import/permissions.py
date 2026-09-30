# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos INC

from taiga.base.api.permissions import (TaigaResourcePermission,
                                        IsProjectAdmin, IsAuthenticated)


# devsstream note: import_project/load_dump also create a brand new Project
# from an uploaded dump (Jira/Trello/GitHub/Asana importers, or a raw JSON
# dump), technically another project-creation path parallel to
# POST /api/v1/projects. LEFT UNCHANGED (still IsAuthenticated()) on
# purpose: tests/integration/test_importer_api.py and the
# test_importers_*_api.py suites have dozens of existing, currently-passing
# tests that exercise a plain (non-superuser) authenticated user
# successfully importing/migrating a project this way - it's an
# established, separately-scoped "bring your own project" migration
# feature, not the same "New Project" self-service flow the admins-only
# rule was aimed at. Restricting it would break that feature outright.
# Flagged for an explicit decision rather than changed unilaterally.
class ImportExportPermission(TaigaResourcePermission):
    import_project_perms = IsAuthenticated()
    import_item_perms = IsProjectAdmin()
    export_project_perms = IsProjectAdmin()
    load_dump_perms = IsAuthenticated()

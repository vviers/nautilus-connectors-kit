# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from unittest import TestCase, mock
from datetime import datetime

from nck.clients.dcm_client import DCMClient


class MockService:
    def dimensionValues(self):
        return self

    def query(self, *args, **kwargs):
        return self

    def execute(self):
        return True


def mock_service(*args, **kwargs):
    return MockService()


class DCMClientTest(TestCase):
    def mock_dcm_client(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    kwargs = {"_service": mock_service()}

    @mock.patch.object(DCMClient, "__init__", mock_dcm_client)
    def test_add_report_criteria(self):
        report = {"name": "report"}
        start = datetime(year=2020, month=1, day=1)
        end = datetime(year=2020, month=2, day=1)
        elements = ["a", "b"]
        DCMClient(**self.kwargs).add_report_criteria(report, start, end, elements, elements)
        expected = {
            "name": "report",
            "criteria": {
                "dateRange": {"startDate": "2020-01-01", "endDate": "2020-02-01"},
                "dimensions": [{"name": "a"}, {"name": "b"}],
                "metricNames": ["a", "b"],
            },
        }
        assert report == expected

    @mock.patch.object(DCMClient, "__init__", mock_dcm_client)
    @mock.patch.object(MockService, "execute", lambda *args: {"items": [{"value": "ok"}, {"value": "nok"}]})
    @mock.patch("tests.clients.test_dcm_client.MockService")
    def test_add_dimension_filters(self, mock_filter):
        report = {"criteria": {"dateRange": {"endDate": "", "startDate": ""}}}
        profile_id = ""
        filters = [("filter", "ok")]
        DCMClient(**self.kwargs).add_dimension_filters(report, profile_id, filters)
        expected = {"criteria": {"dateRange": {"endDate": "", "startDate": ""}, "dimensionFilters": [{"value": "ok"}]}}
        assert report == expected

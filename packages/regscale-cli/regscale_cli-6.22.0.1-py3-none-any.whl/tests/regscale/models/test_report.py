#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
from unittest.mock import patch, MagicMock
import pytest

from regscale.core.app.utils.report_utils import ReportGenerator
from regscale.models import Asset
from tests import CLITestFixture


class TestReportGenerator(CLITestFixture):
    """Test for Report Generator with dynamic test data and no hard-coded IDs"""

    @pytest.fixture(autouse=True)
    def setup_report_test(self):
        """Setup the test with dynamic test data"""
        self.test_uuid = str(uuid.uuid4())
        self.test_parent_id = int(uuid.uuid4().hex[:8], 16)
        self.test_parent_module = "securityplans"
        self.test_report_name = f"test_report_{self.test_uuid[:8]}"

    @pytest.fixture
    def mock_assets(self):
        """Mock assets for testing"""
        assets = []
        for i in range(1, 4):
            asset = MagicMock()
            asset.id = i
            asset.name = f"Test Asset {i}"
            asset.title = f"Test Asset Title {i}"
            asset.description = f"Test asset description {i}"
            asset.status = "Active"
            asset.dateCreated = "2024-01-01 10:00:00"
            asset.dateLastUpdated = "2024-01-01 10:00:00"
            asset.createdById = self.config.get("userId", "1")
            asset.lastUpdatedById = self.config.get("userId", "1")
            assets.append(asset)
        return assets

    @patch("regscale.models.Asset.get_all_by_parent")
    def test_basic_report(self, mock_get_assets, mock_assets):
        """Test the basic report generation"""
        mock_get_assets.return_value = mock_assets
        assets = Asset.get_all_by_parent(self.test_parent_id, self.test_parent_module)
        generator = ReportGenerator(assets)
        assert len(generator.objects) == 3
        assert generator.to_file is False
        assert generator.report_name == ""
        assert generator.regscale_id is None
        assert generator.regscale_module is None

    @patch("regscale.models.Asset.get_all_by_parent")
    def test_advanced_report(self, mock_get_assets, mock_assets):
        """Test the advanced report generation with file output"""
        mock_get_assets.return_value = mock_assets
        assets = Asset.get_all_by_parent(self.test_parent_id, self.test_parent_module)
        generator = ReportGenerator(objects=assets, to_file=True, report_name=self.test_report_name)
        assert len(generator.objects) == 3
        assert generator.to_file is True
        assert generator.report_name == self.test_report_name
        assert generator.regscale_id is None
        assert generator.regscale_module is None

    @patch("regscale.models.Asset.get_all_by_parent")
    def test_save_to_regscale(self, mock_get_assets, mock_assets):
        """Test saving the report to RegScale"""
        mock_get_assets.return_value = mock_assets
        assets = Asset.get_all_by_parent(self.test_parent_id, self.test_parent_module)
        generator = ReportGenerator(
            objects=assets,
            to_file=True,
            report_name=self.test_report_name,
            regscale_id=self.test_parent_id,
            regscale_module=self.test_parent_module,
        )
        assert len(generator.objects) == 3
        assert generator.to_file is True
        assert generator.report_name == self.test_report_name
        assert generator.regscale_id == self.test_parent_id
        assert generator.regscale_module == self.test_parent_module

    def test_report_data_method(self, mock_assets):
        """Test the report_data method"""
        generator = ReportGenerator(mock_assets)
        report_data = generator.report_data()
        assert report_data == mock_assets
        assert len(report_data) == 3

    def test_report_attributes(self, mock_assets):
        """Test that report attributes are properly set"""
        generator = ReportGenerator(mock_assets)
        assert "id" in generator.attributes
        assert "name" in generator.attributes
        assert "title" in generator.attributes
        assert "description" in generator.attributes
        assert "status" in generator.attributes
        assert "dateCreated" in generator.attributes
        assert "dateLastUpdated" in generator.attributes

    @patch("regscale.models.Asset.get_all_by_parent")
    def test_empty_objects_report(self, mock_get_assets):
        """Test report generation with empty objects"""
        mock_get_assets.return_value = []
        assets = Asset.get_all_by_parent(self.test_parent_id, self.test_parent_module)
        generator = ReportGenerator(assets)
        assert len(generator.objects) == 0
        assert generator.attributes == []

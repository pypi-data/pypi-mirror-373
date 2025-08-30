import json
import tempfile
from pathlib import Path

import pytest

from regscale.core.app.api import Api
from regscale.core.app.utils.catalog_utils.download_catalog import get_new_catalog
from regscale.core.app.utils.catalog_utils.update_catalog_v2 import import_catalog
from regscale.models.app_models.catalog_compare import CatalogCompare
from regscale.models.regscale_models import Catalog
from tests.fixtures.test_fixture import CLITestFixture


class TestImport(CLITestFixture):
    """
    Test for AWS integration
    """

    @pytest.fixture(autouse=False)
    def setup(self, catalog_id):
        # Setup code goes here. This will execute before each test method.
        print("Setting up before test")
        my_dir = tempfile.mkdtemp()
        api = Api()
        # You can initialize variables, create necessary objects, or set up any necessary preconditions for the test here.
        data = CatalogCompare.get_master_catalogs(api=api)
        # download json file with requests
        for catalog in data["catalogs"]:
            if catalog["downloadURL"] and catalog["title"] == "Australian Information Security Manual (ISM)":
                url = catalog["downloadURL"]
                name = Path(catalog["downloadURL"]).name
                cat = get_new_catalog(url=url)
                with open(Path(tempfile.gettempdir()) / my_dir / name, "w") as f:
                    json.dump(cat, f)
                catalog_id["name"] = name
                catalog_id["file"] = Path(tempfile.gettempdir()) / my_dir / name
                break
        # Download a bad file
        bad_url = (
            "https://gist.githubusercontent.com/moredip/4165313/raw/ad00ee5bc70016a70976736d5cdf0463d5f7ea15/test.json"
        )
        bad_name = Path(bad_url).name
        bad_cat = get_new_catalog(url=bad_url)
        catalog_id["bad_name"] = "Invalid JSON"
        catalog_id["bad_file"] = Path(tempfile.gettempdir()) / my_dir / bad_name
        with open(catalog_id["bad_file"], "w") as bad_file:
            json.dump(bad_cat, bad_file)

    @pytest.fixture(scope="module")
    def catalog_id(self):
        return {}

    @pytest.fixture(autouse=False)
    def teardown(self, catalog_id):
        yield  # This is where the test function will execute
        # Teardown code goes here. This will execute after each test method.
        print("Tearing down after test")

        if cat_id := catalog_id.get("id"):
            if cat := Catalog.get_object(cat_id):
                assert cat.delete() is True

    def test_import_catalog_invalid(self, setup, catalog_id):
        # Arrange
        catalog_path = Path(catalog_id["bad_file"])

        # Act
        res = import_catalog(catalog_path)
        # Assert
        assert res.json()["success"] is False

    # @pytest.skip("Skipping test because the API keeps timing out even in the application.")
    def test_import_catalog_valid(self, setup, teardown, catalog_id):
        # Arrange
        catalog_path = Path(catalog_id["file"])
        # change the catalog name to include the name of the test run id
        with open(catalog_path, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        with open(catalog_path, "w", encoding="utf-8") as outfile:
            current_title = data["catalog"]["title"]
            data["catalog"]["title"] = self.title_prefix + current_title
            json.dump(data, outfile, indent=4)

        # Act
        res = import_catalog(catalog_path)
        if res.status_code == 400 and res.text == "Catalog already exists":
            pytest.skip("Catalog already exists. Most likely due to another test. Skipping import.")
        # Assert
        assert res.json()["success"] is True
        cat_id = res.json()["catalogId"]
        catalog_id["id"] = cat_id
        assert cat_id is not None

        # delete the catalog
        new_cat = Catalog.get_object(cat_id)
        assert new_cat.delete() is True

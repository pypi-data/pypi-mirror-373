from regscale.models.app_models.mapping import Mapping
import json

MAPPING_TEMPLATE = {
    "mapping": {
        "Pickles": "Pickles",
        "IP Address": "IP Address",
        "Hostname": "Hostname",
        "OS": "OS",
        "Vulnerability Title": "Vulnerability Title",
        "Vulnerability ID": "Vulnerability ID",
        "CVSSv2 Score": "CVSSv2 Score",
        "CVSSv3 Score": "CVSSv3 Score",
        "Description": "Description",
        "Proof": "Proof",
        "Solution": "Solution",
        "CVEs": "CVEs",
    }
}


def test_mapping_validation():
    """
    Test the Mapping class validation
    """
    expected_field_names = [
        "IP Address",
        "Hostname",
        "OS",
        "Vulnerability Title",
        "Vulnerability ID",
        "CVSSv2 Score",
        "CVSSv3 Score",
        "Description",
        "Proof",
        "Solution",
        "CVEs",
    ]
    mapping = Mapping(mapping=MAPPING_TEMPLATE["mapping"], expected_field_names=expected_field_names)

    assert mapping


def test_mapping_no_validation():
    """
    Test the Mapping class validation
    """

    expected_field_names = ["Pickles"]
    mapping = Mapping(mapping=MAPPING_TEMPLATE["mapping"], expected_field_names=expected_field_names)

    assert mapping

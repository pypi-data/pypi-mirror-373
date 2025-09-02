import pandas as pd
import pytest

from dataio._classifications_helper import *


@pytest.fixture
def setup_classification_data():
    # Example classification data setup
    data = [
        [
            "C_ANTH",
            "0100",
            "many-to-many correspondence",
            "9e3aea85-6ef1-49ab-98df-e0bdf80644af",
            "http://www.w3.org/2004/02/skos/core#relatedMatch",
        ],
        [
            "C_COKC",
            "0100",
            "many-to-many correspondence",
            "2e4de738-b168-46d8-9132-086586cd44d5",
            "http://www.w3.org/2004/02/skos/core#relatedMatch",
        ],
        [
            "C_ANTH",
            "0110",
            "one-to-many correspondence",
            "f7c57ebe-1027-47ea-ab76-27058ae87a28",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
        [
            "C_COKC",
            "0121",
            "one-to-many correspondence",
            "c4f4f717-0556-448c-8226-7d247e684e6d",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
        [
            "C_OTBC",
            "0129",
            "one-to-many correspondence",
            "e2e7da7f-00a1-411c-88f9-faaae7b89906",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
    ]

    columns = [
        "bonsai_classification",
        "source_classification",
        "comment",
        "uuid",
        "relation",
    ]
    classification = pd.DataFrame(data, columns=columns)

    return classification


def test_filter_classifications(setup_classification_data):

    classification = setup_classification_data

    data = pd.DataFrame(
        [["a", "0121"], ["0121", "0129"], ["0121", "0130"]], columns=["one", "two"]
    )

    filtered_table = filter_classifications(
        classification, data["two"].unique(), "source_classification"
    )
    assert len(filtered_table) == 2


def test_filter_classifications_with_regex():
    classification_data = [
        [
            "C_ANTH",
            "0100",
            "many-to-many correspondence",
            "9e3aea85-6ef1-49ab-98df-e0bdf80644af",
            "http://www.w3.org/2004/02/skos/core#relatedMatch",
        ],
        [
            "C_COKC",
            "0100",
            "many-to-many correspondence",
            "2e4de738-b168-46d8-9132-086586cd44d5",
            "http://www.w3.org/2004/02/skos/core#relatedMatch",
        ],
        [
            "C_ANTH",
            "0110",
            "one-to-many correspondence",
            "f7c57ebe-1027-47ea-ab76-27058ae87a28",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
        [
            "C_COKC",
            "Co[k]?e",
            "one-to-many correspondence",
            "c4f4f717-0556-448c-8226-7d247e684e6d",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
        [
            "C_OTBC",
            "0129",
            "one-to-many correspondence",
            "e2e7da7f-00a1-411c-88f9-faaae7b89906",
            "http://www.w3.org/2004/02/skos/core#closeMatch",
        ],
    ]

    columns = [
        "bonsai_classification",
        "source_classification",
        "comment",
        "uuid",
        "relation",
    ]
    classification = pd.DataFrame(classification_data, columns=columns)

    data = pd.DataFrame(
        [["a", "Coke"], ["0121", "no_match"], ["0121", "also_no_match"]],
        columns=["one", "two"],
    )

    filtered_table = filter_classifications(
        classification, data["two"].unique(), "source_classification", using_regex=True
    )
    assert len(filtered_table) == 1


def test_find_nearest_parent():
    bonsai_codes = ["A", "B", "C"]
    tree_bonsai_df = pd.DataFrame(
        {
            "code": ["A", "B", "C", "D", "E"],
            "parent_code": [None, "A", "A", "B", "B"],
            "level": [0, 1, 1, 2, 2],
        }
    )

    common_parent, max_steps = find_nearest_parent(bonsai_codes, tree_bonsai_df)

    assert common_parent == "A"
    assert max_steps == 1


def test_combine_duplicates():
    # Test data
    data = {
        "time": ["2024-08-16", "2024-08-16", "2024-08-17", "2024-08-16"],
        "location": ["Store1", "Store1", "Store2", "Store1"],
        "product": ["ProductA", "ProductA", "ProductB", "ProductA"],
        "unit": ["Box", "Box", "Box", "Box"],
        "value": [10, 15, 5, 20],
        "extra_info": ["Info1", "Info2", "Info3", "Info4"],  # Additional column
    }

    df = pd.DataFrame(data)

    # Expected result after combining duplicates
    expected_data = {
        "time": ["2024-08-16", "2024-08-17"],
        "location": ["Store1", "Store2"],
        "product": ["ProductA", "ProductB"],
        "unit": ["Box", "Box"],
        "value": [45, 5],  # 10 + 15 + 20 = 45
        "extra_info": ["Info1", "Info3"],  # Keep first occurrence
    }
    expected_df = pd.DataFrame(expected_data)

    # Run the combine_duplicates function
    result_df = combine_duplicates(df)

    # Test if the result matches the expected output
    assert result_df.equals(
        expected_df
    ), "Test failed: The combined DataFrame does not match the expected output."


def test_increment_version_patch():
    assert increment_version("1.0.0") == "1.0.1"
    assert increment_version("2.5.9") == "2.5.10"
    assert increment_version("0.0.9") == "0.0.10"
    assert increment_version("3.9.99") == "3.9.100"


def test_increment_version_minor():
    assert increment_version("1.0") == "1.1"
    assert increment_version("2.5") == "2.6"


def test_increment_version_major():
    assert increment_version("1") == "2"
    assert increment_version("9") == "10"


def test_increment_version_invalid_format():
    # Test case for empty string
    try:
        increment_version("")
        assert False, "Expected ValueError for empty string"
    except ValueError:
        pass  # Expected outcome

    # Test case for non-numeric values
    try:
        increment_version("abc.def.ghi")
        assert False, "Expected ValueError for non-numeric input"
    except ValueError:
        pass  # Expected outcome

from collections import defaultdict

import pandas as pd


def filter_classifications(
    correspondence, unique_values, origin_column, using_regex=False
) -> dict[str, str]:
    """
    returns a filtered correspondence without many-to-many relations
    this is needed as many-to-many relations cannot be resolved
    automatically
    This also makes sure that only relavent correspondences are used
    filtered by the unique names.
    If using_regex is True then the function will make sure to already,
    parse potential fields and create a custom correspondence, this is done
    in order to not have to do regex matching when applying the mapping to the
    full dataset.
    """
    # change correspondence for regex values
    if using_regex:
        import re

        mapping_for_matched_regex = {}
        for regex in correspondence[origin_column]:
            for unique_value in unique_values:
                if re.findall(regex, unique_value):
                    assert (
                        regex not in mapping_for_matched_regex
                    ), f"Classification regex {regex} matched more then a single unique value, this should not be possible. Please revise classification regex."
                    mapping_for_matched_regex[regex] = unique_value

        correspondence[origin_column] = correspondence[origin_column].apply(
            lambda x: (
                mapping_for_matched_regex[x]
                if x in mapping_for_matched_regex.keys()
                else x
            )
        )

    # Make sure that only actually used unique values are in the correspondence
    correspondence = correspondence[correspondence[origin_column].isin(unique_values)]

    # Identify the many-to-many correspondences
    many_to_many = correspondence[
        correspondence["comment"] == "many-to-many correspondence"
    ]

    # Create a set of classifications involved in many-to-many relationships
    involved_classifications = set(many_to_many.iloc[:, 0]).union(
        set(many_to_many.iloc[:, 1])
    )

    # Identify rows involved in many-to-many relationships
    relations_to_ignore = correspondence[
        correspondence.iloc[:, 0].isin(involved_classifications)
        | correspondence.iloc[:, 1].isin(involved_classifications)
    ]

    # Create the filtered table by excluding the rows involved in many-to-many relationships
    filtered_table = correspondence[
        ~correspondence.index.isin(relations_to_ignore.index)
    ]

    return filtered_table


def generate_classification_mapping_multi_column(
    filtered_table, target_columns
) -> tuple[dict[tuple, (tuple, str)], set[tuple]]:
    mapping = {}
    # accounttype = []
    many_to_one = defaultdict(list)  # Reverse lookup for many-to-one

    for _, row in filtered_table.iterrows():
        to_tuple = tuple(row[f"{col}_to"] for col in target_columns)
        from_tuple = tuple(row[f"{col}_from"] for col in target_columns)
        comment = row["comment"]
        # accounttype = row["accounttype"]

        if comment == "one-to-one correspondence":
            mapping[from_tuple] = to_tuple

        elif comment == "many-to-one correspondence":
            mapping[from_tuple] = to_tuple
            many_to_one[to_tuple].append(from_tuple)

        elif comment == "one-to-many correspondence":
            if from_tuple in mapping:
                # Extend existing tuple by joining new values with '|'
                mapping[from_tuple] = tuple(
                    f"{mapping[from_tuple][i]}|{to_tuple[i]}"
                    for i in range(len(to_tuple))
                )
            else:
                mapping[from_tuple] = to_tuple

    return mapping, many_to_one


def generate_classification_mapping(
    filtered_table, target_column
) -> tuple[dict[str, str], set[str]]:
    mapping = {}
    from_col = target_column + "_from"
    to_col = target_column + "_to"

    # Collect many-to-one correspondences into a set
    many_to_one = set(
        filtered_table.loc[
            filtered_table["comment"] == "many-to-one correspondence", to_col
        ]
    )

    # Find one-to-many correspondences and join the codes in 'to_col'
    one_to_many_mask = filtered_table["comment"] == "one-to-many correspondence"
    filtered_table.loc[one_to_many_mask, to_col] = (
        filtered_table.loc[one_to_many_mask]
        .groupby(from_col)[to_col]
        .transform(lambda x: "|".join(x))
    )
    # Combine the from_col and to_col into a dictionary
    mapping = dict(zip(filtered_table[from_col], filtered_table[to_col]))

    return mapping, many_to_one


def find_nearest_parent(bonsai_codes, tree_bonsai_df):
    tree = build_tree(tree_bonsai_df)
    paths = {code: find_path_to_root(code, tree) for code in bonsai_codes}

    common_parent = None
    min_steps = float("inf")

    for i, (code1, path1) in enumerate(paths.items()):
        for j, (code2, path2) in enumerate(paths.items()):
            if i >= j:
                continue
            common, steps = find_common_ancestor_and_steps(path1, path2)
            if steps < min_steps:
                common_parent = common
                min_steps = steps

    # Calculate the maximum number of steps to the common ancestor for all paths
    max_steps = 0
    for path in paths.values():
        steps_to_common = find_steps_to_common_ancestor_using_levels(
            path, tree_bonsai_df, common_parent
        )
        if steps_to_common > max_steps:
            max_steps = steps_to_common

    return common_parent, max_steps


def build_tree(df):
    tree = {}
    for _, row in df.iterrows():
        tree[row["code"]] = row["parent_code"]
    return tree


def find_path_to_root(code, tree):
    path = []
    while code:
        path.append(code)
        code = tree.get(code)
    return path[::-1]


def find_common_ancestor_and_steps(path1, path2):
    common_ancestor = None
    steps = 0
    for code1, code2 in zip(path1, path2):
        if code1 == code2:
            common_ancestor = code1
        else:
            break
        steps += 1
    return common_ancestor, steps


def find_steps_to_common_ancestor_using_levels(path, tree_bonsai_df, common_ancestor):
    # Find the relevant levels in the DataFrame
    levels = tree_bonsai_df.loc[tree_bonsai_df["code"].isin(path)]["level"]

    # Check if levels is empty
    if levels.empty:
        return 0

    max_level = max(levels)
    min_level = min(levels)

    return max_level - min_level


def combine_duplicates(df):
    """
    Combine duplicate rows in a DataFrame by summing up their 'value' column, treating None values as 0.

    Parameters:
    df (pd.DataFrame): Input DataFrame with potential duplicate rows.

    Returns:
    pd.DataFrame: Combined DataFrame with duplicates merged.
    """
    # Define the columns to check for duplicates
    overlap_columns = ["time", "location", "product", "unit"]

    # Define the value column that needs to be summed
    value_column = "value"

    # Ensure that the value column is in the DataFrame
    if value_column not in df.columns:
        raise ValueError(f"The DataFrame does not contain a '{value_column}' column.")

    # Convert the value column to numeric, coercing errors to NaN
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(
        0.0
    )  # Replace NaNs with 0.0

    # Group by the overlap columns and aggregate using sum for the value column
    combined_df = df.groupby(overlap_columns, as_index=False).agg(
        {
            value_column: "sum",
            **{
                col: "first"
                for col in df.columns
                if col not in overlap_columns and col != value_column
            },
        }
    )

    return combined_df


def count_rows_with_values(
    df: pd.DataFrame, column_name: str, values_list: list
) -> int:
    """
    Counts the number of rows in a DataFrame where the specified column contains any of the given values.

    Parameters:
    - df (pd.DataFrame): The DataFrame to search within.
    - column_name (str): The name of the column to check.
    - values_list (list): The list of values to look for in the specified column.

    Returns:
    - int: The count of rows that have any of the specified values in the given column.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    if not isinstance(values_list, list):
        raise TypeError("The 'values_list' parameter should be a list.")

    # Count rows where the column has values in values_list
    count = df[df[column_name].isin(values_list)].shape[0]
    return count


def increment_version(version):
    # Split the version string into its components
    version_parts = version.split(".")

    # Convert the last part to an integer and increment it
    version_parts[-1] = str(int(version_parts[-1]) + 1)

    # Reassemble the parts back into a string
    new_version = ".".join(version_parts)

    return new_version

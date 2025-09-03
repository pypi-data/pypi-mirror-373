from mammoth_commons.integration import loader
from mammoth_commons.models.researcher_ranking import ResearcherRanking
from random import choices


def normal_ranking(dataset, ranking_variable):
    """
    Rank a dataset based on a specified variable in descending order.

    This function sorts the input dataset based on the values of the given ranking variable,
    and assigns a ranking score to each entry. The highest value for the ranking variable receives
    a rank of 1, and the ranking increases for lower values.

    Parameters:
    dataset (pandas.DataFrame): The dataset to be ranked, provided as a pandas DataFrame.
    ranking_variable (str): The name of the column in the dataset to use for ranking.

    Returns:
    pandas.DataFrame: A new DataFrame containing the original dataset sorted by ranking_variable
                  in descending order, with an additional column 'Ranking_{ranking_variable}'
                  that contains the corresponding rank for each entry.
    """

    ranked_dataset = dataset.sort_values(ranking_variable, ascending=False)
    ranked_dataset[f"Ranking_{ranking_variable}"] = [
        i + 1 for i in range(ranked_dataset.shape[0])
    ]
    return ranked_dataset


def Compute_mitigation_strategy(
    dataset,
    mitigation_method,
    ranking_variable,
    sensitive_attribute,
    protected_attribute,
):
    """
    Computes a ranking adjustment based on selected mitigation strategies to ensure fairness in dataset.

    Parameters:
    -----------
    dataset : pd.DataFrame
        A pandas DataFrame containing the data to be ranked, including sensitive and protected attributes.

    mitigation_method : str
        The method of mitigation to apply. Options include:
        - "Statistical_parity": Adjusts ranking to balance representation between protected and non-protected groups.
        - "Equal_parity": Assumes equal distribution for protected and non-protected groups.
        - "Updated_statistical_parity": Not yet implemented.
        - "Internal_group_fairness": Not yet implemented.

    ranking_variable : str
        The name of the new ranking variable to be added to the dataset.

    sensitive_attribute : str
        The name of the column in the dataset that contains sensitive attribute values.

    protected_attribute : str
        The name of the specific sensitive attribute that is considered protected and requires fairness adjustment.

    Returns:
    --------
    pd.DataFrame
        A pandas DataFrame with updated rankings based on the specified mitigation strategy.

    Raises:
    -------
    NotImplementedError
        If "Updated_statistical_parity" or "Internal_group_fairness" is selected as the mitigation method.
    """
    # Filter out rows with null values in the sensitive attribute
    Dataframe_ranking = dataset[~dataset[sensitive_attribute].isnull()]

    # Initialize dictionaries to store chosen groups and researchers
    Chosen_groups, Chosen_researchers = {}, {}

    # Create a set of unique sensitive attribute values from the dataframe
    sensitive = set(Dataframe_ranking[sensitive_attribute])

    # Create subsets of the data for each group based on the sensitive attribute
    Ranking_sets = {
        attribute: Dataframe_ranking[
            Dataframe_ranking[sensitive_attribute] == attribute
        ]
        for attribute in sensitive
    }

    # Identify the non-protected attribute
    non_protected_attribute = [i for i in sensitive if i != protected_attribute][0]

    # Count the number of instances in each sensitive group
    Len_groups = Dataframe_ranking[sensitive_attribute].value_counts()

    # Apply the statistical parity mitigation strategy
    if mitigation_method == "Statistical_parity":
        Chosen_groups = []
        Len_group_in_ranking = Len_groups
        for i in range(Dataframe_ranking.shape[0]):
            # Calculate probability of selecting the protected attribute
            P_minority = Len_group_in_ranking[protected_attribute] / (
                Len_group_in_ranking[protected_attribute]
                + Len_group_in_ranking[non_protected_attribute]
            )
            # Select group based on probability
            Chosen_groups += [
                choices(
                    [protected_attribute, non_protected_attribute],
                    [P_minority, 1 - P_minority],
                )[0]
            ]
            Len_group_in_ranking[Chosen_groups[-1]] -= 1
    elif mitigation_method == "Equal_parity":
        P_minority = 0.5
    elif mitigation_method == "Updated_statistical_parity":
        raise NotImplementedError(
            "Updated_statistical_parity method is not implemented yet."
        )
    elif mitigation_method == "Internal_group_fairness":
        raise NotImplementedError(
            "Internal_group_fairness method is not implemented yet."
        )

    # Set equal parity chance for protection
    Positions = {
        non_protected_attribute: [
            i for i, j in enumerate(Chosen_groups) if j == non_protected_attribute
        ],
        protected_attribute: [
            i for i, j in enumerate(Chosen_groups) if j == protected_attribute
        ],
    }

    # Create a mapping of chosen researchers based on selection positions
    Chosen_researchers = {
        i_ranking: Ranking_sets[non_protected_attribute].iloc[i_position]["id"]
        for i_position, i_ranking in enumerate(Positions[non_protected_attribute])
    }
    for i_position, i_ranking in enumerate(Positions[protected_attribute]):
        Chosen_researchers[i_ranking] = Ranking_sets[protected_attribute].iloc[
            i_position
        ]["id"]

    # Create a new ranking based on the chosen researchers
    New_ranking = {r: i for i, r in Chosen_researchers.items()}

    # Assign new ranking values to the dataframe
    Dataframe_ranking["Ranking_" + ranking_variable] = [
        New_ranking[i] + 1 for i in Dataframe_ranking.id
    ]

    return Dataframe_ranking


def mitigation_ranking(
    dataset,
    ranking_variable,
    mitigation_method="Statistical_parity",
    sensitive_attribute="Gender",
    protected_attribute="female",
):
    """
    Ranks mitigation strategies based on specified parameters to reduce bias in a given dataset.

    Args:
        dataset (pd.DataFrame): The input dataset to be analyzed, typically a Pandas DataFrame.
        ranking_variable (str): The variable used for ranking the mitigation strategies.
        mitigation_method (str, optional): The method used to implement mitigation strategy.
                                            Default is "Statistical_parity".
        sensitive_attribute (str, optional): The attribute that may carry bias, such as "Gender" or "Race".
                                              Default is "Gender".
        protected_attribute (str, optional): The specific value of the sensitive attribute considered
                                             as protected (e.g., "female" for Gender). Default is "female".

    Returns:
        pd.DataFrame: A DataFrame containing the results of the mitigation strategy computation,
                       including rankings based on the specified mitigation method.

    Example:
        result_df = mitigation_ranking(my_dataset, 'income', 'Equalized_odds', 'Gender', 'male')

    Notes:
        This function utilizes the Compute_mitigation_strategy function to perform the actual
        mitigation ranking computation based on the given parameters.
    """

    # Call the computation function with the provided parameters to obtain ranked mitigations
    return Compute_mitigation_strategy(
        dataset,
        mitigation_method,
        ranking_variable,
        sensitive_attribute,
        protected_attribute,
    )


def model_normal_ranking() -> ResearcherRanking:
    """
    Load and return a Normal Ranking of researchers.

    This function initializes the normal ranking model and returns
    an instance of the ResearcherRanking class containing the ranking data.

    Returns:
        ResearcherRanking: An instance of the ResearcherRanking class
        populated with normal ranking data.
    """
    # Call the ResearcherRanking constructor with 'normal_ranking' as an argument
    return ResearcherRanking(normal_ranking)


@loader(namespace="csh", version="v002", python="3.13")
def model_mitigation_ranking() -> ResearcherRanking:
    """
    Load the researcher ranking model incorporating a mitigation strategy.

    This function implements a fair ranking mechanism utilizing a sampling technique. It applies a
    mitigation strategy based on Statistical Parity, which aims to ensure equitable treatment
    across different groups by mitigating bias in the ranking process. Additionally, it compares
    the results of this fair ranking with a standard ranking derived from one of the numerical columns.

    Returns:
        ResearcherRanking: An instance of ResearcherRanking that contains both the mitigation-based
        ranking and the standard ranking for comparison.
    """
    # Invoke the ResearcherRanking constructor with both mitigation and normal rankings.
    return ResearcherRanking(mitigation_ranking, normal_ranking)

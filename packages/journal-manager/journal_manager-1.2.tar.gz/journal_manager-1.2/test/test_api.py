from danoan.journal_manager.core import api, model

import pytest


@pytest.fixture
def journal_data_list():
    journal_db = []
    journal_db.append(
        model.JournalData(
            "largue-language-models",
            "/home/user/journals/largue-language-models",
            True,
            "Large Language Models",
            "2023-10-11T09:14:32.914681",
        )
    )

    journal_db.append(
        model.JournalData(
            "traveling",
            "/home/user/journals/traveling",
            True,
            "Traveling",
            "2023-10-13T09:14:32.914681",
        )
    )

    journal_db.append(
        model.JournalData(
            "theater",
            "/home/user/journals/theater",
            False,
            "Theater",
            "2023-10-13T09:14:32.914681",
        )
    )

    return model.JournalDataList(journal_db)


def test_find_journal_by_name(journal_data_list):
    journal_query = model.JournalData(
        "largue-language-models", None, None, None, None
    )
    results = api.find_journal(
        journal_data_list, journal_query, model.LogicOperator.AND
    )
    assert results and results[0] == journal_data_list.list_of_journal_data[0]


def test_find_journal_by_location(journal_data_list):
    journal_query = model.JournalData(
        None, "/home/user/journals/traveling", None, None, None
    )
    results = api.find_journal(
        journal_data_list, journal_query, model.LogicOperator.AND
    )
    assert results and results[0] == journal_data_list.list_of_journal_data[1]


def test_find_journal_by_active_status(journal_data_list):
    journal_query = model.JournalData(None, None, True, None, None)
    results = api.find_journal(
        journal_data_list, journal_query, model.LogicOperator.AND
    )
    assert results and len(results) == 2
    assert results[0] == journal_data_list.list_of_journal_data[0]
    assert results[1] == journal_data_list.list_of_journal_data[1]

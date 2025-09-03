import types
import pandas as pd
import pytest

from pancham.integration.salesforce_rest_update_output import (
    SalesforceRestUpdateOutputConfiguration,
    SalesforceRestUpdateWriter,
    SALESFORCE_REST_UPDATE,
)


class DummyReporter:
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []

    def report_debug(self, msg, payload=None):
        self.debug_calls.append((msg, payload))

    def report_info(self, msg):
        self.info_calls.append(msg)


class DummySObject:
    def __init__(self):
        self.updated = []
        self.raise_on_first = False
        self._raised = False

    def update(self, rec_id, payload):
        if self.raise_on_first and not self._raised:
            self._raised = True
            raise Exception("boom")
        self.updated.append((rec_id, payload))


class DummySalesforce:
    def __init__(self, object_name="Account"):
        o = DummySObject()
        setattr(self, object_name, o)
        self._obj = o


@pytest.fixture
def patch_reporter(monkeypatch):
    rep = DummyReporter()
    monkeypatch.setattr("pancham.integration.salesforce_rest_update_output.get_reporter", lambda: rep)
    return rep


@pytest.fixture
def patch_connection(monkeypatch):
    dummy = DummySalesforce()
    monkeypatch.setattr("pancham.integration.salesforce_rest_update_output.get_connection", lambda: dummy)
    return dummy


def test_configuration_can_apply_and_to_writer_valid():
    cfg = {
        "output_type": SALESFORCE_REST_UPDATE,
        "object_name": "Account",
        "id_column": "Id",
    }
    oc = SalesforceRestUpdateOutputConfiguration()
    assert oc.can_apply(cfg) is True
    writer = oc.to_output_writer(cfg)
    assert isinstance(writer, SalesforceRestUpdateWriter)
    assert writer.object_name == "Account"
    assert writer.id_column == "Id"


def test_configuration_can_apply_missing_key_returns_false():
    cfg = {"some_other": {}}
    oc = SalesforceRestUpdateOutputConfiguration()
    assert oc.can_apply(cfg) is False


def test_configuration_can_apply_raises_without_object(monkeypatch):
    cfg = {"output_type": SALESFORCE_REST_UPDATE}
    oc = SalesforceRestUpdateOutputConfiguration()
    with pytest.raises(ValueError):
        oc.can_apply(cfg)


def test_writer_updates_rows_with_coercion_and_excludes_id(patch_connection, patch_reporter):
    df = pd.DataFrame([
        {"Id": "001A", "Name": "Acme", "Active__c": "true", "EmployeeCount": "10", "Notes__c": None},
        {"Id": "001B", "Name": "Beta", "Active__c": "0", "EmployeeCount": pd.NA, "Notes__c": "hello"},
    ])

    writer = SalesforceRestUpdateWriter({
        "object_name": "Account",
        "id_column": "Id",
        "int_cols": ["EmployeeCount"],
        "bool_cols": ["Active__c"],
        "nullable_cols": ["Notes__c"],
    })

    writer.write(df)

    # Ensure two updates were called
    updated = patch_connection._obj.updated
    assert len(updated) == 2
    # Payload should exclude Id, coerce bool/int, drop None/NaN
    rid, payload = updated[0]
    assert rid == "001A"
    assert payload == {"Name": "Acme", "Active__c": True, "EmployeeCount": 10}

    rid2, payload2 = updated[1]
    assert rid2 == "001B"
    # EmployeeCount was NaN -> removed; Active__c "0" -> False; Notes__c present
    assert payload2 == {"Name": "Beta", "Active__c": False, "Notes__c": "hello"}


def test_writer_empty_dataframe_early_return_logs(patch_connection, patch_reporter):
    df = pd.DataFrame(columns=["Id"])  # empty

    writer = SalesforceRestUpdateWriter({
        "object_name": "Account",
        "id_column": "Id",
    })

    writer.write(df)

    # No updates
    assert patch_connection._obj.updated == []
    # A debug log was recorded
    assert any("no data to write" in msg for msg, _ in patch_reporter.debug_calls)


def test_writer_missing_id_column_raises(patch_connection, patch_reporter):
    df = pd.DataFrame([{"Name": "Acme"}])

    writer = SalesforceRestUpdateWriter({
        "object_name": "Account",
        "id_column": "Id",
    })

    with pytest.raises(ValueError):
        writer.write(df)


def test_writer_handles_missing_id_and_update_exception(patch_connection, patch_reporter):
    # Configure sobject to raise on first update
    patch_connection._obj.raise_on_first = True

    df = pd.DataFrame([
        {"Id": None, "Name": "NoId"},  # missing id -> failure tracked, no update call
        {"Id": "001X", "Name": "WillFail"},  # will raise
        {"Id": "001Y", "Name": "WillSucceed"},  # will succeed
    ])

    writer = SalesforceRestUpdateWriter({
        "object_name": "Account",
        "id_column": "Id",
    })

    writer.write(df)

    # Two attempted updates; first raises, second success
    updated = patch_connection._obj.updated
    assert len(updated) == 1
    assert updated[0][0] == "001Y"

    # Final debug summary should include failure_count >= 2
    summaries = [payload for msg, payload in patch_reporter.debug_calls if msg == 'SalesforceRestUpdateWriter completed']
    assert summaries, "Expected completion summary log"
    summary = summaries[-1]
    assert summary["failure_count"] >= 2
    assert summary["success_count"] == 1

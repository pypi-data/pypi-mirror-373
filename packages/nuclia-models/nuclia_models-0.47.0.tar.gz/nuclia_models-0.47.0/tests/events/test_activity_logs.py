import pytest

from nuclia_models.events.activity_logs import (
    ActivityLogsAsk,
    ActivityLogsAskQuery,
    ActivityLogsChat,
    ActivityLogsChatQuery,
    DownloadActivityLogsAskQuery,
    DownloadActivityLogsChatQuery,
    QueryFiltersAsk,
    QueryFiltersChat,
)


def test_query_filters_chat_warns(recwarn: pytest.WarningsRecorder) -> None:
    _ = QueryFiltersChat()
    warnings_ = recwarn.list
    assert all(w.category is DeprecationWarning for w in warnings_), "Expected a DeprecationWarning"


def test_activity_logs_chat_warns(recwarn: pytest.WarningsRecorder) -> None:
    _ = ActivityLogsChat(year_month="2025-05", filters=QueryFiltersChat())
    warnings_ = recwarn.list
    assert len(warnings_) == 2  # one for ActivityLogsChat and the other for QueryFiltersChat
    assert all(w.category is DeprecationWarning for w in warnings_), "Expected a DeprecationWarning"


def test_activity_logs_chat_query_warns(recwarn: pytest.WarningsRecorder) -> None:
    _ = ActivityLogsChatQuery(year_month="2025-05", filters=QueryFiltersChat())
    warnings_ = recwarn.list
    assert len(warnings_) == 3  # ActivityLogsChatQuery, QueryFiltersChat and ActivityLogsChat
    assert all(w.category is DeprecationWarning for w in warnings_), "Expected a DeprecationWarning"


def test_activity_logs_chat_query_warns_2(recwarn: pytest.WarningsRecorder) -> None:
    _ = ActivityLogsChatQuery(year_month="2025-05", filters=QueryFiltersAsk())
    warnings_ = recwarn.list
    assert len(warnings_) == 2  # ActivityLogsChatQuery and ActivityLogsChat
    assert all(w.category is DeprecationWarning for w in warnings_), "Expected a DeprecationWarning"


def test_download_activity_logs_chat_warns(recwarn: pytest.WarningsRecorder) -> None:
    _ = DownloadActivityLogsChatQuery(year_month="2025-05", filters=QueryFiltersAsk())
    warnings_ = recwarn.list
    assert len(warnings_) == 2
    assert all(w.category is DeprecationWarning for w in warnings_), "Expected a DeprecationWarning"


def test_ask_does_not_warn(recwarn: pytest.WarningsRecorder) -> None:
    _ = QueryFiltersAsk(answer={})
    _ = DownloadActivityLogsAskQuery(year_month="2025-05", filters=QueryFiltersAsk())
    _ = ActivityLogsAsk(year_month="2025-05", filters=QueryFiltersAsk())
    _ = ActivityLogsAskQuery(year_month="2025-05", filters=QueryFiltersAsk())

    warnings_ = recwarn.list
    assert len(warnings_) == 0, "Expected no warnings"

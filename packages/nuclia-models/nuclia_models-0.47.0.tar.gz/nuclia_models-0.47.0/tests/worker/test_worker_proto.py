from nuclia_models.worker.proto import AskOperation


def test_ask_operation_alias() -> None:
    # Can be constructed using "json"
    op = AskOperation(question="q", destination="d", json=True)
    assert op.generate_json is True

    # Can be deserialized from "json"
    op = AskOperation.model_validate_json("""{"question": "q", "destination": "d", "json" : true}""")
    assert op.generate_json is True

    # Serializez to "json"
    op = AskOperation(question="q", destination="d")
    op.generate_json = True
    assert (
        op.model_dump_json()
        == """{"question":"q","destination":"d","json":true,"triggers":[],"user_prompt":""}"""
    )

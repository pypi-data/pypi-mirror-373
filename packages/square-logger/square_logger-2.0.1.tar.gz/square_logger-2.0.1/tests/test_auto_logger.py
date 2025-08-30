def test_auto_logger_redaction(caplog, log_folder):
    from square_logger import SquareLogger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
    )

    @global_object_square_logger.auto_logger(redacted_keys=["secret"])
    def do_something(value, secret=None):
        return {"value": value, "secret": secret}

    result = do_something("visible", secret="12345")
    log_output = "\n".join(caplog.messages)

    assert result["secret"] == "12345"
    assert "visible" in log_output
    assert "12345" not in log_output
    assert "**REDACTED**" in log_output


def test_auto_logger_redaction_variation2(caplog, log_folder):
    from square_logger import SquareLogger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
    )

    @global_object_square_logger.auto_logger(redacted_keys=["secret"])
    def do_something(value, secret=None):
        return {"value": value, "secret": secret}

    result = do_something("visible", "12345")
    log_output = "\n".join(caplog.messages)

    assert result["secret"] == "12345"
    assert "visible" in log_output
    assert "12345" not in log_output
    assert "**REDACTED**" in log_output


def test_auto_logger_with_disabled_redaction(caplog, log_folder):
    from square_logger import SquareLogger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
        pbool_enable_redaction=False,
    )

    @global_object_square_logger.auto_logger(redacted_keys=["secret"])
    def do_something(value, secret=None):
        return {"value": value, "secret": secret}

    result = do_something("visible", secret="12345")
    log_output = "\n".join(caplog.messages)

    assert result["secret"] == "12345"
    assert "visible" in log_output
    assert "12345" in log_output


def test_auto_logger_without_redaction(caplog, log_folder):
    from square_logger import SquareLogger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
    )

    @global_object_square_logger.auto_logger()
    def do_something(value, secret=None):
        return {"value": value, "secret": secret}

    result = do_something("visible", secret="12345")
    log_output = "\n".join(caplog.messages)

    assert result["secret"] == "12345"
    assert "visible" in log_output
    assert "12345" in log_output


def test_auto_logger_without_redaction_variation2(caplog, log_folder):
    from square_logger import SquareLogger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
        pbool_enable_redaction=False,
    )

    @global_object_square_logger.auto_logger()
    def do_something(value, secret=None):
        return {"value": value, "secret": secret}

    result = do_something("visible", secret="12345")
    log_output = "\n".join(caplog.messages)

    assert result["secret"] == "12345"
    assert "visible" in log_output
    assert "12345" in log_output


def test_auto_logger_with_pydantic_input(caplog, log_folder):
    from square_logger import SquareLogger
    from pydantic import BaseModel

    class InputModel(BaseModel):
        value: str
        secret: str

    global_object_square_logger = SquareLogger(
        pstr_log_file_name="log_testing",
        pint_log_level=10,
        pstr_log_path=log_folder,
    )

    @global_object_square_logger.auto_logger(redacted_keys=["secret"])
    def do_something(input_model: InputModel):
        return input_model

    result = do_something(InputModel(value="visible", secret="12345"))
    log_output = "\n".join(caplog.messages)

    assert result.secret == "12345"
    assert "visible" in log_output
    assert "12345" not in log_output
    assert "**REDACTED**" in log_output

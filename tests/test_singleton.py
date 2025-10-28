def test_singleton():
    from patterns.singleton import Config
    a, b = Config(), Config()
    assert a is b
    assert isinstance(a.get("log_level", "INFO"), str)

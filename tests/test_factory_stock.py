def test_factory_stock():
    from patterns.factory import InstrumentFactory
    inst = InstrumentFactory.create_instrument(
        {"type":"stock","symbol":"AAPL","name":"Apple","exchange":"NASDAQ"})
    assert inst.__class__.__name__ == "Stock"
    assert inst.symbol == "AAPL"
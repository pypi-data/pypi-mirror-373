from fast_depends import inject

from . import Extension, BaseConfig


async def test_transform():
    ext = Extension("test", module=__name__)

    @ext.transform(inputs=["inputs"], outputs=["outputs"])
    async def transformer(a: dict):
        return {"b": 1}

    assert ext.transformer_inputs == ["inputs"]
    assert ext.transformer_outputs == ["outputs"]

    assert ext.transformer

    result = await ext.transformer({"a": 1})

    assert result == {"b": 1}


async def test_extension_with_config():
    class TestConfig(BaseConfig):
        a: str

    ext = Extension("test", config_class=TestConfig, module=__name__)
    config = {"a": "value"}

    ext.configure(config)

    def test_function(cfg: ext.Config):  # type:ignore
        assert isinstance(cfg, TestConfig)
        assert cfg.a == "value"

    inject(test_function)()  # type:ignore


def test_extension_with_subscribe():
    ext = Extension("test", module=__name__)

    @ext.subscribe("test_key")
    async def subscriber(msg: dict):
        """Description"""
        pass

    assert len(ext.method_information) == 1

    info = ext.method_information[0]

    assert info.routing_key == "test_key"
    assert info.module == "cattle_grid.extensions.test_init"
    assert info.description == "Description"


def test_extension_with_subscribe_specify_description():
    ext = Extension("test", module=__name__)

    @ext.subscribe("test_key", description="other")
    async def subscriber(msg: dict):
        """Description"""
        pass

    assert len(ext.method_information) == 1

    info = ext.method_information[0]

    assert info.description == "other"


def test_extension_with_subscribe_incoming_outgoing():
    ext = Extension("test", module=__name__)

    @ext.subscribe("incoming.Create")
    async def subscriber(msg: dict):
        pass

    @ext.subscribe("outgoing.Create")
    async def outgoing_subscriber(msg: dict):
        pass

    assert len(ext.method_information) == 0


def test_extension_subscribe_wildcard_queues():
    ext = Extension("test", module=__name__)

    @ext.subscribe("incoming.*")
    async def start_subscriber(message: dict):
        pass

    @ext.subscribe("incoming.#")
    async def hash_subscriber(message: dict):
        pass

    @ext.subscribe_on_account_exchange("receive.*")
    async def account_subscriber(message: dict):
        pass

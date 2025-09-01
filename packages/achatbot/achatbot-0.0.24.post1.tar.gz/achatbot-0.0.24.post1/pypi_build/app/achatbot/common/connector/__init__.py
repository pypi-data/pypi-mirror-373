from achatbot.common.factory import EngineFactory
from achatbot.common import interface


class ConnectorInit:
    @staticmethod
    def getEngine(tag, **kwargs) -> interface.IConnector:
        if "redis_queue_connector" in tag:
            from . import redis_queue

        engine = EngineFactory.get_engine_by_tag(interface.IConnector, tag, **kwargs)
        return engine

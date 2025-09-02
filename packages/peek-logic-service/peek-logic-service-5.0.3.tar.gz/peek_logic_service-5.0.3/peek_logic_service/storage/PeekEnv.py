import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_logic_service.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class PeekEnvServer(DeclarativeBase, Tuple):
    """PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """

    __tupleType__ = "peek_logic_service.env.server"
    __tablename__ = "PeekEnvServer"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    workers = relationship("PeekEnvWorker")
    agent = relationship("PeekEnvAgent")

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


@addTupleType
class PeekEnvWorker(DeclarativeBase, Tuple):
    """PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """

    __tupleType__ = "peek_logic_service.env.worker"
    __tablename__ = "PeekEnvWorker"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(
        ForeignKey("peek_logic_service.PeekEnvServer.id"), primary_key=True
    )
    server = relationship("PeekEnvServer")

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


@addTupleType
class PeekEnvAgent(DeclarativeBase, Tuple):
    """PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """

    __tupleType__ = "peek_logic_service.env.agent"
    __tablename__ = "PeekEnvAgent"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(
        ForeignKey("peek_logic_service.PeekEnvServer.id"), primary_key=True
    )
    server = relationship("PeekEnvServer")

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


@addTupleType
class PeekEnvClient(DeclarativeBase, Tuple):
    """PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """

    __tupleType__ = "peek_logic_service.env.client"
    __tablename__ = "PeekEnvClient"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(
        ForeignKey("peek_logic_service.PeekEnvServer.id"), primary_key=True
    )
    server = relationship("PeekEnvServer")

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

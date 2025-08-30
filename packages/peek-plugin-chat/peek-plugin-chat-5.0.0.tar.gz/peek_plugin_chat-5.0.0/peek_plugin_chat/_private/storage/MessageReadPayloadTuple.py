from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from .ChatUserTuple import ChatUserTuple
from .DeclarativeBase import DeclarativeBase
from .MessageTuple import MessageTuple


@addTupleType
class MessageReadPayloadTuple(DeclarativeBase, Tuple):
    __tupleType__ = chatTuplePrefix + "MessageReadPayloadTuple"
    __tablename__ = "MessageReadPayloadTuple"

    id = Column(Integer, primary_key=True, autoincrement=True)

    #: Foreign key to a Message
    messageId = Column(
        Integer, ForeignKey(MessageTuple.id, ondelete="CASCADE"), nullable=False
    )
    message = relationship(MessageTuple)

    #: Foreign key to a ChatUser
    chatUserId = Column(
        Integer, ForeignKey(ChatUserTuple.id, ondelete="CASCADE"), nullable=True
    )
    chatUser = relationship(ChatUserTuple)

    onReadPayload = Column(LargeBinary, nullable=False)

    __table_args__ = (
        Index("idx_ChatPayloads", messageId, chatUserId, unique=False),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

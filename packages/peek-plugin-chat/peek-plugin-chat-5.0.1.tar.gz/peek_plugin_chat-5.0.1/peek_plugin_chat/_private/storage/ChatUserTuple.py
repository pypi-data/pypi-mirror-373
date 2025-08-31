from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import DateTime
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from peek_plugin_chat._private.storage.ChatTuple import ChatTuple
from peek_plugin_chat._private.storage.DeclarativeBase import DeclarativeBase


@addTupleType
class ChatUserTuple(DeclarativeBase, Tuple):
    __tupleType__ = chatTuplePrefix + "ChatUserTuple"
    __tablename__ = "ChatUserTuple"

    id = Column(Integer, primary_key=True, autoincrement=True)

    #: Foreign key to a chat
    chatId = Column(
        Integer, ForeignKey(ChatTuple.id, ondelete="CASCADE"), nullable=False
    )
    chat = relationship(ChatTuple, overlaps="users")

    #: The userId of a user in the chat
    userId = Column(String(2000), nullable=False)
    isUserExternal = Column(Boolean, nullable=False)

    #: Last Read Date
    lastReadDate = Column(DateTime(True), nullable=False)
    # If ChatUserTuple.lastReadDate < ChatTuple.lastActivity then we have unread
    # messages.

    # #:  User Name, to be populated before sending to the UI
    # userName = TupleField(defaultValue="Unknown")

    __table_args__ = (
        Index("idx_ChatUser_userId", userId, unique=False),
        Index("idx_ChatUser_chatId", chatId, unique=False),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

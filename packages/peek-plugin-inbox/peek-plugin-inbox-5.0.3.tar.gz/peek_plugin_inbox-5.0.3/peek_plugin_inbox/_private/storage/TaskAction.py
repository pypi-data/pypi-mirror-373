""" 
 *  Copyright Synerty Pty Ltd 2016
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from peek_plugin_inbox._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class TaskAction(DeclarativeBase, Tuple):
    """Task Action

    This table stores the Task Actions.
    Tasks have zero or more actions that can be performed by the user when they
    receive a task.

    :member title: The title of the action, this will appear as a menu option.
    :member confirmMessage: This is the message that will be shown to confirm the action.
    :member actionedPayload: This payload will be delivered locally on Peek Server
        When the action is performed on the user device.

    """

    __tupleType__ = inboxTuplePrefix + "TaskAction"
    __tablename__ = "TaskAction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    taskId = Column(
        Integer, ForeignKey("Task.id", ondelete="CASCADE"), nullable=False
    )
    task = relationship("Task", uselist=False, overlaps="actions")

    title = Column(String)
    confirmMessage = Column(String)
    onActionPayloadEnvelope = Column(PeekLargeBinary)

    __table_args__ = (Index("idx_TaskAction_taskId", taskId, unique=False),)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

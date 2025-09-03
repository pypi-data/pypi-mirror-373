from dataclasses import dataclass
from unittest.mock import Mock


from pubtools.sign.clients.msg_recv_client import _RecvClient
from pubtools.sign.clients.msg import _MsgClient
from pubtools.sign.models.msg import MsgError


def test_msg_handler_errors():
    mock_error = Mock()

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_link_error(mock_error)
    assert errors == [
        MsgError(
            name=mock_error.link.condition.name,
            description=mock_error.link.condition.description,
            source=mock_error.link,
        )
    ]

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_session_error(mock_error)
    assert errors == [
        MsgError(
            name=mock_error.session.condition.name,
            description=mock_error.session.condition.description,
            source=mock_error.session,
        )
    ]

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_connection_error(mock_error)
    assert errors == [
        MsgError(
            name=mock_error.connection.condition.name,
            description=mock_error.connection.condition.description,
            source=mock_error.connection,
        )
    ]


@dataclass
class FakeCondition:
    """Fake error description."""

    name: str
    description: str


def test_ingore_error():
    mock_error = Mock(
        transport=Mock(
            condition=FakeCondition(
                name="amqp:connection:framing-error", description="SSL Failure: Unknown error"
            )
        )
    )
    errors = []
    msgsc = _RecvClient(
        uid="1",
        topic="topic",
        message_ids=["1"],
        id_key="id",
        broker_urls=[""],
        cert="",
        ca_cert="",
        timeout=0,
        recv={},
        errors=errors,
    )
    msgsc.on_transport_error(mock_error)
    assert errors == []


def test_error_no_description():
    mock_error = Mock(transport=Mock(condition=None, remote_condition=None))
    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_transport_error(mock_error)
    assert errors == []

from unittest.mock import patch

from django.dispatch import Signal

from wbcore.utils.signals import DisconnectSignals, SignalWrapper

test_signal1 = Signal()
test_signal2 = Signal()


def receiver_dummy1(sender, **kwargs):
    pass


def receiver_dummy2(sender, **kwargs):
    pass


def test_disconnect_signals():
    with (
        patch("wbcore.tests.test_utils.test_signals.receiver_dummy1") as mock_receiver_dummy1,
        patch("wbcore.tests.test_utils.test_signals.receiver_dummy2") as mock_receiver_dummy2,
    ):
        test_signal1.connect(receiver_dummy1, "suppressed_sender")
        test_signal1.connect(receiver_dummy1, "working_sender")
        test_signal2.connect(receiver_dummy2, "another_suppressed_sender")

        with DisconnectSignals(
            [
                SignalWrapper(test_signal1, receiver_dummy1, "suppressed_sender"),
                SignalWrapper(test_signal2, receiver_dummy2, "another_suppressed_sender"),
            ]
        ):
            test_signal1.send(sender="suppressed_sender")
            test_signal1.send(sender="working_sender")
            test_signal2.send(sender="another_suppressed_sender")

        assert mock_receiver_dummy1.call_count == 1
        assert mock_receiver_dummy1.call_args.kwargs["sender"] == "working_sender"
        assert not mock_receiver_dummy2.called

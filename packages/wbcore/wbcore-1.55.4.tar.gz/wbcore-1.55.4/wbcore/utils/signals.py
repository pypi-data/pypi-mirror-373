from typing import Callable

from django.db.models.signals import ModelSignal


class SignalWrapper:
    """A convenience class that encapsulates a signal in order to
    be used in the DisconnectedSignals context manager
    """

    def __init__(self, signal: ModelSignal, receiver: Callable, sender, dispatch_uid: str | None = None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def connect(self):
        self.signal.connect(receiver=self.receiver, sender=self.sender, weak=False, dispatch_uid=self.dispatch_uid)

    def disconnect(self):
        self.signal.disconnect(receiver=self.receiver, sender=self.sender, dispatch_uid=self.dispatch_uid)


class DisconnectSignals:
    """A Context-Manager to temporarily disable a set of signals"""

    def __init__(self, signals: list[SignalWrapper]):
        self.signals = signals

    def __enter__(self):
        for signal in self.signals:
            signal.disconnect()

    def __exit__(self, type, value, traceback):
        for signal in self.signals:
            signal.connect()

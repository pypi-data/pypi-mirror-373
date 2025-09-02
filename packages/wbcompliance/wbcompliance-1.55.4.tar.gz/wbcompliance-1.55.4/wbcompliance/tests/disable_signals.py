from collections import defaultdict

from django.db.models.signals import *


class DisableSignals(object):
    def __init__(self, disabled_signals=None):
        self.stashed_signals = defaultdict(list)
        self.disabled_signals = disabled_signals or [
            pre_init,
            post_init,
            pre_save,
            post_save,
            pre_delete,
            post_delete,
            pre_migrate,
            post_migrate,
        ]

    def __enter__(self):
        for signal in self.disabled_signals:
            self.disconnect(signal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for signal in list(self.stashed_signals):
            self.reconnect(signal)

    def disconnect(self, signal):
        self.stashed_signals[signal] = signal.receivers
        signal.receivers = []

    def reconnect(self, signal):
        signal.receivers = self.stashed_signals.get(signal, [])
        del self.stashed_signals[signal]


# https://stackoverflow.com/questions/55578230/django-how-to-visualize-signals-and-save-overrides
# RECEIVER_MODELS = re.compile(r"sender=(\w+)\W")


# class DisableSignalsNotification_OLD_VERSION(DisableSignals):
#     def __enter__(self):
#         for signal in self.disabled_signals:
#             if not isinstance(signal, ModelSignal):
#                 continue
#             for _, receiver in signal.receivers:
#                 rcode = inspect.getsource(receiver())
#                 rmodel = RECEIVER_MODELS.findall(rcode)
#                 if "Notification" in rmodel:
#                     self.disconnect(signal)


class temp_disconnect_signal:
    """Temporarily disconnect a model from a signal"""

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )


class DisableSignalsNotification(temp_disconnect_signal):
    def __init__(self, dispatch_uid=None):
        self.signal = post_save
        self.receiver = post_create_notification
        self.sender = Notification
        self.dispatch_uid = dispatch_uid

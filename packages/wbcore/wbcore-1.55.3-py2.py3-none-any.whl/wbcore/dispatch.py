from django.apps import apps

from wbcore.utils.itertools import get_inheriting_subclasses


def receiver_all_subclasses(signal, sender, *args, **kwargs):
    def _decorator(func):
        signal.connect(func, *args, sender=sender, dispatch_uid=func.__name__ + "_" + sender.__name__, **kwargs)
        for subclass in sender.__subclasses__():
            signal.connect(
                func, *args, sender=subclass, dispatch_uid=func.__name__ + "_" + subclass.__name__, **kwargs
            )

        return func

    return _decorator


def receiver_subclasses(signal, sender, *args, only_leaf=True, **kwargs):
    """
    A decorator for connecting receivers and all receiver's subclasses to signals. Used by passing in the
    signal and keyword arguments to connect::
    The signal needs to be registered after all child models are registered (e.g. by placing the signal in a dedicated
    signal file)
        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...
    """

    def _decorator(func):
        if isinstance(sender, str):
            sender_class = apps.get_model(sender)
        else:
            sender_class = sender
        for snd in get_inheriting_subclasses(sender_class, only_leaf=only_leaf):
            signal.connect(func, *args, sender=snd, dispatch_uid=func.__name__ + "_" + snd.__name__, **kwargs)
        return func

    return _decorator


def receiver_inherited_through_models(signal, sender, through_field_name, **kwargs):
    """
    A decorator for connecting receivers and all subclasses's through model'.
    """

    def _decorator(func):
        for sub_class in sender.__subclasses__():
            if (through_field := getattr(sub_class, through_field_name, None)) and (
                through_class := getattr(through_field, "through", None)
            ):
                signal.connect(
                    func, sender=through_class, dispatch_uid=func.__name__ + "_" + through_class.__name__, **kwargs
                )

    return _decorator

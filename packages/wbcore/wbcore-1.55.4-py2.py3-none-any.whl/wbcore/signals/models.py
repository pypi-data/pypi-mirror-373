from django.db.models.signals import ModelSignal

get_dependant_dynamic_fields_instances = ModelSignal()  # Signal use to gather the dependant fields to be computed before the sender (use for the dynamic field framework). Experimental state
pre_collection = ModelSignal()  # pre_delete signal is sent after collection. Therefore, protect field will trigger an IntergrityError. This signal can be used to circuvent that.

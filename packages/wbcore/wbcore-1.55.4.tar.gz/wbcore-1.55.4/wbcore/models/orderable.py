from ordered_model.models import OrderedModel as BaseOrderedModel


class OrderableModel(BaseOrderedModel):
    class Meta(BaseOrderedModel.Meta):
        abstract = True

def register(section=None, weight=0):
    """
    Register the given serializer and the associated section to the shares site
    """
    from wbcore.shares.sites import share_site

    def _serializer_wrapper(serializer_class):
        share_site.serializers.append(serializer_class)
        if section:
            share_site.sections.append({"section": section, "weight": weight})
        return serializer_class

    return _serializer_wrapper

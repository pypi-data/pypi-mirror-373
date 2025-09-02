from .menus import Menu, MenuItem


class MenuRegistry:
    def __init__(self):
        self._registry = list()

    def clear(self):
        self._registry = list()

    def register(self, menu: Menu | MenuItem):
        self._registry.append(menu)

    def __iter__(self):
        request = getattr(self, "request", None)
        if getattr(self, "alphabetical_sorted", False):
            menus = sorted(filter(lambda x: bool(x), self._registry), key=lambda x: x.label)
        else:
            menus = sorted(filter(lambda x: bool(x), self._registry), key=lambda x: (x.index is None, x.index))

        for menu in menus:
            menu.request = request
            serialized_menu = dict(menu)
            if serialized_menu != {}:
                yield serialized_menu


default_registry = MenuRegistry()

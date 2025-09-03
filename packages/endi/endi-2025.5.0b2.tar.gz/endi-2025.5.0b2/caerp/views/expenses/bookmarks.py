from caerp.models.services.user import UserPrefsService


class BookMarkHandler:
    """
    Wrapper for expense bookmarks
    """

    def __init__(self, request):
        self.request = request
        self.bookmarks = {}
        self.load_bookmarks_from_current_request()

    def load_bookmarks_from_current_request(self):
        expense_dict = UserPrefsService.get(self.request, "expense")
        self.bookmarks = expense_dict["bookmarks"]
        return self.bookmarks

    def refresh(self):
        self.load_bookmarks_from_current_request()

    def store(self, item):
        """
        Store a bookmark (add/edit)
        :@param item: a dictionnary with the bookmark informations
        """
        id_ = item.get("id")
        if not id_:
            id_ = self._next_id()
            item["id"] = id_

        self.bookmarks[id_] = item
        self._save()
        return item

    def delete(self, id_):
        """
        Removes a bookmark
        """
        item = self.bookmarks.pop(id_, None)
        if item is not None:
            self._save()
        return item

    def _next_id(self):
        """
        Return the next available bookmark id
        """
        id_ = 1
        if list(self.bookmarks.keys()):
            all_keys = [int(key) for key in list(self.bookmarks.keys())]
            id_ = max(all_keys) + 1
        return id_

    def _save(self):
        """
        Persist the bookmarks in the database
        """
        expense_dict = UserPrefsService.get(self.request, "expense")
        expense_dict["bookmarks"] = self.bookmarks
        UserPrefsService.set(self.request, "expense", expense_dict)


def get_bookmarks(request):
    """
    Return the user's bookmarks
    """
    return list(BookMarkHandler(request).bookmarks.values())

from rest_framework import routers


class APIRootView(routers.APIRootView):
    """
    Service list.
    """


class APIRouter(routers.DefaultRouter):
    APIRootView = APIRootView

    def __init__(self, root_view_name):
        super().__init__(trailing_slash=False)
        self.root_view_name = root_view_name

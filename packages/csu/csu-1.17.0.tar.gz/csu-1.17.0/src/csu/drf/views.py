from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.views import APIView


class AsyncAPIView(APIView):
    async def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            await self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = await handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    async def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        await self.perform_authentication(request)
        self.check_permissions(request)
        self.check_throttles(request)

    async def perform_authentication(self, request: Request):
        for authenticator in request.authenticators:
            try:
                if hasattr(authenticator, "aauthenticate"):
                    user_auth_tuple = await authenticator.aauthenticate(request)
                else:
                    raise TypeError(f"Async-incompatible authenticator: {authenticator}")
            except APIException:
                request._authenticator = request.user = request.auth = None
                raise

            if user_auth_tuple is not None:
                request._authenticator = authenticator
                request.user, request.auth = user_auth_tuple

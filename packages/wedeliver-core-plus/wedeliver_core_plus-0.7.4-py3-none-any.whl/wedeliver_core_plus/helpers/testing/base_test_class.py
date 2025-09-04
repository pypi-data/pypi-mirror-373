import pytest


class BaseTestClass:
    """
    Base class for reusable test functionality.
    """

    module_path = None
    route_function_name = None

    @pytest.fixture(autouse=True)
    def base_setup(
            self,
            api_request,
            db_session,
            model_factory,
            web_auth_token,
            web_supplier_token,
            app_auth_token,
            app_auth_pre_token,
            auto_patch_microfetcher,
            request,
    ):
        # Inject common fixtures
        self.api_request = api_request
        self.db_session = db_session
        self.model_factory = model_factory
        self.web_auth_token = web_auth_token
        self.web_supplier_token = web_supplier_token
        self.app_auth_token = app_auth_token
        self.app_auth_pre_token = app_auth_pre_token
        self.auto_patch_microfetcher = auto_patch_microfetcher

        # Allow derived classes to add additional fixtures
        self._custom_setup(request)

    def _custom_setup(self, request):
        """
        Method for derived classes to extend the setup process.
        """
        pass

    def patch_microfetcher(self, mock_microfetcher=None, module=None, **kwargs):
        """
        Patches the microfetcher with a given route and data. Automatically sets manual flag if the route differs from
        the default route_function_name.

        :param module: The route to patch. Defaults to self.route_function_name.
        :param mock_microfetcher: The MockMicroFetcher instance to use for patching.
        :param kwargs: Any additional keyword arguments to pass.
        """
        # Default to the class-level route_function_name if no route is provided
        if module is None:
            module = self.route_function_name

        # Automatically add manual flag if the route is different from the default
        if module != self.route_function_name:
            kwargs['manual'] = True

        # Call the actual microfetcher patching function
        self.auto_patch_microfetcher(module, mock_microfetcher, **kwargs)

    def call_api_request(self, **kwargs):

        return self.api_request(self.route_function_name, **kwargs)

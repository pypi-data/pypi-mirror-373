from datetime import datetime, timedelta

import jwt
import pytest
import sqlalchemy

from app import app as flask_app
from app import db
import os
from wedeliver_core_plus import route_metadata, MockMicroFetcher, Role
from unittest.mock import patch
import re
from wedeliver_core_plus.helpers.enums import App


@pytest.fixture(scope='session')
def test_app():
    flask_app.config.update(
        {
            "TESTING": False,
            "DEBUG": False,
            "SQLALCHEMY_ECHO": False,
            "SQLALCHEMY_BINDS": None,
            "SQLALCHEMY_DATABASE_URI": "{engine}://{username}:{password}@{server}:{port}/{database}?charset=utf8".format(
                engine=os.environ.get("DATABASE_ENGINE", "mysql"),
                username=os.environ.get("DATABASE_USERNAME", "root"),
                password=os.environ.get("DATABASE_PASSWORD", "root"),
                server=os.environ.get("DATABASE_SERVER", "0.0.0.0"),
                database=os.environ.get("DATABASE_NAME", "test_db"),
                port=os.environ.get("DATABASE_PORT", 3306),
            ),
        }
    )
    with flask_app.app_context():
        # with flask_app.app_context(): ensures that all commands within this block are run in the Flask app context.
        db.create_all()
        # yield keyword returns a list of values but doesn't stop the execution of the function
        yield flask_app

        db.session.remove()
        # pytest.helpers.reset()
        db.drop_all()


@pytest.fixture()
def client(test_app):
    yield test_app.test_client()


# @pytest.fixture
# def db_session(test_app):
#     with test_app.app_context():
#         # Start a database transaction
#         connection = db.engine.connect()
#         transaction = connection.begin()
#         options = dict(bind=connection, binds={})
#         # Create a scoped session bound to the connection
#         session = db.create_scoped_session(options=options)
#
#         # Override the default db.session with our test session
#         prev_session = db.session  # Save the previous session
#         db.session = session
#
#         yield session
#
#         # Cleanup: Restore the original db.session
#         db.session = prev_session
#         session.remove()
#         transaction.rollback()
#         connection.close()


@pytest.fixture(scope='function')
def db_session(test_app):
    """
    Fixture to provide a database session with automatic transaction rollback.
    This will ensure all changes made during each test are rolled back,
    effectively deleting any rows inserted during the test.
    """
    with test_app.app_context():
        # Start a new transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind a new session to the transaction connection
        options = {"bind": connection, "binds": {}}
        session = db.create_scoped_session(options=options)
        db.session = session

        yield session

        # Rollback the transaction to clean up inserted rows
        transaction.rollback()
        connection.close()

        # Remove session to clean up
        session.remove()


@pytest.fixture
def model_factory(db_session):
    """Generic factory fixture for creating models."""
    created_models = []

    def _create_model(create_func, **kwargs):
        model_instance = create_func(db_session, **kwargs)
        created_models.append(model_instance)
        return model_instance

    yield _create_model

    # Cleanup: Ensure models are deleted if not automatically cleaned up by rollback
    try:
        for model_instance in created_models:
            db_session.delete(model_instance)
        if created_models:
            db_session.commit()
    except Exception as e:
        pass
        # db_session.rollback()
        # pytest.fail(f"Unexpected error during cleanup: {e}")



# @pytest.fixture
# def model_factory(db_session):
#     def _create_model(create_func, **kwargs):
#         return create_func(db_session, **kwargs)
#     return _create_model


@pytest.fixture
def mock_micro_fetcher():
    # Define or import your MockMicroFetcher class or instance here
    # This should be the same as used in your other tests
    return MockMicroFetcher()


@pytest.fixture
def api_client(client, mock_micro_fetcher):
    class APIClient:
        def __init__(self, client):
            self.client = client
            self.default_headers = {}
            self.auth_token = None

        def set_headers(self, headers):
            self.default_headers.update(headers)

        def get(self, url, headers=None, **kwargs):
            return self._do_request(
                self.client.get,
                url,
                headers=headers,
                **kwargs
            )

        def post(self, url, json=None, data=None, headers=None, **kwargs):
            return self._do_request(
                self.client.post,
                url,
                json=json,
                data=data,
                headers=headers,
                **kwargs
            )

        def put(self, url, json=None, data=None, headers=None, **kwargs):
            return self._do_request(
                self.client.put,
                url,
                json=json,
                data=data,
                headers=headers,
                **kwargs
            )

        def delete(self, url, headers=None, **kwargs):
            return self._do_request(
                self.client.delete,
                url,
                headers=headers,
                **kwargs
            )

        def _merge_headers(self, headers):
            merged = self.default_headers.copy()
            if headers:
                merged.update(headers)
            return merged

        def _do_request(self, method, url, headers=None, **kwargs):
            merged_headers = self._merge_headers(headers)
            response = method(
                url,
                headers=merged_headers,
                **kwargs
            )
            return response

    return APIClient(client)


@pytest.fixture
def web_auth_token(test_app):
    def get_token(role=Role.SYSTEM_ADMIN, language='ar'):
        # Default token data for system admin
        token_data = dict(
            account_id=1,
            app=App.WEB_APP.value,
            email='administrator@wedeliverapp.com',
            role=role,
            is_logged=True,
            language=language,
            exp=int(datetime.timestamp(datetime.now() + timedelta(hours=12))),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Encode the token
        token = jwt.encode(token_data, test_app.config.get("SECRET_KEY"), algorithm="HS256")

        plain_data = dict(
            email=token_data.get('email'),
            role=token_data.get("role"),
            language=language,
        )

        return dict(
            message="Logged successfully",
            data=plain_data,
            token=token.decode("utf-8") if isinstance(token, bytes) else token,
        )

    return get_token


@pytest.fixture
def web_supplier_token(test_app):
    def get_token(role=Role.CRM_USER, language='ar'):
        # Default token data for system supplier

        token_data = dict(
            account_id=1,
            app=App.WEB_APP.value,
            email='supplier@example.com',
            role=role,
            language=language,
            is_logged=True,
            exp=int(datetime.timestamp(datetime.now() + timedelta(hours=12))),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            supplier_id=1
        )
        token = jwt.encode(token_data, test_app.config.get("SECRET_KEY"), algorithm="HS256")


        plain_data = dict(
            email=token_data.get("email"),
            role=token_data.get("role"),
            supplier="Test Supplier",
        )

        return dict(
            message="Logged successfully",
            data=plain_data,
            token=token.decode("utf-8") if isinstance(token, bytes) else token,
        )

    return get_token


@pytest.fixture
def app_auth_token(test_app):
    def get_token(role=Role.APP_USER, customer_id=1, account_id=2, device_id=1, language='ar', currency='SAR',
                  country_code='sa', nick_name='Test Nickname', image="",mobile= "966500000001",app_version="1.0.0",platform="android"):
        customer = dict(
            id=customer_id,
            nick_name=nick_name,
            image=image
        )
        token_data = dict(
            account_id=account_id,
            device_id=device_id,
            language=language,
            app=App.CUSTOMER_APP.value,
            role=role,
            customer=dict(**customer, full_name=customer.get("nick_name")),
            is_logged=True,
            exp=int(datetime.timestamp(datetime.now() + timedelta(days=365))),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mobile=mobile,
            app_version=app_version,
            platform=platform,
        )
        token = jwt.encode(token_data, test_app.config.get("SECRET_KEY"), algorithm="HS256")

        plain_data = dict(
            required_pin=False,
            language=token_data.get('language'),
            country_code=country_code,
            currency=currency,
            full_name=customer.get("nick_name"),
            customer_image=customer["image"],
            app_version_obj='0.0.0',
        )
        plain_data.update(**customer)

        # update_customer_last_login(account.id)
        return dict(
            message="Logged successfully",
            data=plain_data,
            token=token.decode("utf-8") if isinstance(token, bytes) else token,
        )

    return get_token


@pytest.fixture
def app_auth_pre_token(test_app):
    def get_token(role=Role.APP_USER, account_id=1):
        token_data = dict(
            account_id=account_id,
            app=App.CUSTOMER_APP.value,
            role=role,
            is_logged=False,
            exp=int(datetime.timestamp(datetime.now() + timedelta(days=365))),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        token = jwt.encode(token_data, test_app.config.get("SECRET_KEY"), algorithm="HS256")

        db.session.commit()

        return dict(
            message="You have activated your account successfully",
            data=dict(required_pin=True),  # Require a (new PIN) or not
            token=token.decode("utf-8") if isinstance(token, bytes) else token,
        )

    return get_token


@pytest.fixture
def get_api_url():
    def _get_url(route_function_name):
        route_info = route_metadata.get(route_function_name)
        if not route_info:
            raise ValueError(f"No metadata found for route '{route_function_name}'")
        return route_info['url']

    return _get_url


@pytest.fixture
def auto_patch_microfetcher():
    patches = []

    def _patch(route_function_name, mock_micro_fetcher, manual=False):
        if manual:
            module_path = route_function_name
        else:
            route_info = route_metadata.get(route_function_name)
            if not route_info:
                raise ValueError(f"No metadata found for route '{route_function_name}'")

            if not route_info.get('is_testable'):
                raise ValueError(f"Route '{route_function_name}' is not testable")

            module_path = route_info.get('module_path')
            if not module_path:
                raise ValueError(f"No module path specified for route '{route_function_name}'")

        # Build the full module path to patch
        full_module_path = f"{module_path}.MicroFetcher"

        try:
            # Apply the patch
            patcher = patch(full_module_path, new=mock_micro_fetcher)
            patched = patcher.start()
            patches.append(patcher)
            return patched
        except (ModuleNotFoundError, AttributeError, ImportError) as e:
            # Module or MicroFetcher not found, skip patching
            # Optionally, log a warning message
            print(f"Warning: Could not patch MicroFetcher at '{full_module_path}'. Skipping patch.")
            print(f"Reason: {e}")
            return None

    yield _patch

    # Cleanup patches after tests
    for patcher in patches:
        patcher.stop()


@pytest.fixture
def get_route_metadata():
    return route_metadata


def substitute_url_placeholders(url, url_params):
    """
    Replaces placeholders in the URL with actual values from url_params.

    Placeholders are in the format: <converter:variable_name>
    Example: /path/<int:id> => /path/123

    Parameters:
    - url: The URL string with placeholders.
    - url_params: A dictionary of variable_name: value.

    Returns:
    - The URL with placeholders replaced by actual values.
    """

    def replace_match(match):
        # Extract variable name from the placeholder
        placeholder = match.group(0)  # e.g., '<int:withdraw_request_id>'
        # Split the placeholder to get the variable name
        parts = placeholder.strip('<>').split(':')
        if len(parts) == 2:
            variable_name = parts[1]
        else:
            variable_name = parts[0]
        # Get the actual value from url_params
        if variable_name in url_params:
            return str(url_params[variable_name])
        else:
            raise ValueError(f"URL parameter '{variable_name}' not provided in url_params")

    # Replace all placeholders in the URL
    return re.sub(r'<[^>]+>', replace_match, url)


@pytest.fixture
def api_request(api_client):
    def _api_request(route_function_name, url_params=None, method=None, **kwargs):
        """
        Makes an API request using the appropriate HTTP method based on route metadata.

        Parameters:
        - route_function_name: Name of the route function (string).
        - url_params: Dictionary of URL parameters to replace placeholders.
        - method: Optional HTTP method to use.
        - kwargs: Additional arguments for the API call, such as query_string, data, json, headers, etc.

        Returns:
        - response: The response object from the API call.
        """
        # Retrieve the route metadata
        route_info = route_metadata.get(route_function_name)
        if not route_info:
            raise ValueError(f"No metadata found for route '{route_function_name}'")

        # Get the API URL
        api_url = route_info.get('url')
        if not api_url:
            raise ValueError(f"No URL specified for route '{route_function_name}'")

        # Replace URL placeholders with actual values
        url_params = url_params or {}
        try:
            api_url = substitute_url_placeholders(api_url, url_params)
        except ValueError as e:
            raise ValueError(f"Error substituting URL placeholders: {e}")

        # Get the HTTP methods
        methods = route_info.get('methods', [])
        if not methods:
            raise ValueError(f"No HTTP methods specified for route '{route_function_name}'")

        # Choose the HTTP method to use
        if method:
            # Use the specified method
            http_method = method.lower()
            if http_method.upper() not in methods:
                raise ValueError(f"Specified method '{method.upper()}' not supported for route '{route_function_name}'")
        else:
            # Default to the first method in the list
            http_method = methods[0].lower()

        # Ensure the api_client has the method
        if not hasattr(api_client, http_method):
            raise AttributeError(f"api_client does not support method '{http_method}'")

        # Get the method from api_client
        api_client_method = getattr(api_client, http_method)

        # Make the API call
        response = api_client_method(api_url, **kwargs)

        return response

    return _api_request

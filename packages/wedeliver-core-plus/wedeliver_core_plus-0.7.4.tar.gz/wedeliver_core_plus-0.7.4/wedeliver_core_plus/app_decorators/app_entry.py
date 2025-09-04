from datetime import datetime
from functools import wraps
from marshmallow import post_dump, pre_dump
from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.app_decorators import (
    handle_response,
    handle_auth,
    handle_exceptions,
    serializer,
)
from wedeliver_core_plus.helpers.time import DATETIME_FORMAT_SCHEMA

# from wedeliver_core_plus.helpers.get_prefix import get_prefix

# Dictionary to store route metadata
route_metadata = {}


def route(path, methods=["GET"], schema=None, many=False, allowed_roles=None, require_auth=True,
          append_auth_args=None,
          pre_login=False,
          deprecated=False,
          allowed_permissions=None, guards=[]):
    app = WedeliverCorePlus.get_app()

    def factory(func):
        # Store metadata
        route_metadata[func.__name__] = {
            'module_path': getattr(func, 'testing_class_module', None),
            'url': path,
            'methods': methods,
            'schema': schema,
            'allowed_roles': allowed_roles,
            'is_testable': getattr(func, 'is_testable', False),
        }

        @app.route(path, methods=methods)
        @handle_response
        @handle_exceptions
        @handle_auth(require_auth=require_auth, append_auth_args=append_auth_args, allowed_roles=allowed_roles,
                     allowed_permissions=allowed_permissions, pre_login=pre_login, guards=guards, deprecated=deprecated)
        @serializer(schema=schema, many=many)
        @wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)

        return decorator

    return factory


def testing_class(test_cls):
    def decorator(func):
        func.testing_class_module = getattr(test_cls, 'module_path', None)
        func.is_testable = True
        # Set the route function name on the test class
        setattr(test_cls, 'route_function_name', func.__name__)
        return func
    return decorator


def advance(features_class):
    def decorator(cls):
        original_cls = cls  # Save a reference to the original class

        # class_name = f"AutoAdvanced_{cls.__name__}"

        # Dynamically create the new class
        # AutoAdvancedClass = type(class_name, (cls, features_class), {})

        # Alternatively, you can use a regular class definition, if you prefer:
        # class AutoAdvancedClass(cls, features_class):
        #     pass

        class AutoAdvancedClass(cls, features_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def before_insert(self, mapper, connection):
                # Check if features_class has the method before_insert
                if hasattr(features_class, 'before_insert'):
                    features_class.before_insert(self, mapper, connection)

            def after_insert(self, mapper, connection):
                # Check if features_class has the method before_insert
                if hasattr(features_class, 'after_insert'):
                    features_class.after_insert(self, mapper, connection)

            def before_update(self, mapper, connection):
                if hasattr(features_class, 'before_update'):
                    features_class.before_update(self, mapper, connection)

            def after_update(self, mapper, connection):
                if hasattr(features_class, 'after_update'):
                    features_class.after_update(self, mapper, connection)

            def before_delete(self, mapper, connection):
                if hasattr(features_class, 'before_delete'):
                    features_class.before_delete(self, mapper, connection)

            def after_delete(self, mapper, connection):
                if hasattr(features_class, 'after_delete'):
                    features_class.after_delete(self, mapper, connection)

        # Pass the original class to restfull
        return restfull(original_cls, AutoAdvancedClass)

    return decorator


def restfull(original_cls, advanced_model_class):
    # from flask import current_app

    model_name = original_cls.__name__.lower()
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    ma = app.extensions['flask-marshmallow']

    module_path = original_cls.__module__

    # Split the string by the dot character
    parts = module_path.split('.')

    # Extract the third part of the module path
    service_name = f'/{parts[2]}' if len(parts) > 2 else None

    single_name = model_name if not hasattr(advanced_model_class,
                                            '__restfull__') else advanced_model_class.__restfull__.get('model_name',
                                                                                                       model_name)
    plural_name = f'{model_name}s' if not hasattr(advanced_model_class,
                                                  '__restfull__') else advanced_model_class.__restfull__.get(
        'models_name', f'{model_name}s')

    api_prefix = '/api/v1' if not hasattr(advanced_model_class,
                                          '__restfull__') else advanced_model_class.__restfull__.get('url_prefix',
                                                                                                     '/api/v1')

    api_prefix = f'{service_name}{api_prefix}' if service_name else api_prefix

    def generate_dynamic_schema(method):
        required_fields = [] if not hasattr(original_cls, '__restfull__') else original_cls.__restfull__.get('methods',
                                                                                                             {}).get(
            method, {}).get('required_fields', [])

        hidden_fields = [] if not hasattr(original_cls, '__restfull__') else original_cls.__restfull__.get(
            'hidden_fields', [])

        class ModelSchema(ma.SQLAlchemyAutoSchema):
            class Meta:
                # model = original_cls
                table = original_cls.__table__
                # include_relationships = True
                # load_instance = True

            @post_dump
            def format_datetime_fields(self, data, **kwargs):
                for key, value in data.items():
                    # Check if the value is a datetime string by trying to convert it
                    try:
                        dt_obj = datetime.fromisoformat(value.replace("T", " "))
                        # If successful, reformat it
                        data[key] = dt_obj.strftime(DATETIME_FORMAT_SCHEMA)
                    except (ValueError, TypeError, AttributeError):
                        # Skip values that can't be converted to datetime
                        continue
                return data

            @post_dump(pass_many=True)
            def filter_fields(self, data, many, **kwargs):
                if many:
                    return [{key: item[key] for key in item if key not in hidden_fields} for item in data]
                return {key: data[key] for key in data if key not in hidden_fields}

        for field_name, field_obj in ModelSchema._declared_fields.items():
            if field_name in required_fields:
                field_obj.required = True
            else:
                field_obj.required = False

        return ModelSchema

    get_model_schema = generate_dynamic_schema('get')
    list_model_schema = generate_dynamic_schema('list')
    post_model_schema = generate_dynamic_schema('post')

    # get_model_schema.Meta.model = original_cls
    @route(f'{api_prefix}/resource/{single_name}', methods=['POST'], schema=post_model_schema)
    def create(validated_data={}):
        new_item = advanced_model_class(**validated_data)
        db.session.add(new_item)
        db.session.commit()
        return new_item

    @route(f'{api_prefix}/resource/{single_name}/<int:id>', methods=['GET'], schema=get_model_schema)
    def read(id, validated_data={}):
        item = advanced_model_class.query.get_or_404(id)
        return item

    @route(f'{api_prefix}/resource/{plural_name}', methods=['GET'], schema=list_model_schema)
    def list(validated_data={}):
        items = advanced_model_class.query.all()
        return items

    @route(f'{api_prefix}/resource/{single_name}/<int:item_id>', methods=['PUT'])
    def update(item_id, validated_data={}):
        item = advanced_model_class.query.get_or_404(item_id)
        for key, value in validated_data.items():
            setattr(item, key, value)
        db.session.commit()
        return True

    @route(f'{api_prefix}/resource/{single_name}/<int:item_id>', methods=['DELETE'])
    def delete(item_id, validated_data={}):
        item = advanced_model_class.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return True

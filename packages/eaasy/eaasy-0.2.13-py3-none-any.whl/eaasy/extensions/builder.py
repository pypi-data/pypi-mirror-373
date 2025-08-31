from eaasy import Common, BaseEntity, limiter
from eaasy.extensions.helper import verify_oidc
from typing import Any, Literal
from flask_restx import Namespace, Resource, Model, OrderedModel, fields
from flask_restx._http import HTTPStatus
from sqlalchemy.orm.attributes import InstrumentedAttribute
from eaasy.domain.exceptions import ErrorResponse
from datetime import datetime, timezone
from flask_oidc import OpenIDConnect
from authlib.integrations.flask_oauth2 import current_token

TokenProperties = Literal['sub', 'email_verified', 'email', 'name', 'preferred_username', 'given_name', 'family_name', 'username'] 


def buil_model(entity: Common | Any, namespace: Namespace | None = None) -> tuple[Namespace, Model | OrderedModel]:
    ns = namespace if namespace is not None \
        else Namespace(entity.__name__, description=f"{entity.__name__} operations", path=f"/{entity.__name__.lower()}")
    model_name = entity.__name__
    model_attributes = {}

    attributes = [x for x in entity.__dict__.keys() if not x.startswith('_')]

    for attr in attributes:
        attribute: InstrumentedAttribute = entity.__dict__[attr]
        if not attr.startswith('_'):
            if f'{attribute.type}' == 'INTEGER':
                model_attributes[attr] = fields.Integer(
                    required=not attribute.nullable, 
                    description=attr,
                    default=0 if not attribute.nullable else None,
                    example=0)
            elif 'NUMERIC' in f'{attribute.type}':
                model_attributes[attr] = fields.Float(
                    required=not attribute.nullable, 
                    description=attr,
                    default=0.0 if not attribute.nullable else None,
                    example=0.0)
            elif f'{attribute.type}' == 'VARCHAR':
                model_attributes[attr] = fields.String(
                    required=not attribute.nullable, 
                    description=attr,
                    default='' if not attribute.nullable else None,
                    example='string')
            elif f'{attribute.type}' == 'DATETIME':
                model_attributes[attr] = fields.DateTime(
                    required=not attribute.nullable, 
                    description=attr,
                    default=datetime.strftime(datetime.now(timezone.utc), '%Y-%m-%dT%H:%M:%S') if not attribute.nullable else None,
                    example=datetime.strftime(datetime.now(timezone.utc), '%Y-%m-%dT%H:%M:%S'))
            elif f'{attribute.type}' == 'BOOLEAN':
                model_attributes[attr] = fields.Boolean(
                    required=not attribute.nullable, 
                    description=attr,
                    default=False,
                    example=False)
            else:
                print(f"\033[33mType {attribute.type} not supported\033[0m")

    model = ns.model(model_name, model_attributes) 

    return ns, model

def build_dynamic_class(name: str, base_classes: list[type], **kwargs) -> type:
    return type(name, tuple(base_classes), kwargs)

def build_resource(
        entity: BaseEntity, 
        namespace: Namespace, 
        get_model: Model | OrderedModel,
        upsert_model: Model | OrderedModel,
        **kwargs) -> None:
    
    def _log(level: Literal['debug', 'info', 'warning', 'error'], message: str):
        logger = kwargs.get('logger', None)
        if logger is not None: # pragma: no cover
            getattr(logger, level)(message)

    def callback(name: str, data: Any = None):
        on_event = kwargs.get(name, None)
        if on_event is not None:
            try:
                on_event(data)
            except Exception as e:
                _log('error', f'Error on {name} event: {e}')
                on_callback_fail = kwargs.get(f'{name}_fail', None)
                if on_callback_fail is not None:
                    on_callback_fail(e)
                else: 
                    raise Exception({
                        'status_code': 500,
                        'message': str(e),
                        'data': data
                    })

    def get_limit_rate(name: str) -> str | None:
        limiter = kwargs.get('limit', None)
        return limiter if limiter is not None else kwargs.get(name, None)
    
    def get_oidc(name: str) -> OpenIDConnect | None:
        oidc = kwargs.get(name, None)
        return oidc if oidc is not None else kwargs.get('oidc', None)
    
    def get_current_user_info(property: TokenProperties) -> str: # pragma: no cover
        return dict(current_token)[property] # type: ignore
    
    class DynamicResourceGetAll(Resource, ErrorResponse):
        @verify_oidc(get_oidc('get_all_oidc'))
        @limiter.limit(get_limit_rate('get_all_limit') or "")
        @namespace.marshal_with(get_model, as_list=True)
        def get(self):
            all_entities = entity.get_all()
            sort_by = kwargs.get('sort_by', None)
            sorting = kwargs.get('sorting', 'asc')

            if sort_by is not None and sort_by in all_entities[0].__dict__.keys():
                all_entities = sorted(all_entities, key=lambda x: getattr(x, sort_by), reverse=(sorting=='desc'))
            elif sort_by is not None: # pragma: no cover
                _log('warning', f'Cannot sort by {sort_by}, attribute not found in entity {entity.__name__}')

            return all_entities, HTTPStatus.OK

    class DynamicResourceCreate(Resource, ErrorResponse):
        @verify_oidc(get_oidc('post_oidc'))
        @limiter.limit(get_limit_rate('post_limit') or "")
        @namespace.expect(upsert_model)
        @namespace.marshal_with(get_model)
        def post(self):
            try:
                data = entity.create(**namespace.payload)
                callback('on_post', data=data)
                
                return data, HTTPStatus.CREATED
            except Exception as e:
                self.error_response(e.args)

    class DynamicResourceGetById(Resource, ErrorResponse):
        @verify_oidc(get_oidc('get_by_id_oidc'))
        @limiter.limit(get_limit_rate('get_by_id_limit') or "")
        @namespace.marshal_with(get_model)
        def get(self, id):
            try:
                return entity.get_by_id(id), HTTPStatus.OK
            except Exception as e:
                self.error_response(e.args)

    class DynamicResourceEditById(Resource, ErrorResponse):
        @verify_oidc(get_oidc('put_oidc'))
        @limiter.limit(get_limit_rate('put_limit') or "")
        @namespace.expect(upsert_model)
        @namespace.marshal_with(get_model)
        def put(self, id):
            try:
                data = entity.update(id, **namespace.payload)
                callback('on_put', data=data)

                return data, HTTPStatus.OK
            except Exception as e:
                self.error_response(e.args)

    class DynamicResourceDeleteById(Resource, ErrorResponse):
        @verify_oidc(get_oidc('delete_all_oidc'))
        @limiter.limit(get_limit_rate('delete_limit') or "")
        def delete(self, id):
            try:
                entity.delete(id)
                callback('on_delete')
                return '', HTTPStatus.NO_CONTENT
            except Exception as e:
                self.error_response(e.args)

    get_all = kwargs.get('get_all', True)
    post = kwargs.get('post', True)

    get_by_id = kwargs.get('get_by_id', True)
    put = kwargs.get('put', True)
    delete = kwargs.get('delete', True)

    all = []
    if get_all: all.append(DynamicResourceGetAll)
    if post: all.append(DynamicResourceCreate)

    if len(all) > 0:
        DynamicResource = build_dynamic_class('DynamicResource', all)
        namespace.add_resource(DynamicResource, '/')

    by_id = []
    if get_by_id: by_id.append(DynamicResourceGetById)
    if put: by_id.append(DynamicResourceEditById)
    if delete: by_id.append(DynamicResourceDeleteById)

    if len(by_id) > 0:
        DynamicResourceById = build_dynamic_class('DynamicResourceById', by_id)
        namespace.add_resource(DynamicResourceById, '/<int:id>')

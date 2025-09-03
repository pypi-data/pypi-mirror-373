import sqlalchemy  # Leave here for tests (mocking 'update' function)
from sqlalchemy import create_engine, Column, Integer, DateTime, text
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
import os

Base = declarative_base()

class SessionManager: # pragma: no cover
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = scoped_session(session_factory)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

class Common(Base):
    __abstract__ = True

    # Utility
    @classmethod
    def __dict_to_entity__(cls, data):
        return {key: value for key, value in data.items() if hasattr(cls, key)}

    # Session
    @classmethod
    def get_session(cls): # pragma: no cover
        POSTGRES_URI = os.getenv('POSTGRES_URI')

        if not POSTGRES_URI:
            raise EnvironmentError(
                "Missing 'POSTGRES_URI' environment variable")  # pragma: no cover

        # Proceed to create the engine
        engine = create_engine(POSTGRES_URI)

        return SessionManager(sessionmaker(bind=engine))

    # CRUD Errors
    @classmethod
    def field_not_nullable(cls, field: str):
        raise Exception({
            'status_code': 400,
            'message': f'{field} cannot be null',
            'data': {'field': field},
        })
    
    @classmethod
    def foreign_key_not_found(cls, field: str, value: str):
        raise Exception({
            'status_code': 400,
            'message': f'invalid foreign key: {field} with id {value} not found',
            'data': {},
        })

    @classmethod
    def not_found(cls, **kwargs):
        raise Exception({
            'status_code': 404,
            'message': f'{cls.__name__} with {kwargs} not found',
            'data': kwargs,
        })

    @classmethod
    def already_exists(cls, details, **kwargs):
        raise Exception({
            'status_code': 409,
            'message': f'{cls.__name__} {details}',
            'data': kwargs,
        })

    @classmethod
    def failure(cls, message: str, **kwargs):
        raise Exception({
            'status_code': 500,
            'message': message,
            'data': kwargs,
        })

    @classmethod
    def integrity_error(cls, message: str, **kwargs):
        if "not-null" in message:
            field = message.split('"')[1]
            cls.field_not_nullable(field)
        elif "duplicate key" in message:
            details = message.split('DETAIL:  ')[1].split("\n")[0]
            cls.already_exists(details=details, **kwargs)
        elif "violates foreign key constraint" in message:
            field = message.split('"')[1]
            value = message.split('=(')[1].split(')')[0]
            cls.foreign_key_not_found(field, value)
        else:
            cls.failure(message, **kwargs)

class BaseEntity(Common):
    __abstract__ = True

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    @classmethod
    def get_by_id(cls, id: int):
        with cls.get_session() as session:
            data = session.query(cls).get(id)
            return data if data else cls.not_found(id=id)

    @classmethod
    def get_all(cls):
        with cls.get_session() as session:
            return session.query(cls).order_by(cls.id).all()


    @classmethod
    def create(cls, **kwargs):
        with cls.get_session() as session:
            try:
                obj = cls(**cls.__dict_to_entity__(kwargs))
                session.add(obj)
                session.commit()
                session.refresh(obj)
                return obj
            except IntegrityError as e:
                session.rollback()
                cls.integrity_error(str(e.orig), **kwargs)
            except Exception as e:
                session.rollback()
                cls.failure(str(e), **kwargs)

    @classmethod
    def update(cls, id: int, **kwargs):
        with cls.get_session() as session:
            try:
                assert cls.get_by_id(id)
                obj = cls.__dict_to_entity__(kwargs)
                update_obj = sqlalchemy.update(cls).where(cls.id == id).values(**obj)
                session.execute(update_obj)
                session.commit()
                return cls.get_by_id(id)
            except IntegrityError as e:
                session.rollback()
                cls.integrity_error(str(e.orig), **kwargs)
            except Exception as e:
                session.rollback()
                if 'status_code' in e.args[0]:
                    raise e
                cls.failure(str(e), **kwargs)

    @classmethod
    def delete(cls, id: int):
        with cls.get_session() as session:
            try:
                obj = cls.get_by_id(id)
                session.delete(obj)
                session.commit()
            except Exception as e:
                session.rollback()
                if 'status_code' in e.args[0]:
                    raise e
                cls.failure(str(e), id=id)

class Audit:
    __abstract__ = True

    createdAt = Column(DateTime(timezone=False), nullable=False, default=text("(select current_timestamp at time zone 'UTC')"))
    updatedAt = Column(DateTime(timezone=False), nullable=False, default=text("(select current_timestamp at time zone 'UTC')"), onupdate=text("(select current_timestamp at time zone 'UTC')"))
    deletedAt = Column(DateTime(timezone=False), nullable=True)

__all__ = ['Base', 'Common', 'BaseEntity', 'Audit']

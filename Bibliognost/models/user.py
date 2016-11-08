import hashlib
import uuid
from datetime import datetime

from flask import g, request
from flask_login import UserMixin, AnonymousUserMixin
from psycopg2.extensions import adapt
from psycopg2.extras import RealDictCursor, register_uuid
from werkzeug.security import generate_password_hash, check_password_hash

from Bibliognost import login_manager
from .role import Role


@login_manager.user_loader
def load_user(email):
    """
    callback function to load user object, given an email as unicode string.

    :param email: email of the user
    :type email: str
    :return: User object, if found, else None.
    """
    
    return User.get(email=email)


def fetch_user_data_from_db(field_name, value, fields=('*',)):
    """
    queries db and fetches the user based on a given email.

    :param field_name: 'email' or 'id' of the user
    :type field_name: str
    :param value: value of the field_name
    :type value: str
    :param fields: specify fields to get from the db, default is all fields '*'.
    :type fields: tuple[str]
    :return: A Dictionary with keys as column name of the table if user is found, else None
    """
    cursor = g.db.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT {0} FROM users WHERE {1} = %s'.format(', '.join(fields), field_name), (value, ))
    return cursor.fetchone()


def insert_user_data_to_db(**kwargs):
    """
    persists the user

    :param kwargs: a dictionary with column name as keys
    :type kwargs: dict
    :return: status message returned from executing the SQL
    :raises: TypeError, if columns with no default value in table are not in kwargs
    """
    missing_required_keys = tuple(filter(lambda field: field not in kwargs, User.REQUIRED_FIELDS))
    if missing_required_keys:
        raise TypeError('missing required field(s) in kwargs, {0}'.format(missing_required_keys))
    register_uuid()
    cursor = g.db.cursor()
    cursor.execute(
        'INSERT INTO users ({0}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'.format(', '.join(User.REQUIRED_FIELDS)),
        (
            adapt(kwargs.get('id')),
            kwargs.get('name'),
            kwargs.get('email'),
            kwargs.get('password'),
            kwargs.get('role'),
            kwargs.get('createtime'),
            kwargs.get('updatetime'),
            kwargs.get('lastscene')
        )
    )
    return cursor.statusmessage


class User(UserMixin):
    """
    Mapping of user table as python object.
    Required fields must be provied while constructing the object
    Read-only fields, once initialized, must not be set again
    """
    REQUIRED_FIELDS = ("id", "name", "email", "password", "role", "createtime", "updatetime", "lastscene")
    READ_ONLY = ("createtime",)

    #: Assignment operators must not be used on read-only fields
    #: of the user object. They can be set only at the
    #: time of initialization.

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.bio = kwargs.get('bio')
        self.avatar_hash = kwargs.get('avatarhash')
        self.location = kwargs.get('location')
        self.updatetime = kwargs.get('updatetime')
        self.lastscene = kwargs.get('lastscene')
        self._password_hash = kwargs.get('password')
        self._createtime = kwargs.get('createtime')
        self._role = kwargs.get('role')

        if self.email and not self.avatar_hash:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            cursor = g.db.cursor()
            cursor.execute(
                'UPDATE users SET avatarhash = %s WHERE email = %s', (self.avatar_hash, self.email)
            )

    @property
    def password(self):
        raise AttributeError('password is not a readable property')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    @property
    def createtime(self):
        return self._createtime

    @createtime.setter
    def createtime(self):
        raise Exception("createtime: read-only fields do not support assignment operator")

    @property
    def role(self):
        if not self._role:
            self.role = fetch_user_data_from_db('email', self.email, ('role_name',))['role_name']
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    @property
    def is_active(self):
        """All users are active"""
        return True

    @property
    def is_anonymous(self):
        """Always return False, anonymous users aren't supported"""
        return False

    @property
    def is_authenticated(self):
        """All users are authenticated"""
        return True

    def get_first_name(self):
        return self.name.split(' ')[0]

    def ping(self):
        cursor = g.db.cursor()
        cursor.execute(
            'UPDATE users SET lastscene = %s WHERE id = %s', (datetime.timestamp(datetime.utcnow()) * 1000, self.id)
        )

    def is_admin(self):
        """verifies if the user is admin"""
        return self.role == Role.ROLE_ADMIN

    def get_id(self):
        """Return email for flask_login to use it as user id"""
        return self.email

    def can(self, *permissions):
        """
        verifies whether a user has permission to perform a task

        :param permissions: list of permissions
        :return: bool, True if the user has all the permissions
        """
        return all(permission in Role.ROLES[self.role] for permission in permissions)

    def gravatar(self, size=256, default='retro', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
            md5_hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=md5_hash, size=size, default=default, rating=rating
        )

    @classmethod
    def register(cls, **user_info):
        """
        registers a new user

        :param user_info: name, email and password as keys
        :type user_info: dict
        :return: User object on successful registration, else None
        """
        timestamp = datetime.timestamp(datetime.utcnow()) * 1000
        user_info['id'] = uuid.uuid4()
        user_info['createtime'] = timestamp
        user_info['updatetime'] = timestamp
        user_info['lastscene'] = timestamp
        user_info['role'] = Role.DEFAULT_ROLE
        user = cls(**user_info)
        user.password = user_info.pop('password')
        response = insert_user_data_to_db(**user_info, password=user._password_hash)
        if response:
            return user
    
    @classmethod
    def get(cls, **field_name_with_val):
        """
        Fetches user from the DB based on their email or id.

        :param field_name_with_val: key must be either 'email' or 'id' of the user, not both
        :type field_name_with_val: dict
        :return: User object if found, else None
        :raises: TypeError, if neither or both of `email` or `id` is provided
        """
        has_both_keys = all(key in field_name_with_val for key in ("email", "id"))
        has_none_keys = not any(key in field_name_with_val for key in ("email", "id"))
        if has_both_keys or has_none_keys:
            raise TypeError('Invalid Argument: neither or both of `email` or `id` provided')
        field_name = "email" if "email" in field_name_with_val else "id"
        user = fetch_user_data_from_db(field_name, field_name_with_val[field_name])
        if user:
            return cls(**user)

    def __repr__(self):
        return 'User(name={0}, email={1})'.format(self.name, self.email)


class AnonymousUser(AnonymousUserMixin):
    def can(self, *permissions):
        """Anonymous user have no permissions, always return false"""
        del permissions  #: Just to supress the PEP warning
        return False

    def is_admin(self):
        """Anonymous user can never be admin"""
        return False

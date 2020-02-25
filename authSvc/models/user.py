import datetime, uuid

from pymodm import fields, MongoModel
from models.role import Role


class User(MongoModel):
    class Meta:
        collection_name = 'user'
        connection_alias = 'cytang-flask-mongo'
        final = True
    
    uuid = fields.CharField(primary_key=True, default=uuid.uuid4)
    username = fields.CharField(required=True)
    email = fields.EmailField(required=True)
    password = fields.CharField(required=True)
    roles = fields.ListField(fields.ReferenceField(Role), default=[], blank=True)
    created_at = fields.DateTimeField(required=False, default=datetime.datetime.utcnow())
    updated_at = fields.DateTimeField(required=False, default=datetime.datetime.utcnow())

    _updatable_fields = {'username', 'password', 'roles'} # Set

    def patch(self, **kwargs):
        updatable_data = {field : value for field, value in kwargs.items() if field in self._updatable_fields}
        for field, value in updatable_data.items():
            setattr(self, field, value)
        self.updated_at = datetime.datetime.utcnow()
        self.save()

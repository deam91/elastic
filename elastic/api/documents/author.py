from django_elasticsearch import Document, fields
from django_elasticsearch.registries import registry

from api.models import Author, Book


@registry.register_document
class AuthorDocument(Document):

    books = fields.NestedField(properties={
        'title': fields.TextField(),
        'description': fields.TextField(),
        'created': fields.TextField(),
        'category': fields.ObjectField(properties={
            'name': fields.TextField()
        })
    })

    class Index:
        name = 'authors'
        related_models = [Book]

    class Django:
        model = Author
        fields = ['first_name', 'last_name']

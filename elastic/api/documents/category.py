from django_elasticsearch import Document
from django_elasticsearch.registries import registry

from api.models import Category


@registry.register_document
class CategoryDocument(Document):
    class Index:
        name = 'categories'
        related_models = []

    class Django:
        model = Category
        fields = ['name']

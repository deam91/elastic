from django_elasticsearch import Document, fields
from django_elasticsearch.registries import registry

from api.models import Book, Category, Author


@registry.register_document
class BookDocument(Document):

    category = fields.ObjectField(properties={
        'name': fields.TextField()
    })

    class Index:
        name = 'books'

    class Django:
        model = Book
        fields = ['title', 'description', 'created']
        related_models = [Category]

    def get_queryset(self):
        """Select related in sql requests to improve performance"""
        return super(BookDocument, self).get_queryset().select_related('category')

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Category instance(s) from the related model.
        Use related_models with caution, it cause the index to updating a lot of items.
        """
        if isinstance(related_instance, Category):
            return related_instance.books.all()
        elif isinstance(related_instance, Author):
            return related_instance.books

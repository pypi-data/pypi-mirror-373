import factory

from wbcrm.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=32)
    is_competitor = factory.Faker("pybool")

    class Meta:
        model = Product

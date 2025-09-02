import factory

from .models import AssetAllocation, AssetAllocationType, GeographicFocus


class AssetAllocationTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    default_max_investment = factory.Faker("pydecimal", min_value=0.0, max_value=1, right_digits=4)

    class Meta:
        model = AssetAllocationType


class AssetAllocationFactory(factory.django.DjangoModelFactory):
    company = factory.SubFactory("wbcore.contrib.directory.factories.CompanyFactory")
    asset_type = factory.SubFactory(AssetAllocationTypeFactory)
    percent = factory.Faker("pydecimal", min_value=0.0, max_value=1, right_digits=4)
    max_investment = factory.Faker("pydecimal", min_value=0.0, max_value=1, right_digits=4)
    comment = factory.Faker("sentence")

    class Meta:
        model = AssetAllocation


class GeographicFocusFactory(factory.django.DjangoModelFactory):
    company = factory.SubFactory("wbcore.contrib.directory.factories.CompanyFactory")
    country = factory.SubFactory("wbcore.contrib.geography.factories.CountryFactory")
    percent = factory.Faker("pydecimal", min_value=0.0, max_value=1, right_digits=4)
    comment = factory.Faker("sentence")

    class Meta:
        model = GeographicFocus

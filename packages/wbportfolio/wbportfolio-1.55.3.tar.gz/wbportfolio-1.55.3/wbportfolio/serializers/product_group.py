from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Company
from wbcore.contrib.directory.serializers import CompanyRepresentationSerializer
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer
from wbfdm.serializers.instruments import InstrumentModelSerializer

from wbportfolio.models import ProductGroup, ProductGroupRepresentant
from wbportfolio.serializers.portfolios import PortfolioRepresentationSerializer


class ProductGroupRepresentantRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _representant = CompanyRepresentationSerializer(source="representant")
    _country = GeographyRepresentationSerializer(source="country", filter_params={"level": 1})

    class Meta:
        model = ProductGroupRepresentant
        fields = (
            "id",
            "product_group",
            "representant",
            "_representant",
            "country",
            "_country",
        )


class ProductGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:product_group-detail")

    class Meta:
        model = ProductGroup
        fields = ("id", "computed_str", "name_repr", "_detail")


class ProductGroupModelSerializer(InstrumentModelSerializer):
    id_repr = wb_serializers.CharField(source="id", read_only=True, label="ID")
    _management_company = CompanyRepresentationSerializer(source="management_company")
    management_company = wb_serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all().select_related("entry_ptr")
    )

    _depositary = CompanyRepresentationSerializer(source="depositary")
    depositary = wb_serializers.PrimaryKeyRelatedField(queryset=Company.objects.all().select_related("entry_ptr"))

    _transfer_agent = CompanyRepresentationSerializer(source="transfer_agent")
    transfer_agent = wb_serializers.PrimaryKeyRelatedField(queryset=Company.objects.all().select_related("entry_ptr"))

    _administrator = CompanyRepresentationSerializer(source="administrator")
    administrator = wb_serializers.PrimaryKeyRelatedField(queryset=Company.objects.all().select_related("entry_ptr"))

    _investment_manager = CompanyRepresentationSerializer(source="investment_manager")
    investment_manager = wb_serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all().select_related("entry_ptr")
    )

    _auditor = CompanyRepresentationSerializer(source="auditor")
    auditor = wb_serializers.PrimaryKeyRelatedField(queryset=Company.objects.all().select_related("entry_ptr"))

    _paying_agent = CompanyRepresentationSerializer(source="paying_agent")
    paying_agent = wb_serializers.PrimaryKeyRelatedField(queryset=Company.objects.all().select_related("entry_ptr"))

    _portfolios = PortfolioRepresentationSerializer(source="portfolios", many=True)

    class Meta(InstrumentModelSerializer.Meta):
        model = ProductGroup
        fields = (
            "id_repr",
            "type",
            "category",
            "umbrella",
            "management_company",
            "_management_company",
            "depositary",
            "_depositary",
            "transfer_agent",
            "_transfer_agent",
            "administrator",
            "_administrator",
            "investment_manager",
            "_investment_manager",
            "auditor",
            "_auditor",
            "paying_agent",
            "_paying_agent",
            "representants",
            # "_representants",
            "_portfolios",
            "portfolios",
        ) + InstrumentModelSerializer.Meta.fields

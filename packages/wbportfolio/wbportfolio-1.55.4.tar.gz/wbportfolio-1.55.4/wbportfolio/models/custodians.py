from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from wbcore.contrib.directory.models import Company
from wbcore.models import WBModel


class Custodian(WBModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Name",
        help_text="The Name of the Custodian.",
    )
    company = models.ForeignKey(
        "directory.Company", null=True, blank=True, on_delete=models.SET_NULL, related_name="custodians"
    )
    mapping = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        verbose_name="Custodian Mapping",
        help_text="Each custodian of this mapping will be assigned to this custodian.",
    )

    @staticmethod
    def get_unspecified_bank_name():
        return "<NO BANK SPECIFIED>"

    @classmethod
    def get_unspecified_bank(cls):
        return cls.get_by_mapping(cls.get_unspecified_bank_name())

    @classmethod
    def get_by_mapping(cls, mapping: str, use_similarity=False, create_missing=True):
        SIMILIRATY_SCORE = 0.7
        lower_mapping = mapping.lower()
        try:
            return cls.objects.get(mapping__contains=[lower_mapping])
        except cls.DoesNotExist:
            if use_similarity:
                similar_custodians = cls.objects.annotate(
                    similarity_score=TrigramSimilarity("name", lower_mapping)
                ).filter(similarity_score__gt=SIMILIRATY_SCORE)
                if similar_custodians.count() == 1:
                    custodian = similar_custodians.first()
                    print(f"find similar custodian {lower_mapping} -> {custodian.name}")  # noqa: T201
                    custodian.mapping.append(lower_mapping)
                    custodian.save()
                    return custodian
                else:
                    similar_companies = Company.objects.annotate(
                        similarity_score=TrigramSimilarity("name", lower_mapping)
                    ).filter(similarity_score__gt=SIMILIRATY_SCORE)
                    if similar_companies.count() == 1:
                        print(  # noqa: T201
                            f"Find similar company {lower_mapping} -> {similar_companies.first().name}"
                        )  # noqa: T201
                        return cls.objects.create(
                            name=lower_mapping, mapping=[lower_mapping], company=similar_companies.first()
                        )
        if create_missing:
            return cls.objects.create(name=lower_mapping, mapping=[lower_mapping])

    def merge(self, custodian):
        if self != custodian:
            custodian.trades.update(custodian=self)
            self.mapping = list(set(self.mapping + custodian.mapping))
            if not self.company and custodian.company:
                self.company = custodian.company
            self.save()
            custodian.delete()

    def split_off(self, mapping):
        if mapping in self.mapping:
            self.mapping.remove(mapping)
            self.save()
            custodian = Custodian.objects.create(name=mapping, mapping=[mapping])
            self.trades.filter(bank=mapping).update(custodian=custodian)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Custodian"
        verbose_name_plural = "Custodians"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:custodian"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:custodianrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

class OppositeSharesFieldMethodMixin:
    def filter_opposite_shares(self, queryset, name, value):
        return queryset.filter(shares=value * -1)

    def filter_opposite_approximate_shares(self, queryset, name, value):
        value = float(value)
        value_lower_bound = -0.9 * value
        value_higher_bound = -1.1 * value

        if value > 0:
            return queryset.filter(shares__lte=value_lower_bound, shares__gte=value_higher_bound)
        return queryset.filter(shares__lte=value_higher_bound, shares__gte=value_lower_bound)

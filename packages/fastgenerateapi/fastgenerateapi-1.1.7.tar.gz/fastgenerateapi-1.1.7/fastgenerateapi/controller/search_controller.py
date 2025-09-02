from typing import Union

from tortoise.queryset import QuerySet

from fastgenerateapi.controller.filter_controller import FilterController


class SearchController(FilterController):
    """
        SearchController
    """

    def query(self, queryset: QuerySet, value: Union[str, list]) -> QuerySet:
        """
            do query action
        :param queryset:
        :param value:
        :return:
        """
        q = None
        if len(self.filters) == 0:
            return queryset
        for f in self.filters:
            if not value:
                continue

            if q is None:
                q = f.generate_q(value=value)
            else:
                q = q | f.generate_q(value=value)
        if q is None:
            return queryset
        queryset = queryset.filter(q)
        return queryset



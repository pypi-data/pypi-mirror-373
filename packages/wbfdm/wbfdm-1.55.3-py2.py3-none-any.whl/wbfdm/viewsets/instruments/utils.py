from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q
from django.db.models.expressions import Value
from django.db.models.functions import Coalesce


class InstrumentSearchFilter:
    def get_min_search_rank(self, view) -> float:
        return getattr(view, "SEARCH_MIN_RANK", 0.3)

    def filter_queryset(self, request, queryset, view):
        if search := request.GET.get("search", None):
            min_search_rank = self.get_min_search_rank(view)
            query = SearchQuery(search, search_type="phrase")
            return (
                queryset.annotate(search_rank=Coalesce(SearchRank(F("search_vector"), query), Value(-1.0)))
                .filter(
                    (Q(search_vector=query) & Q(search_rank__gte=min_search_rank))
                    | Q(name__icontains=search)
                    | Q(name_repr__icontains=search)
                    | Q(isin__icontains=search)
                )
                .order_by("-search_rank")
            ).distinct()
        elif "parent" in request.GET:
            return queryset.order_by("-is_primary", "computed_str")
        return queryset

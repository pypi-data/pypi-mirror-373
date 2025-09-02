{% with financial_table="TreActRpt", value="DefActValue", only_valid=True, estimate=False %}
    {% include 'qa/sql/ibes/financials.sql' %}
{% endwith %}

union

{% with financial_table="TreSumPer", value="DefMeanEst", only_valid=True, from_index=1, estimate=True %}
    {% include 'qa/sql/ibes/financials.sql' %}
{% endwith %}

{% with financial_table="TreSumPer", value="DefMeanEst", estimate=True, only_valid=True %}
    {% include 'qa/sql/ibes/base_estimates.sql' %}
{% endwith %}

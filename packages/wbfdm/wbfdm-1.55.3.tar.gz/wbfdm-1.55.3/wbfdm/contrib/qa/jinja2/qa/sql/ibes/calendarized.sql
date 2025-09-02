with data as (
    {% with financial_table="TreActRpt", value="DefActValue", only_valid=True, estimate=False %}
        {% include 'qa/sql/ibes/financials.sql' %}
    {% endwith %}

    union

    {% with financial_table="TreSumPer", value="DefMeanEst", only_valid=True, from_index=1, estimate=True %}
        {% include 'qa/sql/ibes/financials.sql' %}
    {% endwith %}
)

select
    *,
    case
        when period_type = 'Y' and month(period_end_date) = 12 then value
        when period_type = 'Y'
            then month(period_end_date) * value / 12 + (12 - month(period_end_date)) * lead(value, 1) over (partition by financial, external_identifier, period_type order by period_end_date) / 12
        when period_type = 'Q' and (
            (interim = 1 and month(period_end_date) = 3)
            or (interim = 2 and month(period_end_date) = 6)
            or (interim = 3 and month(period_end_date) = 9)
            or (interim = 4 and month(period_end_date) = 12)
        )
            then value
        when period_type = 'Q'
            then month(period_end_date) * value / 3 + (3 - month(period_end_date)) * lead(value, 1) over (partition by financial, external_identifier, period_type order by period_end_date) / 3

        when period_type = 'S' and (
            (interim = 1 and month(period_end_date) = 6)
            or (interim = 2 and month(period_end_date) = 12)
        )
            then value
        when period_type = 'S'
            then month(period_end_date) * value / 6 + (6 - month(period_end_date)) * lead(value, 1) over (partition by financial, external_identifier, period_type order by period_end_date) / 6
    end as _value
from data

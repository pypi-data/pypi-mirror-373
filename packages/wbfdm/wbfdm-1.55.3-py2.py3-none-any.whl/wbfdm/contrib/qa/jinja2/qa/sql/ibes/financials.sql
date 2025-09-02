select
    case
        when fin.PerType = 2 then 'M'
        when fin.PerType = 3 then 'Q'
        when fin.PerType = 4 then 'Y'
        when fin.PerType = 5 then 'S'
    end as period_type,
    convert(date, fin.ExpireDate) as valid_until,
    fin.EstPermID as external_identifier,
    convert(date, fin.PerEndDate) as period_end_date,

    idx.FiscalYear as year,
    idx.FiscalIndex as interim,
    idx.PerIndex as 'index',

    case
        when (code.Description collate Latin1_General_Bin) = 'GBp' then {{ value|identifier }} * DefScale / 100
        else {{ value | identifier }} * DefScale
    end as value,

    code.Description as currency,
    mapping.financial as financial,
    {% block additional_fields%}{% endblock %}
    {% if estimate %}1{% else %}0{% endif %} as estimate,
    'qa-ibes' as source

from {{ financial_table |identifier }} as fin

join TrePerIndex as idx
    on idx.EstPermID = fin.EstPermID
    and idx.PerType = fin.PerType
    and idx.PerEndDate = fin.PerEndDate

join stainly_financial_mapping as mapping
    on mapping.ibes_financial = fin.Measure

left join TreCode as code
    on code.Code = fin.DefCurrPermID
    and code.CodeType = 7

where
    fin.EffectiveDate = (
        select max(EffectiveDate)
        from {{ financial_table |identifier }}
        where
            EstPermID = fin.EstPermID
            and PerEndDate = fin.PerEndDate
            and PerType = fin.PerType
            and Measure = fin.Measure
            and (
                ExpireDate = fin.ExpireDate
                or (fin.ExpireDate is null and ExpireDate is null)
            )
    )

    and fin.EstPermID in (
        {% for instrument in instruments %}
            {{ instrument }}{% if not loop.last %},{% endif %}
        {% endfor %}
    )

    and mapping.financial in (
        {% for financial in financials %}
            {{ financial }}{% if not loop.last %},{% endif %}
        {% endfor %}
    )

    {% if only_valid %}and fin.ExpireDate is null{% endif %}

    {% if from_year %}and idx.FiscalYear >= {{ from_year }}{% endif %}
    {% if to_year %}and idx.FiscalYear <= {{ to_year }}{% endif %}

    {% if from_date %}and fin.PerEndDate >= {{ from_date }}{% endif %}
    {% if to_date %}and fin.PerEndDate <= {{ to_date }}{% endif %}

    {% if from_index or from_index == 0 %}and idx.PerIndex >= {{ from_index }}{% endif %}
    {% if to_index or to_index == 0 %}and idx.PerIndex <= {{ to_index }}{% endif %}

    {% if period_type == 'annual' %}and idx.FiscalIndex = 0{% elif period_type == 'interim' %}and idx.FiscalIndex > 0{% endif %}

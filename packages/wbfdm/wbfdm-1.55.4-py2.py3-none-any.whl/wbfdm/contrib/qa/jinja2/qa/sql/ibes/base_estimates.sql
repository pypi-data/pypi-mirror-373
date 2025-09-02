{% extends 'qa/sql/ibes/financials.sql' %}

{% block additional_fields %}
(
    select DefActValue * DefScale
    from TreActRpt
    where
        fin.EstPermID = EstPermID
        and fin.PerEndDate = PerEndDate
        and fin.Measure = Measure
        and fin.PerType = PerType
        and ExpireDate is null
        and fin.IsParent = IsParent
) as actual_value,
case
    when fin.DefMeanEst = 0 then null
    else ((
        select DefActValue * DefScale
        from TREActRpt
        where
            fin.EstPermID = EstPermID
            and fin.PerEndDate = PerEndDate
            and fin.Measure = Measure
            and fin.PerType = PerType
            and ExpireDate IS NULL
            and fin.IsParent = IsParent
    ) - (fin.DefMeanEst * fin.DefScale)) / (fin.DefMeanEst * fin.DefScale)
end AS difference_pct,
fin.DefHighEst * fin.DefScale AS value_high,
fin.DefLowEst * fin.DefScale AS value_low,
fin.DefStdDev * fin.DefScale AS value_stdev,
fin.NumEsts AS value_amount,
{% endblock %}

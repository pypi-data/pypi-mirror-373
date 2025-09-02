SELECT
    'qa-ds2-company' AS 'source',
    company.DsCmpyCode AS 'source_id',
    NULL AS 'parent_id',
    coalesce(cmp_ref.PrimaryName, company.DsCmpyName) AS 'name',
    company.CmpyCtryCode AS 'country_id',
    exchange_qt.ISOCurrCode AS 'currency_id',
    'company' AS 'instrument_type_id',
    rkd_instrument.ISIN AS 'isin',
    rkd_instrument.Ticker AS 'ticker',
    rkd_instrument.RIC AS 'refinitiv_identifier_code',
	country_qt.DsMnem AS 'refinitiv_mnemonic_code',
    rkd_instrument.Cusip AS 'cusip',
    rkd_instrument.Sedol AS 'sedol',
    filing.TxtInfo AS 'description',
    rkd_cmp_det.Employees AS 'employees',
    (select top 1 concat('00', phone.CtryPh, phone.City, phone.PhoneNo) from RKDFndCmpPhone AS phone where phone.Code = rkd_instrument.Code AND PhTypeCode = 1) AS 'phone',
    (select top 1 web.URL from RKDFndCmpWebLink AS web where web.Code = rkd_instrument.Code AND web.URLTypeCode = 1) AS 'primary_url',
    (select string_agg(web.URL, ',') from RKDFndCmpWebLink AS web where web.Code = rkd_instrument.Code AND web.URLTypeCode <> 1) AS 'additional_urls',
    concat(rkd_cmp_det.StAdd1, ', ', rkd_cmp_det.Post, ', ', rkd_cmp_det.City) AS 'headquarter_address',
    convert(Date, COALESCE(rkd_cmp_det.PublicSince, (SELECT MIN(MarketDate) FROM DS2PrimQtPrc WHERE InfoCode = exchange_qt.InfoCode))) AS 'inception_date',
	NULL AS 'delisted_date',
    convert(Date, cmp_ref.LatestFinAnnDt) AS 'last_annual_report',
    convert(Date, cmp_ref.LatestFinIntmDt) AS 'last_interim_report',
    -- MarketData DL
    exchange_qt.InfoCode AS 'quote_code',
    exchange_qt.ExchIntCode AS 'exchange_code',
    -- Fundamental DL
    rkd_instrument.Code AS 'rkd_code',
    -- Forecast DL
    ibes_mapping.EstPermID AS 'ibes_code'

FROM DS2Company AS company

LEFT JOIN DS2Security AS security
    ON company.DsCmpyCode = security.DsCmpyCode
    AND security.IsMajorSec = 'Y'

LEFT JOIN DS2ExchQtInfo AS exchange_qt
    ON exchange_qt.InfoCode = security.PrimQtInfoCode
    AND exchange_qt.IsPrimExchQt = 'Y'

LEFT JOIN DS2CtryQtInfo AS country_qt
    ON exchange_qt.InfoCode = country_qt.InfoCode

LEFT JOIN vw_SecurityMappingX AS mappingX
    ON mappingX.vencode = security.PrimQtInfoCode
    AND mappingX.ventype = 33
    AND mappingX.rank = 1
    AND mappingX.StartDate = (
        SELECT MAX(I.StartDate)
        FROM vw_SecurityMappingX AS I
        WHERE I.typ = mappingX.typ AND I.vencode = mappingX.vencode AND I.ventype = mappingX.ventype
    )

LEFT JOIN vw_SecurityMappingX AS mappingRKD
    ON mappingX.seccode = mappingRKD.seccode
    AND mappingX.typ = mappingRKD.typ
    AND mappingRKD.ventype = 26
    AND mappingRKD.rank = 1
    AND mappingRKD.StartDate = (
        SELECT MAX(I.StartDate)
        FROM vw_SecurityMappingX AS I
        WHERE I.typ = mappingRKD.typ AND I.vencode = mappingRKD.vencode AND I.ventype = mappingRKD.ventype
    )

LEFT JOIN RKDFndCmpRefIssue AS rkd_instrument
    ON rkd_instrument.IssueCode = mappingRKD.vencode

LEFT JOIN RKDFndCmpDet AS rkd_cmp_det
    ON rkd_cmp_det.Code = rkd_instrument.Code

LEFT JOIN RKDFndCmpRef AS cmp_ref
    ON cmp_ref.Code = rkd_instrument.Code

LEFT JOIN RKDFndCmpFiling AS filing
    ON filing.Code = rkd_instrument.Code
    AND filing.TxtInfoTypeCode = 2

LEFT JOIN vw_IBES2Mapping AS ibes_mapping
    ON ibes_mapping.SecCode = mappingX.seccode
    AND ibes_mapping.typ = mappingX.typ
    AND ibes_mapping.Exchange = (
        CASE
            WHEN ibes_mapping.typ = 6 THEN 0
            WHEN ibes_mapping.typ = 1 THEN 1
        END
    )

{% if source_id %}
where company.DsCmpyCode = {{ source_id }}
{% endif %}
-- where company.CmpyCtryCode = 'IS'

ORDER BY company.DsCmpyCode

{% if (offset == 0 or offset) and batch %}
offset {{ offset|sqlsafe }} rows
fetch next {{ batch|sqlsafe }} rows only
{% endif %}

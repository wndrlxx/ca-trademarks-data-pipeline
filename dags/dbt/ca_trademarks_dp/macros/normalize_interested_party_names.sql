{% macro normalize_interested_party_names(column_name) %}
    case
        when contains_substr({{ column_name }}, '911979')
        then 'Shoppers Drug Mart'
        when contains_substr({{ column_name }}, 'canada post')
        then 'Canada Post Corporation'
        when contains_substr({{ column_name }}, 'loblaw')
        then 'Loblaws Inc.'
        when contains_substr({{ column_name }}, 'molson')
        then 'Molson Canada'
        when regexp_contains({{ column_name }}, r'(?i)canadia.*tire')
        then 'Canadian Tire Corporation'
        when contains_substr({{ column_name }}, 'anheuser')
        then 'Anheuser Busch'
        when contains_substr({{ column_name }}, 'kellogg')
        then 'Kellogg Company'
        when regexp_contains({{ column_name }}, r'(?i)proctor.*gamble')
        then 'Proctor & Gamble'
        when contains_substr({{ column_name }}, 'imperial tobacco')
        then 'Imperial Tobacco'
        when regexp_contains({{ column_name }}, r'(?i)rothman.*ben.*hedge')
        then 'Rothmans, Benson & Hedges Inc.'
        when
            regexp_contains(
                {{ column_name }},
                r'(?i)engineers canada|canadian council of professional engineers'
            )
        then 'Engineers Canada'
        when contains_substr({{ column_name }}, 'lidl stiftung')
        then 'Lidl Stiftung & Co. KG'
        when contains_substr({{ column_name }}, 'royal bank of canada')
        then 'Royal Bank of Canada'
        when contains_substr({{ column_name }}, 'dundee corporation')
        then 'Dundee Corporation'
        when regexp_contains({{ column_name }}, r'(?i)lg (?:display|corp|electronics)')
        then 'LG Corporation'
        when contains_substr({{ column_name }}, "l'oreal")
        then "L'OREAL"
        when contains_substr({{ column_name }}, 'unilever')
        then "Unilever PLC"
        when regexp_contains({{ column_name }}, r'(?i)^apple inc')
        then 'Apple Inc.'
        when contains_substr({{ column_name }}, 'glaxo')
        then "GSK PLC"
        when regexp_contains({{ column_name }}, r'(?i)^\W*IGT')
        then 'IGT Global Solutions Corporation'
        when contains_substr({{ column_name }}, "victoria's secret")
        then "Victoria's Secret & Co."
        when contains_substr({{ column_name }}, 'spin master ltd')
        then 'Spin Master Ltd.'
        when contains_substr({{ column_name }}, 'mercedes-benz')
        then 'Mercedes-Benz Group AG'
        when contains_substr({{ column_name }}, 'sherwin-williams')
        then 'The Sherwin-Williams Company'
        when regexp_contains({{ column_name }}, r'(?i)nestl[e|é|É]')
        then 'Nestlé S.A.'
        when contains_substr({{ column_name }}, 'novartis')
        then 'Novartis'
        when contains_substr({{ column_name }}, 'bank of nova scotia')
        then 'The Bank of Nova Scotia'
        when contains_substr({{ column_name }}, 'target brands')
        then 'Target Brands, Inc.'
        when contains_substr({{ column_name }}, 'telus')
        then 'Telus Corporation'
        when contains_substr({{ column_name }}, 'nintendo')
        then 'Nintendo Co., Ltd.'
        when contains_substr({{ column_name }}, 'wal-mart')
        then 'Wal-Mart Stores, Inc.'
        when contains_substr({{ column_name }}, 'canadian imperial bank')
        then 'Canadian Imperial Bank of Commerce'
        when contains_substr({{ column_name }}, 'maple leaf food')
        then 'Maple Leaf Foods Inc.'
        else {{ column_name }}
    end
{% endmacro %}

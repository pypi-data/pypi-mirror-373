from lumaCLI.metadata.sources.powerbi.transform import (
    _extract_dataflow_table_from_expression,
    _extract_table_from_expression,
)


def test__extract_table_from_expression():
    expr = 'let\n    Source = AmazonRedshift.Database("redshift-cluster.someaddr123.eu-west-1.redshift.amazonaws.com","somedb"),\n    sandbox = Source{[Name="finance"]}[Data],\n    kpi_p1 = sandbox{[Name="fi_kpi_p1_table"]}[Data]\nin\n    kpi_p1'
    expected = {
        "name": "fi_kpi_p1_table",
        "schema": "finance",
        "database": "somedb",
    }
    assert _extract_table_from_expression(expr) == expected

    expr2 = 'let\n    Source_Redshift = AmazonRedshift.Database("redshift-cluster.someaddr123.eu-west-1.redshift.amazonaws.com","somedb"),\n    finance = Source_Redshift{[Name="finance"]}[Data],\n    fi_zsd_familt = finance{[Name="fi_zsd_familt"]}[Data],\n    #"Renamed Columns" = Table.RenameColumns(fi_zsd_familt,{{"sub_family_code", "Family Code"}, {"sub_family_desc", "Family"}})\nin\n    #"Renamed Columns"'
    expected2 = {
        "name": "fi_zsd_familt",
        "schema": "finance",
        "database": "somedb",
    }
    assert _extract_table_from_expression(expr2) == expected2

    expr3 = 'let\n    Source_Redshift = AmazonRedshift.Database("redshift-cluster.someaddr123.eu-west-1.redshift.amazonaws.com","somedb"),\n    finance = Source_Redshift{[Name="finance"]}[Data],\n    fi_tcurr = finance{[Name="fi_tcurr"]}[Data],\n    #"Renamed Columns2" = Table.RenameColumns(fi_tcurr,{{"exch_rate_type", "Exch Rate Type"}, {"from_currency", "From Currency"}, {"to_currency", "To Currency"}, {"valid_from", "Valid From"}, {"ratio_from", "Ratio From"}, {"exchange_rate", "Exchange Rate"}, {"ratio_to", "Ratio To"}}),\n    #"Changed Type Valid From" = Table.TransformColumnTypes(#"Renamed Columns2", {{"Valid From", type date}}, "es-ES"),\n    \n    #"Filtered BUDG & M" = Table.SelectRows(#"Changed Type Valid From", each ([Exch Rate Type] = "BUDG" or [Exch Rate Type] = "M") ),\n    #"Filtered From Curr EUR" = Table.SelectRows(#"Filtered BUDG & M", each ([From Currency] = "EUR") ),\n    #"Add Year" = Table.AddColumn(#"Filtered From Curr EUR", "Year", each Date.Year([Valid From])),\n    #"Add Month" = Table.AddColumn(#"Add Year", "Month", each Date.Month([Valid From])),\n    #"Add Day" = Table.AddColumn(#"Add Month", "Day", each Date.Day([Valid From])),\n    #"Changed Data Types" = Table.TransformColumnTypes(#"Add Day",{{"Year", Int64.Type}, {"Month", Int64.Type}, {"Day", Int64.Type}}),\n    #"Filtered Day 1" = Table.SelectRows(#"Changed Data Types", each ([Day] = 1) ),\n    #"Renamed Columns" = Table.RenameColumns(#"Filtered Day 1",{{"Valid From", "EX Date"}}),\n    #"Filtered Rows" = Table.SelectRows(#"Renamed Columns", each [Year] >= 2022)\nin\n    #"Filtered Rows"'
    expected3 = {
        "name": "fi_tcurr",
        "schema": "finance",
        "database": "somedb",
    }
    assert _extract_table_from_expression(expr3) == expected3

    # NativeQuery example - we don't extract models from those, as they're unstructured.
    expr4 = "let\n    Source_Redshift = Value.NativeQuery(AmazonRedshift.Database(\"redshift-cluster.someaddr123.eu-west-1.redshift.amazonaws.com\",\"somedb\"), \"SELECT #(lf)  LOWER(p.model) AS model,#(lf)  s.product_line,#(lf)  s.product_line_detail,#(lf)  SUM(COALESCE(s.placements, 0)) AS total_placements#(lf)FROM finance.fi_part_numbers_for_placements p#(lf)LEFT JOIN (#(lf)  SELECT#(lf)    material,#(lf)    product_line,#(lf)    product_line_detail,#(lf)    COALESCE(SUM(sales_qty), 0) + COALESCE(SUM(actual_qty_reagent_rental), 0) AS placements#(lf)  FROM finance.fi_zsd_sald#(lf)  WHERE fiscal_year BETWEEN EXTRACT(YEAR FROM CURRENT_DATE) - 2 #(lf)                         AND EXTRACT(YEAR FROM CURRENT_DATE) + 1#(lf)    AND sales_org IN (#(lf)      '001', '005', '006', '015', #(lf)      '133', '134', '135', #(lf)      '1693', '175', '176', #(lf)      '193', '1933'#(lf)    )#(lf)  GROUP BY material, product_line, product_line_detail#(lf)) s ON p.material = s.material#(lf)GROUP BY LOWER(p.model), s.product_line, s.product_line_detail#(lf)HAVING SUM(COALESCE(s.placements, 0)) <> 0\", null, [EnableFolding=true])\nin\n    Source_Redshift"
    assert _extract_table_from_expression(expr4) is None


def test__extract_dataflow_table_from_expression():
    expr = 'let\n    Source = SourceNewStrategicDim,\n   Table = Source{[entity="co_sales_org"]}[Data],\n   Text = Table.TransformColumnTypes(Table, List.Transform(Table.ColumnNames(Table),each {_, type text} )),\n    Trim = Table.TransformColumns(Text,List.Transform(Table.ColumnNames(Text), each {_, each Text.Trim(_), type text})),\n    Null =  Table.ReplaceValue(Trim,"",null,Replacer.ReplaceValue,Table.ColumnNames(Trim)),\n    Proper = Table.TransformColumnNames(Null, Text.Proper )\nin\n    Proper'
    expected = {
        "name": "co_sales_org",
        "schema": None,
        "database": None,
    }
    assert _extract_dataflow_table_from_expression(expr) == expected

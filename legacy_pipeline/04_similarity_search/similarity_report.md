# RAG Similarity Search Results
This report maps each sub-problem to the most relevant database schema components based on semantic similarity.

## Sub-Problem: SC00002_SUB_001
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Validate incoming vendor bills against purchase orders

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7328 (Raw Distance: 0.5345)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `Bill_I_N/A_1`) - Cosine Similarity: 0.7185 (Raw Distance: 0.5630)
```text
Schema Name: Bill_I
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component is part of the 'Bill Process' group, designed to compute and process billing information, settling data on a 'Per Lineid Monthly' basis.
        Technical Logic: The 'Bill_I' component aggregates data using 'ForPrdFrom', applies 31 conditions to compute 1 primary component, and settles output 'Per Lineid Monthly' with an output process code of 'TT'.
```

**Match 3:** (ID: `schema_components.csv_205`) - Cosine Similarity: 0.7078 (Raw Distance: 0.5845)
```text
schema_name: PO&IPVsBill\ncomponent_name: Bill\nmodel_id: MATH\ncomponent_type: MATH\ncomponent_type_value: COST\ncomponent_expr: BillQty + BillRate + BillAddlCharge + BillDiscountAmt + BillTaxPercentage + BillBaseValue + BillTaxValue + BillDocumentValue \ncriteria_count: 1
```

---

## Sub-Problem: SC00002_SUB_002
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Extract line item details from the vendor bill

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7900 (Raw Distance: 0.4200)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `Bill_I_N/A_1`) - Cosine Similarity: 0.7700 (Raw Distance: 0.4600)
```text
Schema Name: Bill_I
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component is part of the 'Bill Process' group, designed to compute and process billing information, settling data on a 'Per Lineid Monthly' basis.
        Technical Logic: The 'Bill_I' component aggregates data using 'ForPrdFrom', applies 31 conditions to compute 1 primary component, and settles output 'Per Lineid Monthly' with an output process code of 'TT'.
```

**Match 3:** (ID: `exported_groq_data.csv_201`) - Cosine Similarity: 0.7625 (Raw Distance: 0.4750)
```text
id: PO&IPVsBill_BillDocumentValue_201\ndocument: Schema Name: PO&IPVsBill
        Component Name: BillDocumentValue
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component in the 'PO&IPVsBill' schema that calculates the total cost of a bill item, based on the 'COST' field from another schema, and uses the document number, item ID, and link reference as criteria.
        Technical Logic: The component uses a SUMFROMSCHEMA operation to aggregate the 'COST' field from another schema, and applies criteria based on the document number, item ID, and link reference, which are extracted from the component expression using JSON parsing.\ncomponent_name: BillDocumentValue\nschema_name: PO&IPVsBill
```

---

## Sub-Problem: SC00002_SUB_003
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Match bill quantities with received goods receipts

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7886 (Raw Distance: 0.4228)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `exported_groq_data.csv_205`) - Cosine Similarity: 0.7800 (Raw Distance: 0.4401)
```text
id: PO&IPVsBill_Bill_205\ndocument: Schema Name: PO&IPVsBill
        Component Name: Bill
        Component Type: MATH
        Business Purpose: This row represents a bill component in the PO&IPVsBill schema, used to calculate the total cost of a bill.
        Technical Logic: The component_expr 'BillQty + BillRate + BillAddlCharge + BillDiscountAmt + BillTaxPercentage + BillBaseValue + BillTaxValue + BillDocumentValue' is evaluated to calculate the total cost, which is then used in the model with ID 'MATH' for 1 criteria.\ncomponent_name: Bill\nschema_name: PO&IPVsBill
```

**Match 3:** (ID: `exported_groq_data.csv_177`) - Cosine Similarity: 0.7780 (Raw Distance: 0.4441)
```text
id: PO&IPVsBill_BillRate_177\ndocument: Schema Name: PO&IPVsBill
        Component Name: BillRate
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component named 'BillRate' in the 'PO&IPVsBill' schema, which calculates the total cost of items in the 'Bill_Item' model.
        Technical Logic: The component uses the 'SUMFROMSCHEMA' type to sum the 'COST' value from the schema, filtered by the document number, item ID, and link reference, as specified in the component expression.\ncomponent_name: BillRate\nschema_name: PO&IPVsBill
```

---

## Sub-Problem: SC00002_SUB_004
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Calculate GST on individual bill items

### Top Matching Schema Components:
**Match 1:** (ID: `exported_groq_data.csv_106`) - Cosine Similarity: 0.8241 (Raw Distance: 0.3519)
```text
id: GSTAccBill_I_PValue_106\ndocument: Schema Name: GSTAccBill_I
        Component Name: PValue
        Component Type: MATH
        Business Purpose: This row calculates the GST (Goods and Services Tax) cost as a percentage of the bill base value, using a parameter named 'Parameter1'.
        Technical Logic: The component 'PValue' in the 'GSTAccBill_I' schema uses a mathematical expression to calculate the GST cost, which is then used in the model 'MATH'. The expression '(BillBaseValue * Parameter1)/100' multiplies the bill base value by the parameter value and divides the result by 100 to get the GST cost.\ncomponent_name: PValue\nschema_name: GSTAccBill_I
```

**Match 2:** (ID: `exported_groq_data.csv_114`) - Cosine Similarity: 0.8196 (Raw Distance: 0.3609)
```text
id: ExpAccBill_I_GST_NValue_114\ndocument: Schema Name: ExpAccBill_I_GST
        Component Name: NValue
        Component Type: MATH
        Business Purpose: This row calculates the GST (Goods and Services Tax) cost by subtracting 1% of the BillBaseValue multiplied by Parameter1.
        Technical Logic: The component_expr '-(BillBaseValue * Parameter1)/100' is a mathematical expression that calculates the GST cost. It multiplies the BillBaseValue by Parameter1, then subtracts 1% of the result, effectively calculating the GST cost.\ncomponent_name: NValue\nschema_name: ExpAccBill_I_GST
```

**Match 3:** (ID: `enriched_exported_groq_data.csv_106`) - Cosine Similarity: 0.8077 (Raw Distance: 0.3846)
```text
id: GSTAccBill_I_PValue_106\ndocument: Schema Name: GSTAccBill_I
        Component Name: PValue
        Component Type: MATH
        Business Purpose: This row calculates the GST (Goods and Services Tax) cost as a percentage of the bill base value, using a parameter named 'Parameter1'.
        Technical Logic: The component 'PValue' in the 'GSTAccBill_I' schema uses a mathematical expression to calculate the GST cost, which is then used in the model 'MATH'. The expression '(BillBaseValue * Parameter1)/100' multiplies the bill base value by the parameter value and divides the result by 100 to get the GST cost.\ncomponent_name: PValue\nschema_name: GSTAccBill_I\npurpose: This row calculates the GST (Goods and Services Tax) cost as a percentage of the bill base value.\ntechnical_logic: The component 'PValue' in the 'GSTAccBill_I' schema uses a mathematical expression to calculate the GST cost, multiplying the bill base value by the parameter value and dividing the result by 100.
```

---

## Sub-Problem: SC00002_SUB_005
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Determine applicable TDS rates for vendor bills

### Top Matching Schema Components:
**Match 1:** (ID: `enriched_exported_groq_data.csv_124`) - Cosine Similarity: 0.7749 (Raw Distance: 0.4501)
```text
id: TDSAccBill_I_Value1_124\ndocument: Schema Name: TDSAccBill_I
        Component Name: Value1
        Component Type: MATH
        Business Purpose: This row calculates the TDS (Tax Deducted at Source) on a bill by multiplying the base value with the TDS rate and dividing by 100.
        Technical Logic: The component_expr 'AccBaseValue*TDSRate/100' is evaluated to calculate the TDS amount, where AccBaseValue is the base value and TDSRate is the TDS rate.\ncomponent_name: Value1\nschema_name: TDSAccBill_I\npurpose: This row calculates the TDS (Tax Deducted at Source) on a bill.\ntechnical_logic: The component evaluates the expression 'AccBaseValue*TDSRate/100' to calculate the TDS amount.
```

**Match 2:** (ID: `exported_groq_data.csv_124`) - Cosine Similarity: 0.7730 (Raw Distance: 0.4540)
```text
id: TDSAccBill_I_Value1_124\ndocument: Schema Name: TDSAccBill_I
        Component Name: Value1
        Component Type: MATH
        Business Purpose: This row calculates the TDS (Tax Deducted at Source) on a bill by multiplying the base value with the TDS rate and dividing by 100.
        Technical Logic: The component_expr 'AccBaseValue*TDSRate/100' is evaluated to calculate the TDS amount, where AccBaseValue is the base value and TDSRate is the TDS rate.\ncomponent_name: Value1\nschema_name: TDSAccBill_I
```

**Match 3:** (ID: `schema_classes.csv_22`) - Cosine Similarity: 0.7692 (Raw Distance: 0.4617)
```text
schema_name: TDSAccBill_I\nsource_schema: SC00002\nschema_group_name: Bill Process\ndata_source: Bill_I\ndate_aggregation_on: ForPrdFrom\nsettlement_type: Per SectionName Monthly\noutput_process_code: TT\ncomponent_count: 11\ncondition_count: 15\nhas_getgroupfromschema2: False\nnl_summary: Aggregates and allocates 11 components from Bill_I data source, settling Per SectionName Monthly and feeds 2 downstream classes. Performs arithmetic transformations across 15 field conditions.
```

---

## Sub-Problem: SC00002_SUB_006
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Allocate costs to specific cost centers based on purchase order details

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7351 (Raw Distance: 0.5297)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `exported_groq_data.csv_205`) - Cosine Similarity: 0.7260 (Raw Distance: 0.5480)
```text
id: PO&IPVsBill_Bill_205\ndocument: Schema Name: PO&IPVsBill
        Component Name: Bill
        Component Type: MATH
        Business Purpose: This row represents a bill component in the PO&IPVsBill schema, used to calculate the total cost of a bill.
        Technical Logic: The component_expr 'BillQty + BillRate + BillAddlCharge + BillDiscountAmt + BillTaxPercentage + BillBaseValue + BillTaxValue + BillDocumentValue' is evaluated to calculate the total cost, which is then used in the model with ID 'MATH' for 1 criteria.\ncomponent_name: Bill\nschema_name: PO&IPVsBill
```

**Match 3:** (ID: `schema_classes.csv_22`) - Cosine Similarity: 0.7233 (Raw Distance: 0.5534)
```text
schema_name: TDSAccBill_I\nsource_schema: SC00002\nschema_group_name: Bill Process\ndata_source: Bill_I\ndate_aggregation_on: ForPrdFrom\nsettlement_type: Per SectionName Monthly\noutput_process_code: TT\ncomponent_count: 11\ncondition_count: 15\nhas_getgroupfromschema2: False\nnl_summary: Aggregates and allocates 11 components from Bill_I data source, settling Per SectionName Monthly and feeds 2 downstream classes. Performs arithmetic transformations across 15 field conditions.
```

---

## Sub-Problem: SC00002_SUB_007
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Assign business units to vendor bills for cost tracking purposes

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7798 (Raw Distance: 0.4405)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `Bill_I_N/A_1`) - Cosine Similarity: 0.7586 (Raw Distance: 0.4829)
```text
Schema Name: Bill_I
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component is part of the 'Bill Process' group, designed to compute and process billing information, settling data on a 'Per Lineid Monthly' basis.
        Technical Logic: The 'Bill_I' component aggregates data using 'ForPrdFrom', applies 31 conditions to compute 1 primary component, and settles output 'Per Lineid Monthly' with an output process code of 'TT'.
```

**Match 3:** (ID: `exported_groq_data.csv_177`) - Cosine Similarity: 0.7509 (Raw Distance: 0.4982)
```text
id: PO&IPVsBill_BillRate_177\ndocument: Schema Name: PO&IPVsBill
        Component Name: BillRate
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component named 'BillRate' in the 'PO&IPVsBill' schema, which calculates the total cost of items in the 'Bill_Item' model.
        Technical Logic: The component uses the 'SUMFROMSCHEMA' type to sum the 'COST' value from the schema, filtered by the document number, item ID, and link reference, as specified in the component expression.\ncomponent_name: BillRate\nschema_name: PO&IPVsBill
```

---

## Sub-Problem: SC00002_SUB_008
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Create accounting journal entries for bill payments and taxes

### Top Matching Schema Components:
**Match 1:** (ID: `exported_groq_data.csv_156`) - Cosine Similarity: 0.7729 (Raw Distance: 0.4542)
```text
id: BillCostAllocation_BillAmountinLocalCurrency_156\ndocument: Schema Name: BillCostAllocation
        Component Name: BillAmountinLocalCurrency
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component in the 'BillCostAllocation' schema that calculates the total cost of an accounting journal entry, specifically the 'BillAmountinLocalCurrency' component, which sums up the costs based on the 'COST' type.
        Technical Logic: The component_expr field uses a JSON object to filter the data, selecting records where the 'documentnumber', 'AccountType', 'ForPrdFrom', 'ForPrdTo', 'linkref', 'CostAllocationMethod', and 'lineref' fields match the specified values. The SUMFROMSCHEMA component_type is then used to calculate the sum of the 'COST' type, resulting in the total cost of the accounting journal entry.\ncomponent_name: BillAmountinLocalCurrency\nschema_name: BillCostAllocation
```

**Match 2:** (ID: `enriched_exported_groq_data.csv_156`) - Cosine Similarity: 0.7727 (Raw Distance: 0.4546)
```text
id: BillCostAllocation_BillAmountinLocalCurrency_156\ndocument: Schema Name: BillCostAllocation
        Component Name: BillAmountinLocalCurrency
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component in the 'BillCostAllocation' schema that calculates the total cost of an accounting journal entry, specifically the 'BillAmountinLocalCurrency' component, which sums up the costs based on the 'COST' type.
        Technical Logic: The component_expr field uses a JSON object to filter the data, selecting records where the 'documentnumber', 'AccountType', 'ForPrdFrom', 'ForPrdTo', 'linkref', 'CostAllocationMethod', and 'lineref' fields match the specified values. The SUMFROMSCHEMA component_type is then used to calculate the sum of the 'COST' type, resulting in the total cost of the accounting journal entry.\ncomponent_name: BillAmountinLocalCurrency\nschema_name: BillCostAllocation\npurpose: This component calculates the total cost of an accounting journal entry.\ntechnical_logic: It uses a JSON object to filter data based on specified fields and then calculates the sum of the 'COST' type using the SUMFROMSCHEMA component type.
```

**Match 3:** (ID: `exported_groq_data.csv_177`) - Cosine Similarity: 0.7641 (Raw Distance: 0.4718)
```text
id: PO&IPVsBill_BillRate_177\ndocument: Schema Name: PO&IPVsBill
        Component Name: BillRate
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component named 'BillRate' in the 'PO&IPVsBill' schema, which calculates the total cost of items in the 'Bill_Item' model.
        Technical Logic: The component uses the 'SUMFROMSCHEMA' type to sum the 'COST' value from the schema, filtered by the document number, item ID, and link reference, as specified in the component expression.\ncomponent_name: BillRate\nschema_name: PO&IPVsBill
```

---

## Sub-Problem: SC00002_SUB_009
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Settle bills across multiple dimensions including line of business and vendor

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7919 (Raw Distance: 0.4161)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `Bill_I_N/A_1`) - Cosine Similarity: 0.7729 (Raw Distance: 0.4542)
```text
Schema Name: Bill_I
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component is part of the 'Bill Process' group, designed to compute and process billing information, settling data on a 'Per Lineid Monthly' basis.
        Technical Logic: The 'Bill_I' component aggregates data using 'ForPrdFrom', applies 31 conditions to compute 1 primary component, and settles output 'Per Lineid Monthly' with an output process code of 'TT'.
```

**Match 3:** (ID: `BillCostAllocation_N/A_28`) - Cosine Similarity: 0.7676 (Raw Distance: 0.4648)
```text
Schema Name: BillCostAllocation
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component aggregates and allocates 7 components from the Bill_I data source, settling on a Per LOB Monthly basis.
        Technical Logic: This component performs arithmetic transformations across 10 field conditions, aggregating data from the Bill_I data source and settling on a Per LOB Monthly basis.
```

---

## Sub-Problem: SC00002_SUB_010
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Track workflow status of vendor bills from receipt to payment

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7267 (Raw Distance: 0.5465)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `Bill_I_N/A_1`) - Cosine Similarity: 0.7194 (Raw Distance: 0.5612)
```text
Schema Name: Bill_I
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component is part of the 'Bill Process' group, designed to compute and process billing information, settling data on a 'Per Lineid Monthly' basis.
        Technical Logic: The 'Bill_I' component aggregates data using 'ForPrdFrom', applies 31 conditions to compute 1 primary component, and settles output 'Per Lineid Monthly' with an output process code of 'TT'.
```

**Match 3:** (ID: `Bill_H_N/A_2`) - Cosine Similarity: 0.7182 (Raw Distance: 0.5637)
```text
Schema Name: Bill_H
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes billing data from the 'Bill_H' data source, computing specific components settled on a 'Per interimid Monthly' basis.
        Technical Logic: The system processes data from the 'Bill_H' data source, aggregating information based on 'documentdate', computing 3 components by applying 25 field conditions with arithmetic transformations, and generates output with process code 'TT'.
```

---

## Sub-Problem: SC00002_SUB_011
**Statement:**
Project Name: Bill Processing System
Sub-Problem: Reconcile bills with purchase orders and goods receipts to ensure accuracy

### Top Matching Schema Components:
**Match 1:** (ID: `Bill_Item_N/A_5`) - Cosine Similarity: 0.7873 (Raw Distance: 0.4254)
```text
Schema Name: Bill_Item
        Component Name: N/A
        Component Type: N/A
        Business Purpose: This component processes individual bill items, aggregating and allocating data from a source system to support the overall billing process.
        Technical Logic: The Bill_Item component processes 25 distinct data components sourced from 'Bill_I' (internal source SC00002). Data aggregation is performed based on 'ForPrdFrom' and settled 'Per Lineid Monthly'. It applies 31 field conditions for arithmetic transformations, outputting via process code 'TT' to downstream consumers.
```

**Match 2:** (ID: `exported_groq_data.csv_205`) - Cosine Similarity: 0.7570 (Raw Distance: 0.4860)
```text
id: PO&IPVsBill_Bill_205\ndocument: Schema Name: PO&IPVsBill
        Component Name: Bill
        Component Type: MATH
        Business Purpose: This row represents a bill component in the PO&IPVsBill schema, used to calculate the total cost of a bill.
        Technical Logic: The component_expr 'BillQty + BillRate + BillAddlCharge + BillDiscountAmt + BillTaxPercentage + BillBaseValue + BillTaxValue + BillDocumentValue' is evaluated to calculate the total cost, which is then used in the model with ID 'MATH' for 1 criteria.\ncomponent_name: Bill\nschema_name: PO&IPVsBill
```

**Match 3:** (ID: `exported_groq_data.csv_177`) - Cosine Similarity: 0.7568 (Raw Distance: 0.4863)
```text
id: PO&IPVsBill_BillRate_177\ndocument: Schema Name: PO&IPVsBill
        Component Name: BillRate
        Component Type: SUMFROMSCHEMA
        Business Purpose: This row defines a component named 'BillRate' in the 'PO&IPVsBill' schema, which calculates the total cost of items in the 'Bill_Item' model.
        Technical Logic: The component uses the 'SUMFROMSCHEMA' type to sum the 'COST' value from the schema, filtered by the document number, item ID, and link reference, as specified in the component expression.\ncomponent_name: BillRate\nschema_name: PO&IPVsBill
```

---

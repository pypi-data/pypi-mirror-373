# Relative valuation

Classic and commonly used relative ratios PE, PEG, PS, PFCF, EV-EBITDA
Additional comparative metrics: growth (EPS, Sales, FCF), EV, Market Cap

## Filters

A set of filter is available:
1. **Output**: Chart, Table (Last Value), Table (Time-series)
    - **Chart [default view]**: By default shows all ratios for the instrument in question in one figure with PEG on a secondary/right axis.
    - **Table (Last Value)**: By default shows the last available  value for all ratios for the instrument in question in one table.
    - **Table (Time-series)**: Shows all available values for all ratios for the instrument in question in one table.

2. **Period**: Common periods (TTM, FTW, FY+1, FY+2) are available with **FTW** set by default.

3. **Versus related (not available in the Time-series view):**
    - if the view "**Table (Last Value)**" is set, then all available related instruments (peers, partners, suppliers, etc.) will be shown in the same table, including Mean and Median values.
    - if the view "**Chart**" is set, then all available related instruments (peers, partners, suppliers, etc.) will be shown in the same chart. Additionally, the user may choose which variables to show on X,Y,and Bubble Size axis. Median line may be disactivated, if desired.

4. **Draw ranges**: if the view "**Chart**" is set, then each ratio will be shown on a separate subplot with historic min-max ranges shown with dashed lines.

5. **Range type**: if the view "**Chart**" is set and "**Draw ranges**" is activated, then a user may choose the type of "min-max" range: Min-Max (entire period) or Rolling.
    - **"Min-Max (entire period)"** looks for the min and max values for each ratio across the entire period in questions and sets it for the entire graph.
    - **"Rolling"** looks for the min and max values for each ratio across the "Rolling Period" specified in a separate filter.

6. **Rolling period**: works with "**Range type**" filter if the view "**Chart**" is set and "**Draw ranges**" is activated.

7. **Clean data** (more "treatment"): significant and heavy data cleaning will be applied to all variables. For **each** series:
    - All raw input data is forward and then backward filled.
    - All empty rows are deleted and remaining blanks for all variables are filled by linear interpolation.
    - Ratios are then normally calculated.
    - The resulting series are cleaned for outliers (values in the top and bottom 5% are deleted).
    - All negative (incl. EV/S) and NaN values are set to Null (deleted as "non-meaningful").
    - All values above a certain threshold (by default 100) are deleted. **Exceptions** are:
        - PEG above 15
        - PS above 40
    - The remaining series are forward and backward filled to clean missing values for smoother series.
    - All series are smoothed (3-day simple moving average). The **PEG** series is smoothed differently (10-day simple moving average).

8. **X-Axis**: works if the view "**Chart**" is set and "**Versus related**" is activated. Controls the variable shown on the x-axis.

9. **Y-Axis**: works if the view "**Chart**" is set and "**Versus related**" is activated. Controls the variable shown on the y-axis.

10. **Z-Axis (bubble size)**: works if the view "**Chart**" is set and "**Versus related**" is activated. Controls the variable shown on the z-axis/bubble size.

11. **Median**: works if the view "**Chart**" is set and "**Versus related**" is activated. Calculates the median for **X-Axis** and **Y-Axis** variables across the entire period range.

## Formulas

#### FY+1 and FY+2

$$
Ratio_{t} = Price_{t} / Ratio\: Item_{t}
$$

$
where \\
$
$$
t    =  day \\
$$
$
Ratio\: Item =
$
$$
EPS = Daily\: Consensus\: Net\: Profit\: Forecast / Number\:of\:shares\\
or \\
Revenue\: per\: share = Daily\: Consensus\: Revenue\: Forecast / Number\:of\:shares\\
or \\
EBITDA\: per\: share = Daily\: Consensus\: EBITDA\; Forecast / Number\:of\:shares\\
or \\
FCF = Daily\: Consensus\: FreeCashFlow\; Forecast / Number\:of\:shares\\
$$

#### Trailing Twelve Month (TTM) and Next Twelve Month (NTM) *also known as Forward Twelve Months (FTM)*
\
$
Ratio\: Item =
$
$$
EPS = Daily\: EPS\: TTM\: \\
or \\
Revenue\: or\: EBITDA\: or\: FCF\: per\: share = Interpolated\: between\: consensus\: FY+2\:,\: FY+1 \\
Revenue\: or\: EBITDA\: or\: FCF\:per\: share =Interpolated\: between\: FY+1\:(current)\:,\: FY0\:(last)\:,\: FY-1\:(previous) \\
$$

#### Trailing Twelve Month (TTM) and Next Twelve Month (NTM) *also known as Forward Twelve Months (FTM)*
\
$
DailyPEG_{fy+1} = Price / EPS_{fy+1} / Growth_{fy+1\: vs\: fy0} \\
DailyPEG_{fy+2} = Price / EPS_{fy+2} / Growth_{geoavg(fy+2\: vs\: fy1,\:fy+1\: vs\: fy0)} \\
DailyPEG_{NTM} = Price / EPS_{NTM} / Growth_{ntm\: vs\: ttm} \\
DailyPEG_{TTM} = Price / EPS_{TTM} / Growth_{ttm\: vs\: ttm_{t-1}} \\
$

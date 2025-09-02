# Aggregate AssetPosition Liquidity Table View

The purpose of this view is to observe how fast an aggregated asset position
can be sold across all portfolios. We have two columns for two different dates.
One column shows the velocity and the other one shows the relative percent of
the total AuM (Asset under Management), "Days to Liquidate" and "Percent AUM"
respectively.

Some good things to know:

- We use the mean volume for the last 50 days.

- One third of the average volume for an asset position is
  used to estimate the velocity. This number is subjective and attempts
  to represent the number of trades that can be made.

- If we have a value for more than 3 days to sell an asset position,
  the latter will be displayed in yellow. If this value is greater than 5,
  it will be in red.

- We can use a filter that only displays asset positions that have a date
  to liquidate greater than a given value for the Historic Date.

- The "Compared Date" is used to compare the asset position with the Historic Date.
Therefore, the values are not sorted for the last two columns.

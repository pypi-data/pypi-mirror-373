# Financial Statistics

Here is a list of different financial statistics that can help to evaluate performance and risk of an instrument against
his benchmark.

### Meaning:
1. Mean Return: it is the average of all the returns during the period.
2. Volatility: it is a statistical measure of the dispersion of returns.
3. Maximum Drawdown: a drawdown is the return between the current price and the last highest price. If the current price
   is the last highest price, the drawdown is 0. Therefore, drawdowns are only negative values. The maximum drawdown
   (MDD) is the biggest fall in terms of return.
4. Longest Drawdown Period: the longest number of days to recover his last highest price.
5. Last cumulative return: a cumulative return on an investment is the aggregate amount that the investment has gained
   or lost over time, independent of the amount of time involved. The last cumulative return is the return between the
   first price and last price over the period.
6. Value at Risk: the Value at Risk (VaR) is a downside risk measure. The idea is to keep the worst returns which are
   lower than a specific return based on a quantile (default value is 5%). Once we have these worst returns, the VaR is
   the highest one (so the "least bad"). The quantile number for the VaR is called alpha in finance. This process is the
   historical VaR approach.
7. Conditional Value at Risk: The CVaR is a downside risk measure. It is the same process as the VaR, however it is the
   mean of the worst returns. The CVaR is an absolute value (always positive).
8. Skewness: in statistics, skewness is the degree of asymmetry observed in a probability function. For instance,
   negative skewness occurs when the returns to the left of (less than) the mean are fewer but farther from it than
   returns to the right of (greater than) the mean.
9. Excess Kurtosis: Like Skewness, Kurtosis is a statistical measure that is used to describe distribution. Whereas
   skewness differentiates extreme values in one versus the other tail, kurtosis measures extreme values in either tail.
   For instance, a higher kurtosis means that there are more extreme returns (positive and negative).
10. Compound Annual Growth Rate: The CAGR is a rate of return that would be required for an investment to grow from its
    beginning balance to its ending balance, assuming the profits were reinvested at the end of each year of the
    investment’s life span.
11. Sortino Ratio: it is a downside risk ratio. In finance, the most important risk is not volatility, but rather the
    risk of not achieving the return in relation to an investment goal. Here it is not the same formula as investopedia,
    so it is not the Sortino Ratio as everybody know. Here we use the target level instead of the risk free rate (it is
    mostly the same thing). To calculate the Sortino Ratio, first we need only the returns that are below the target
    level (default value is 0). Then, we take those returns, square them, sum them, divide by the total number of
    returns (not only those who are below the target level) and finally square root them. This is what we call the
    « below-target semi-deviation ». Calculate the annualized return and also annualized the below-target
    semi-deviation. Take the annualized return, soustract by the target level and finally divide by the annualized
    below-target semi-deviation.
12. Adjusted Sortino Ratio: it is just the Sortino Ratio divided by square root of 2.
13. Calmar Ratio: it is the CAGR divided by the MDD.
14. Sterling Ratio: it is the annualized returns soustracted by the risk free rate, divided by the MDD.
15. Burke Ratio: it is the annualized returns soustracted by the risk free rate, divided by the square root of the sum
    of the square of the drawdowns.

# Dashboard Explainer

Reference doc for explaining the dashboard in interviews or presentations.

---

## Current State — Two KPI Rows

The Current State section has two rows, each a different lens on the same market.

**Space Market** shows what is physically happening: how much space is empty, whether tenants are taking or giving back space. This is ground-truth leasing data that does not exist in any public API — it comes from industry MarketBeat reports.

**Financial Signals** shows how investors and lenders are reacting to the space market. REIT prices reflect what investors think buildings are worth. Rates and delinquency show whether the debt market is healthy or stressed.

The two rows are one story. The Space Market row is the cause — vacancy and absorption drive everything else. The Financial Signals row is the effect — investor prices and loan stress are reactions to what is happening with tenants and occupancy.

---

### Space Market KPI Row

*Office Vacancy · Industrial Vacancy · Office YTD Absorption · Industrial YTD Absorption*
*Source: Cushman & Wakefield MarketBeat · Office Q2 2025 · Industrial Q3 2025*

**Vacancy** tells you how much space is empty. **Absorption** tells you whether the market is getting better or worse — negative means tenants gave back more space than they took. "12 consecutive quarters negative" means three full years of deterioration with no bottom yet.

The gap between 24.1% office vacancy and 4.8% industrial vacancy is the central story of the whole dashboard in two numbers. A leasing broker uses vacancy to set expectations with landlord clients: you are not in a recovery, you are still in freefall relative to tenants. A capital markets broker uses it to underwrite income — high vacancy means lower rent revenue means lower building value.

---

### Financial Signals KPI Row

*Office REIT Price · Industrial REIT Price · Fed Funds Rate · CRE Loan Delinquency*
*Source: yfinance · FRED via Snowflake*

**Office and Industrial REIT prices** are the fastest signal of what investors think buildings are worth right now — they update daily, months before private sale transactions close. When office REIT prices fall, investors are losing confidence in office properties before that shows up in deal data.

**The fed funds rate** is how expensive it is to borrow money right now. Higher rates mean financing a deal costs more, which shrinks the buyer pool and pushes property values down.

**The CRE delinquency rate** tells you how many existing property owners cannot pay their loans — high delinquency means more distressed sellers coming to market.

A broker walking into a client meeting wants to know: what are prices doing, what does borrowing cost, and how many owners are in trouble? These four numbers answer all three questions in one look.

---

## Market Fundamentals — Submarket Breakdown

*Source: Cushman & Wakefield MarketBeat · Office Q2 2025 · Industrial Q3 2025*

The total market vacancy number is the headline, but a leasing broker works in submarkets. 24.1% overall office vacancy means nothing if you are advising a tenant looking in LA West (24%) versus San Gabriel Valley (7.1%) — those are completely different negotiating environments.

The submarket table is the translation layer between the macro story and a specific deal. High vacancy and negative absorption in a submarket means landlord desperation — tenants have leverage to negotiate free rent, tenant improvement allowances, and below-market rents. Low vacancy and positive absorption means the opposite. For industrial, LA West at 2.7% vacancy with a $2.38 asking rent versus LA South at 6.3% and $1.46 tells a tenant exactly where pricing power sits before they even tour a building.

---

## Investor Signals

---

### Chart 1 — REIT Price Trend by Sector

*Office and industrial REIT prices indexed to 100 from 2019. Filtered by Start Year slider.*

Both sectors start equal in 2019. Industrial climbed to roughly double or triple while office fell to half to two-thirds of its starting value. The indexed format removes the noise of different stock prices and shows the relative confidence divergence — the gap opening up is the whole story.

**For a capital markets broker:** The chart shows exactly when office started losing investor confidence and whether it has started to reverse — which is what determines whether now is the right moment to list a property or wait.

**For a leasing broker:** The chart explains negotiating dynamics in plain terms. Office landlords have watched the value of their buildings fall 30-40% while industrial landlords have seen theirs nearly triple. An office landlord needs tenants to service debt on an underwater asset — that is why they offer months of free rent and large tenant improvement allowances. An industrial landlord has the leverage — that is why industrial lease terms are tighter and rents are still rising.

---

### Chart 6 — CRE Loan Delinquency Rate (2008–present)

*Percentage of CRE bank loans 30+ days past due. Source: FRED (DRCRELEXFACBS)*

This chart exists to answer one question a client always asks: is this 2008? The answer is no. Current delinquency is around 1.8% — roughly one-fifth of the 8.7% peak in 2010. In 2008 the entire lending system seized. Today banks are stressed but functional. That distinction matters enormously for deal-making.

**For a capital markets broker:** Rising delinquency means two things at once — distressed sellers who need to exit fast, creating deal flow, and tighter lending standards that make it harder for buyers to get financing. Knowing where we are relative to 2008 tells a broker whether to be aggressive or cautious in advising clients on timing. "Distressed but not systemic" is a very different conversation than "the market is frozen."

**For a leasing broker:** Delinquency rises because vacancy rises. When offices empty out, owners lose rent and cannot service their debt. This chart confirms that the vacancy problem is severe enough to reach the lending market — which means the distressed landlords offering aggressive lease deals are not outliers, they are the norm.

---

### Chart 2 — Rising Rates Crushed Office Valuations

*Office REIT indexed price vs. Fed Funds Rate on dual axes. Filtered by Start Year slider.*

This chart shows the mechanism behind the office crash. Rates went from near zero to 5.3% in 18 months — the fastest hiking cycle in 40 years. Office prices fell in lockstep.

The reason rates matter so much: commercial real estate is almost always financed with debt. When borrowing gets more expensive, two things happen. First, buyers can afford to pay less for a building because their debt payments are higher. Second, existing owners who need to refinance face dramatically higher costs, putting their buildings under financial stress.

**For a capital markets broker:** This chart separates two explanations for the office crash — a rate problem, which is temporary and fixable when cuts arrive, versus a structural problem from remote work permanently reducing demand. The chart shows rates clearly drove the 2022-2023 crash. But if rates are falling and office is still struggling, the problem is becoming structural. That changes the investment thesis entirely — you are no longer waiting for a rate cut to unlock value, you are waiting for a demand recovery that may take years.

**For a leasing broker:** Knowing why values crashed tells you how motivated landlords are. A landlord who bought at 2021 valuations using 2021 debt is now underwater on both the asset value and the refinancing cost. That landlord signs whatever lease it takes to generate cash flow.

---

### Chart 5 — Why Industrial Held Up

*E-commerce as % of retail sales (4-quarter average) vs. industrial REIT indexed price. Source: FRED (ECOMPCTNSA) · yfinance*

Industrial did not just survive the rate hike cycle — it actively grew. This chart explains why. As e-commerce became a larger share of all retail sales, the economy permanently needed more warehouse and logistics space. The demand driver is structural, not cyclical — it does not go away when the economy slows down because people do not stop shopping online during a downturn.

**For a leasing broker:** This explains why industrial lease negotiations work differently from office. Industrial landlords are not desperate. Rents have risen dramatically over the past five years and while they have softened slightly from the peak, they are still well above pre-COVID levels. A tenant signing an industrial lease today is paying a rent that reflects a permanently higher demand baseline — not a temporary spike.

**For a capital markets broker:** Industrial assets have held value through a rate cycle that destroyed office values. That resilience is evidence of durable income — the underwriting assumption of continued occupancy is supported by a structural demand driver, not just recent history.

---

## Outlook

---

### Chart 4 — LA Employment vs. Peer Cities

*Employment in office-using sectors indexed to 100 from 2020. Metro selector interactive.*

This chart tracks employment in financial services and professional services — the two industries that primarily lease office space. Companies hire people first, then sign leases six to eighteen months later. By the time vacancy rates and leasing volume move, the employment trend has already played out. This chart shows you what is coming before it shows up in the data JLL's own brokers are watching.

The story: Dallas is up significantly from its 2020 baseline — Sun Belt job growth in office-using sectors is real and sustained. LA is among the weakest of the major metros, having never fully recovered its office-using employment base.

**For a capital markets broker:** LA employment lagging Dallas and New York means the office demand recovery in LA will be slower. If a client is allocating capital between markets, employment trends in office-using sectors are the forward-looking argument for or against each city.

**For a leasing broker:** Office leasing recovers when employers start growing their headcount again. This chart says that is not happening in LA relative to peers. Do not advise landlord clients to hold out for higher rents — the tenant demand driver is not there yet.

**For a JLL BI Analyst:** Walking into a client meeting with a leading indicator that moves before the leasing data does is the difference between a transactional broker and a strategic advisor. This chart positions JLL as having intelligence the client does not, which is the core value proposition of the BI function.

---

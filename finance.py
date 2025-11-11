import numpy as np
import numpy_financial as npf
import pandas as pd

def lcoe(capex, opex_annual, energy_annual_mwh, years=25, discount=0.08):
    cash_costs = [capex] + [opex_annual]*(years)
    energy = [0] + [energy_annual_mwh]*(years)  # año 0 sin energía
    # Valor presente de costes y energía
    pvc = sum(c / ((1+discount)**t) for t, c in enumerate(cash_costs))
    pve = sum(e / ((1+discount)**t) for t, e in enumerate(energy))
    return pvc / max(pve, 1e-6)

def irr_from_cashflows(capex, cashflows_years):
    return float(npf.irr([-capex] + cashflows_years))

def payback_year(capex, cashflows_years):
    cum = 0.0
    for i, cf in enumerate(cashflows_years, start=1):
        cum += cf
        if cum >= capex:
            return i
    return None

def quick_scenarios(capex, opex, tariff_usd_mwh, energy_mwh, years=25):
    # cashflow simple: ingresos - opex
    revenue = tariff_usd_mwh * energy_mwh
    cf = [revenue - opex] * years
    irr = irr_from_cashflows(capex, cf)
    lcoe_val = lcoe(capex, opex, energy_mwh, years)
    return {"IRR": irr, "LCOE": lcoe_val, "AnnualCashflow": revenue - opex}

def sensitivity_tariff(capex, opex, energy_mwh, tariffs):
    rows = []
    for t in tariffs:
        res = quick_scenarios(capex, opex, t, energy_mwh)
        rows.append({"Tariff": t, "IRR": res["IRR"], "AnnualCF": res["AnnualCashflow"]})
    return pd.DataFrame(rows)

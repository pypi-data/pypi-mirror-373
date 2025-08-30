import pandas as pd
from datetime import datetime
from collections import defaultdict
import statistics as stats
from datetime import timedelta
import statistics as stats
import numpy as np

now = datetime.today()
CURRENT_YEAR = now.strftime("%Y")

# Greenblatt Magic Formula number 
def greenblatt_formula(df): 
    
    df = df.copy()
    
    # Mask för rader där PE och ROE är varken None eller 0
    valid_mask = (
        df[f"PE {CURRENT_YEAR}"].notna() & 
        df["ROCE"].notna() &
        (df[f"PE {CURRENT_YEAR}"] != 0) & 
        (df["ROCE"] != 0)
    )

    # Initiera kolumn med None
    df["Greenblatt Formula"] = None

    # Rangordna bara giltiga rader
    PE_rank = df.loc[valid_mask, f"PE {CURRENT_YEAR}"].rank(ascending=True, method="min")
    ROE_rank = df.loc[valid_mask, "ROE"].rank(ascending=False, method="min")

    # Summera rank och skriv in i nya kolumnen för giltiga rader
    for idx in PE_rank.index:
        df.at[idx, "Greenblatt Formula"] = PE_rank[idx] + ROE_rank[idx]

    return df

# standardavvikelsen av monethly return de senaste 36 månaderna 
# rank in ascending order 
def volatility(price_data):
    if len(price_data) < 38:  # Behöver minst 38 dagars data för 36 månaders tillväxt
        return None, [], []

    try:
        for d in price_data:
            if isinstance(d['date'], str):
                d['date'] = datetime.strptime(d['date'], '%Y-%m-%d')

        price_data.sort(key=lambda x: x['date'])

        monthly_data = defaultdict(list)
        for entry in price_data:
            key = (entry['date'].year, entry['date'].month)
            monthly_data[key].append(entry)

        last_day_adj_closes = [entries[-1]['adjusted_close'] for key, entries in sorted(monthly_data.items())]
        last_36_adj_closes = last_day_adj_closes[-38:]

        if len(last_36_adj_closes) < 14:
            return None, [], []

        monthly_growths = []
        for idx in range(1, len(last_36_adj_closes)-1):
            growth = last_36_adj_closes[idx+1] / last_36_adj_closes[idx] - 1
            monthly_growths.append(growth)

        std = stats.stdev(monthly_growths)
        return std, last_36_adj_closes, monthly_growths

    except Exception:
        return None, [], []

# NPY - formel från artikeln "formula investing"
def NPY(closing_prices, data, price_data): 
    def find_adjusted_close_on_or_after(date, stock_prices):
        # Convert to set of available dates for faster lookup
        available_dates = {entry['date'].date(): entry['adjusted_close'] for entry in stock_prices}
        
        # Start at the given date and move forward until found
        while date.date() not in available_dates:
            date += timedelta(days=1)
        
        return available_dates[date.date()]
   
    N = len(closing_prices)
    R = closing_prices[N-1] / closing_prices[N-13] - 1
    inc_data = data.get("Financials", {}).get("Balance_Sheet", {}).get("yearly", {})
    
    sorted_Years = sorted(inc_data.items(), reverse=True)[0:2]

    latest_year = sorted_Years[0][1].get("commonStockSharesOutstanding")
    date_last_year= datetime.strptime(sorted_Years[0][1].get("date"), '%Y-%m-%d') 

    second_latest_year = sorted_Years[1][1].get("commonStockSharesOutstanding")
    date_second_last_year= datetime.strptime(sorted_Years[1][1].get("date"), '%Y-%m-%d') 

    price_last_year = find_adjusted_close_on_or_after(date_last_year, price_data)
    price_second_last_year = find_adjusted_close_on_or_after(date_second_last_year, price_data)
    
    mc_last_year = price_last_year * float(latest_year)
    mc_second_last_year = price_second_last_year * float(second_latest_year)

    delta = mc_last_year / mc_second_last_year

    NPY = R - stats.log(delta)
    
    return NPY 

# Momentum: komulativ produkt av pristillväxt de senaste elva månaderna
def momentum(monthly_growths): 
    c_growth = 1 
    for m_growth in monthly_growths[-12:-1]: 
        c_growth = c_growth * (m_growth + 1)
    return c_growth -1 

# used within wrapper
def conservative(data, price_data): 
    try:
        vol, closing_prices, monthly_growths = volatility(price_data)
    except Exception as e:
        vol = None
        closing_prices = []
        monthly_growths = []

    try:
        if closing_prices and data:
            npy = NPY(closing_prices, data, price_data)
        else:
            npy = None
    except Exception as e:
        npy = None

    try:
        if monthly_growths and len(monthly_growths) >= 12:
            moment = momentum(monthly_growths)
        else:
            moment = None
    except Exception as e:
        moment = None

    return {
        "volatility": vol,
        "npy": npy,
        "moment": moment
    }

# used in analysis section 
def conservative_formula(df, separate_data_list):
    df_temp = pd.DataFrame(separate_data_list)

    # Steg 1: Rankningar (NaN behålls automatiskt vid saknade värden)
    df_temp['volatility_rank'] = df_temp['volatility'].rank(ascending=True, method='min')
    df_temp['npy_rank']        = df_temp['npy'].rank(ascending=False, method='min')
    df_temp['moment_rank']     = df_temp['moment'].rank(ascending=False, method='min')

    # Steg 2: Beräkna snitt-rank om alla tre finns, annars sätt None
    scores_dict = {}
    for _, entry in df_temp.iterrows():
        company = entry['Ticker']
        ranks = [entry['volatility_rank'], entry['npy_rank'], entry['moment_rank']]
        
        if all(pd.notna(ranks)):
            avg_rank = round(sum(ranks) / 3, 1)
        else:
            avg_rank = None

        scores_dict[company] = avg_rank

    # Steg 3: Lägg till i ursprungliga df
    scores_series = pd.Series(scores_dict, name='conservative_score')
    df['Conservative Formula'] = df['Ticker'].map(scores_series)

    return df

# used in analysis section
# This closely follows the academic definition of "quality" used by:
#Asness, Frazzini, and Pedersen (in "Quality Minus Junk")
#Novy-Marx (Gross Profitability)
#Green, Hand, Soliman (Accruals and investment patterns)

def quality_score(df):
    df = df.copy()
    
    try:
        z_norm_grossp = (df['Bruttovinstmarginal'] - df['Bruttovinstmarginal'].mean(skipna=True)) / df['Bruttovinstmarginal'].std(skipna=True)
        accruals_abs = -1 * df['Accruals']
        z_norm_accruals = (accruals_abs - accruals_abs.mean(skipna=True)) / accruals_abs.std(skipna=True)
        assetg_abs = -1 * df['Tillgångstillväxt']
        z_norm_assetg = (assetg_abs - assetg_abs.mean(skipna=True)) / assetg_abs.std(skipna=True)
        
        # beräkna enligt "Combined Quality Score Formula"
        df['Quality Score'] = round((z_norm_grossp + z_norm_accruals + z_norm_assetg) / 3, 4)

    except Exception as e:
        raise ValueError(f"Failed to compute quality score: {e}")

    return df

def create_cop_at_noa_composite_score(df):
    """
    Creates a composite score from COP_AT and NOA_GR1A columns.
    
    1. Selects cop_at, NOA_GR1A, and Sector columns
    2. Standardizes using z-scores within each sector  
    3. Creates composite score = z(COP_AT) - z(NOA_GR1A)
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing 'cop_at', 'NOA_GR1A', and 'Sector' columns
    
    Returns:
    pandas.DataFrame: DataFrame with original columns plus composite score
    """
    print("Calculating composite score...")
    
    # Check if required columns exist
    required_columns = ['cop_at', 'NOA_GR1A', 'Sector']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns {missing_columns}. Skipping composite score calculation.")
        return df
    
    # Create a copy of the dataframe
    result_df = df.copy()
    
    # Initialize the composite score column
    result_df['z_NOA_COP_Composite'] = None
    
    try:
        # Process each sector separately
        for sector_name in df['Sector'].dropna().unique():
            print(f"Processing sector: {sector_name}")
            
            # Get rows for this sector with valid cop_at and NOA_GR1A values
            sector_mask = (
                (df['Sector'] == sector_name) & 
                df['cop_at'].notna() & 
                df['NOA_GR1A'].notna()
            )
            
            sector_count = sector_mask.sum()
            if sector_count < 2:
                print(f"  Skipping {sector_name}: only {sector_count} valid data points")
                continue
            
            # Get the data for this sector
            sector_data = df[sector_mask]
            
            # Calculate sector statistics
            cop_mean = sector_data['cop_at'].mean()
            cop_std = sector_data['cop_at'].std()
            noa_mean = sector_data['NOA_GR1A'].mean()
            noa_std = sector_data['NOA_GR1A'].std()
            
            print(f"  {sector_name}: {sector_count} companies, COP_AT std={cop_std:.4f}, NOA std={noa_std:.4f}")
            
            # Skip if no variation (all values the same)
            if cop_std == 0 or noa_std == 0:
                print(f"  Skipping {sector_name}: zero standard deviation")
                continue
            
            # Calculate z-scores and composite score for each company in this sector
            for idx in sector_data.index:
                cop_value = df.loc[idx, 'cop_at']
                noa_value = df.loc[idx, 'NOA_GR1A']
                
                # Calculate z-scores
                z_cop = (cop_value - cop_mean) / cop_std
                z_noa = (noa_value - noa_mean) / noa_std
                
                # Calculate composite score: z(COP_AT) - z(NOA_GR1A)
                composite = z_cop - z_noa
                
                # Round and store
                result_df.loc[idx, 'z_NOA_COP_Composite'] = round(float(composite), 4)
        
        print("Composite score calculation completed.")
        
    except Exception as e:
        print(f"Error in composite score calculation: {e}")
        return df
    
    return result_df

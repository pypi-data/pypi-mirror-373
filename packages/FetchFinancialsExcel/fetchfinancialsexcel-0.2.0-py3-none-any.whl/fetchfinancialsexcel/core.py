import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional, Dict, Any

from . import company_data_extraction_EODH as eodh
from . import data_analysis as analyse


class FundamentalDataFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.current_date = datetime.today().strftime("%Y-%m-%d")
        eodh.API_KEY = api_key
    
    def extract_tickers_from_excel(self, file_path):
        df = pd.read_excel(file_path, header=None)
        tickers = []
        company_list = []
        
        for index, row in df.iterrows():
            if index < 1 or pd.isna(row[1]):
                continue
                
            company = str(row[0]).strip().upper()
            ticker = str(row[1]).strip().upper()
            ticker = ''.join(c for c in ticker if c.isalpha() or c.isdigit() or c == '.' or c == '-')
            ticker = ticker.strip('.-')
            
            if ticker:
                tickers.append(ticker)
            if company:
                company_list.append(company)
                
        return company_list, tickers
    
    def fetch_company_data(self, company_ticker):
        # Fetch fundamental and price data
        data = eodh.fetch_fundamentals(company_ticker)
        price_data = eodh.fetch_price_data(company_ticker)

        # Initialize empty dictionaries
        price = general = roce = pe = revenue = buybacks = ma = eps = total_yield = gross_p = accrual = asset_g = insiders = fcf = cop_at = cop_at_generous = noa = {}
        
        # Fetch all indicators with error handling
        try: 
            price = eodh.real_time_price(company_ticker, data)
            print(f"Price data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching price data: {e}")

        try: 
            general = eodh.get_selected_highlights(data)
            print(f"Highlights fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching highlights: {e}")

        try: 
            roce = eodh.calculate_roce(data)
            print(f"ROCE calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating ROCE: {e}")

        try: 
            pe = eodh.calculate_five_year_average_pe(company_ticker, data, price_data)
            print(f"P/E ratio calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating P/E: {e}")

        try: 
            revenue = eodh.get_revenue_growth_data(data)
            print(f"Revenue data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
        
        try: 
            eps = eodh.get_eps_growth_full(data)
            print(f"EPS data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching EPS data: {e}")
        
        try: 
            fcf = eodh.fcf_yield_growth_latest(data)
            print(f"FCF data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching FCF data: {e}")
        
        try: 
            buybacks = eodh.buyback_change_latest(data)
            print(f"Buyback data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching buyback data: {e}")
        
        try: 
            insiders = eodh.get_percent_insiders(data)
            print(f"Insider data fetched for {company_ticker}.")
        except Exception as e:
            print(f"Error fetching insider data: {e}")

        try: 
            ma = eodh.get_moving_averages(data)
            print(f"Moving averages calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating moving averages: {e}")

        try: 
            gross_p = eodh.gross_profitability(data)
            print(f"Gross profitability calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating gross profitability: {e}")
        
        try: 
            accrual = eodh.accruals(data)
            print(f"Accruals calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating accruals: {e}")

        try: 
            asset_g = eodh.asset_growth(data)
            print(f"Asset growth calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating asset growth: {e}")

        try: 
            total_yield = eodh.total_yield(data)
            print(f"Total yield calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating total yield: {e}")

        try: 
            cop_at = eodh.compute_cop_at(data)
            print(f"COP/AT calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating COP/AT: {e}")

        try: 
            cop_at_generous = eodh.compute_cop_at_generous(data)
            print(f"COP/AT Revised calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating COP/AT Revised: {e}")

        try: 
            noa = eodh.get_NOA(data)
            print(f"NOA calculated for {company_ticker}.")
        except Exception as e:
            print(f"Error calculating NOA: {e}")

        # Fetch conservative components for later calculation
        try: 
            conservative_comps = analyse.conservative(data, price_data)
        except Exception as e:
            print(f"Error calculating conservative components: {e}")
            conservative_comps = {}

        # Combine all indicators
        combined = {**price, **general, **roce, **pe, **revenue, **eps, **fcf, **buybacks, **insiders, **ma, **gross_p, **accrual, **asset_g, **total_yield, **cop_at, **cop_at_generous, **noa}
        other = {**conservative_comps}
        
        return combined, other
    
    def add_company_data(self, data_df: pd.DataFrame, company_name: str, company_ticker: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        company_data = {
            'Bolag': company_name,
            'Ticker': company_ticker
        }

        company_data_separate = {
            'Ticker': company_ticker
        }

        indicators, other = self.fetch_company_data(company_ticker)

        if indicators is not None:
            company_data.update(indicators)
            company_data_separate.update(other)
        else:
            print(f"No data found for {company_ticker}, adding empty row.")

        try:
            data_df = pd.concat([data_df, pd.DataFrame([company_data])], ignore_index=True)
        except Exception as e:
            print("Error adding to DataFrame, adding empty row instead.")
            data_df = pd.concat([data_df, pd.DataFrame([{'Ticker': company_ticker, 'Bolag': company_name}])], ignore_index=True)

        return data_df, company_data_separate
    
    def fetch_all_data(self, company_list: List[str], ticker_list: List[str], max_workers: int = 10) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        data_df = pd.DataFrame()
        separate_data_list = []

        # Combine company names and tickers
        combined = list(zip(company_list, ticker_list))

        def process_company(args):
            company, ticker = args
            return self.add_company_data(pd.DataFrame(), company, ticker)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_company, combined))

        for df, separate_data in results:
            data_df = pd.concat([data_df, df], ignore_index=True)
            separate_data_list.append(separate_data)

        return data_df, separate_data_list
    
    def analyze_data(self, df, separate_data_list):
        
        # Create COP/AT Revised composite score
        df_analyzed = analyse.create_cop_at_noa_composite_score(df)
        
        # Apply Greenblatt formula
        df_analyzed = analyse.greenblatt_formula(df_analyzed)
        
        # Apply conservative formula
        df_analyzed = analyse.conservative_formula(df_analyzed, separate_data_list)
        
        # Calculate quality score
        df_analyzed = analyse.quality_score(df_analyzed)
        
        # Add last updated date
        df_analyzed["Last Updated"] = self.current_date
        
        return df_analyzed
    
    def process_excel_file(self, input_file: str, output_file: str, max_workers: int = 10) -> None:
        print(f"Processing file: {input_file}")
        
        # Extract tickers from Excel file
        company_list, ticker_list = self.extract_tickers_from_excel(input_file)
        print(f"Found {len(ticker_list)} tickers to process")
        
        # Fetch all data
        print("Fetching financial data...")
        df, separate_data_list = self.fetch_all_data(company_list, ticker_list, max_workers)
        
        # Analyze data
        print("Performing financial analysis...")
        df_analyzed = self.analyze_data(df, separate_data_list)
        
        # Clean data before saving to Excel
        print(f"Saving results to: {output_file}")
        
        # Comprehensive data cleaning to prevent Excel XML errors
        import numpy as np
        df_cleaned = df_analyzed.copy()
        
        # Debug: Check for problematic data types and values
        print("Debug: Checking for problematic values...")
        problematic_cols = []
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                # Check for very long strings that might cause issues
                max_length = df_cleaned[col].astype(str).str.len().max()
                if max_length > 1000:
                    problematic_cols.append(f"{col} (long strings: max {max_length})")
            
            # Check for inf values
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                inf_count = np.isinf(df_cleaned[col]).sum()
                if inf_count > 0:
                    problematic_cols.append(f"{col} (inf values: {inf_count})")
        
        if problematic_cols:
            print(f"Found potentially problematic columns: {problematic_cols}")
        
        # Replace inf, -inf, and NaN with None for Excel compatibility
        df_cleaned = df_cleaned.replace([float('inf'), float('-inf'), np.inf, -np.inf], None)
        
        # Handle any remaining NaN values
        df_cleaned = df_cleaned.where(pd.notnull(df_cleaned), None)
        
        # Clean column names - remove/replace problematic characters
        df_cleaned.columns = [str(col).strip().replace('/', '_').replace('\\', '_').replace('*', '_').replace('[', '_').replace(']', '_').replace(':', '_').replace('?', '_') for col in df_cleaned.columns]
        
        # Convert any complex data types to strings
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str)
                # Replace 'None' strings back to actual None
                df_cleaned[col] = df_cleaned[col].replace('None', None)
        
        # Try writing with different engines in case of issues
        try:
            df_cleaned.to_excel(output_file, index=False, engine='openpyxl')
        except Exception as e:
            print(f"Error with openpyxl engine: {e}")
            print("Trying with xlsxwriter engine...")
            try:
                df_cleaned.to_excel(output_file, index=False, engine='xlsxwriter')
            except Exception as e2:
                print(f"Error with xlsxwriter engine: {e2}")
                # Fallback to CSV if Excel fails
                csv_file = output_file.replace('.xlsx', '.csv')
                print(f"Saving as CSV instead: {csv_file}")
                df_cleaned.to_csv(csv_file, index=False)
        print("Processing complete!") 
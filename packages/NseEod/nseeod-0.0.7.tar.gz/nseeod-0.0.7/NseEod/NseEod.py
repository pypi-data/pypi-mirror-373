"""
* NSE EOD Library *
Description: This NSE EOD Library is a Python Library to get publicly available data from the new NSE India website
Disclaimer: This NSE EOD Library is meant for educational purposes only. Downloading data from the NSE
website requires explicit approval from the exchange. Hence, the usage of this NSE EOD Library is for
limited purposes only under proper/explicit approvals.
Requirements: The following packages are to be installed (using pip) prior to using this NSE EOD Library
- pandas
- python 3.8 and above

"""
# pip install pandas xlrd openpyxl pyxlsb requests

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import zipfile
import random
import time
import feedparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

class NseEoD:
    equity_market_list = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100',
                          'NIFTY MIDCAP 150', 'NIFTY SMALLCAP 50', 'NIFTY SMALLCAP 100', 'NIFTY SMALLCAP 250',
                          'NIFTY MIDSMALLCAP 400', 'NIFTY 100', 'NIFTY 200', 'NIFTY AUTO',
                          'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FINANCIAL SERVICES', 'NIFTY FINANCIAL SERVICES 25/50',
                          'NIFTY FMCG', 'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA', 'NIFTY PSU BANK',
                          'NIFTY REALTY', 'NIFTY PRIVATE BANK', 'Securities in F&O', 'Permitted to Trade',
                          'NIFTY DIVIDEND OPPORTUNITIES 50', 'NIFTY50 VALUE 20', 'NIFTY100 QUALITY 30',
                          'NIFTY50 EQUAL WEIGHT', 'NIFTY100 EQUAL WEIGHT', 'NIFTY100 LOW VOLATILITY 30',
                          'NIFTY ALPHA 50', 'NIFTY200 QUALITY 30', 'NIFTY ALPHA LOW-VOLATILITY 30',
                          'NIFTY200 MOMENTUM 30', 'NIFTY COMMODITIES', 'NIFTY INDIA CONSUMPTION', 'NIFTY CPSE',
                          'NIFTY INFRASTRUCTURE', 'NIFTY MNC', 'NIFTY GROWTH SECTORS 15', 'NIFTY PSE',
                          'NIFTY SERVICES SECTOR', 'NIFTY100 LIQUID 15', 'NIFTY MIDCAP LIQUID 15']
    pre_market_list = ['NIFTY 50', 'Nifty Bank', 'Emerge', 'Securities in F&O', 'Others', 'All']

    def __init__(self):
        self.session = requests.Session()
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session with proper cookies and headers"""
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Origin': 'https://www.nseindia.com'
        }
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)
            self.session.get("https://www.nseindia.com/market-data/live-equity-market", 
                           headers=self.headers, timeout=10)
            time.sleep(1)
        except requests.RequestException:
            pass

    def _get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        return random.choice(user_agents)

    def rotate_user_agent(self):
        self.headers['User-Agent'] = self._get_random_user_agent()

    def fno_bhav_copy(self, trade_date: str = ""):
        self.rotate_user_agent()
        bhav_df = pd.DataFrame()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = 'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'
        payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"

        try:
            request_bhav = self.session.get(url + payload, headers=self.headers, timeout=10)
            if request_bhav.status_code == 200:
                bhav_df = self._extract_csv_from_zip(request_bhav.content)
            else:
                url2 = "https://www.nseindia.com/api/reports?archives=" \
                       "%5B%7B%22name%22%3A%22F%26O%20-%20Bhavcopy(csv)%22%2C%22type%22%3A%22archives%22%2C%22category%22" \
                       f"%3A%22derivatives%22%2C%22section%22%3A%22equity%22%7D%5D&date={str(trade_date.strftime('%d-%b-%Y'))}" \
                       "&type=equity&mode=single"
                ref = requests.get('https://www.nseindia.com/reports-archives', headers=self.headers)
                request_bhav = self.session.get(url2, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
                request_bhav.raise_for_status()
                bhav_df = self._extract_csv_from_zip(request_bhav.content)

            if not bhav_df.empty:
                # Filtering rows where all four columns (22, 23, 24, 25) are zero
                try:
                    bhav_df = bhav_df[~((bhav_df.iloc[:, 22] == 0) & 
                                         (bhav_df.iloc[:, 23] == 0) & 
                                         (bhav_df.iloc[:, 24] == 0) & 
                                         (bhav_df.iloc[:, 25] == 0))]
                    bhav_df = bhav_df.sort_values(by=bhav_df.columns[24], ascending=False)
                except IndexError:
                    print("Warning: The specified columns do not exist in the CSV.")

            return bhav_df

        except (requests.RequestException, FileNotFoundError):
            return None

    def _extract_csv_from_zip(self, zip_content):
        with zipfile.ZipFile(BytesIO(zip_content), 'r') as zip_bhav:
            for file_name in zip_bhav.namelist():
                if file_name.endswith('.csv'):
                    return pd.read_csv(zip_bhav.open(file_name))
        return pd.DataFrame()


    def bhav_copy_with_delivery(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        use_date = trade_date.strftime("%d%m%Y")
        url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{use_date}.csv'
        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(request_bhav.content))
            bhav_df.columns = [name.replace(' ', '') for name in bhav_df.columns]
            bhav_df['SERIES'] = bhav_df['SERIES'].str.replace(' ', '')
            bhav_df['DATE1'] = bhav_df['DATE1'].str.replace(' ', '')
            return bhav_df
        except requests.RequestException:
            return None

    def equity_bhav_copy(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = 'https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_'
        payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
        try:
            request_bhav = requests.get(url + payload, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()
            for file_name in zip_bhav.filelist:
                if file_name:
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
            return bhav_df
        except requests.RequestException:
            return None

    def bhav_copy_indices(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None

    def series_change(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/series_change.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def shortselling(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/archives/equities/shortSelling/shortselling_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def eq_band_changes(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/equities/eq_band_changes_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def pe_ratio(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%y")
        url = f"https://nsearchives.nseindia.com/content/equities/peDetail/PE_{str(trade_date.strftime('%d%m%y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def market_activity_report(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%y")
        url = f"https://nsearchives.nseindia.com/archives/equities/mkt/MA{str(trade_date.strftime('%d%m%y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def bulk_deal(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/bulk.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def block_deal(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/block.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def price_band(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/equities/sec_list_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def surveillance_indicator(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%y")
        url = f"https://nsearchives.nseindia.com/content/cm/REG1_IND{str(trade_date.strftime('%d%m%y').upper())}.csv"
        
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))

            # Replace 100 with blank in columns F to R
            columns_to_replace = bhav_df.loc[:, 'GSM':'Filler31'].columns
            bhav_df[columns_to_replace] = bhav_df[columns_to_replace].replace(100, '')

            return bhav_df
        except (requests.RequestException, ValueError) as e:
            print("Error:", e)
            return None
        
    def top10_nifty50(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%y")
        url = f"https://nsearchives.nseindia.com/content/indices/top10nifty50_{str(trade_date.strftime('%d%m%y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def mcap(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%y")
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{trade_date.strftime('%d%m%y').upper()}.zip"

        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()

            for file_name in zip_bhav.namelist():
                if file_name.lower().startswith("mcap") and file_name.endswith(".csv"):
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
                    break

            if bhav_df.empty:
                print("No MCAP CSV file found in the ZIP archive.")
                return None

            return bhav_df

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        

    # def namechange(self):
    #     self.rotate_user_agent()
    #     url = f"https://nsearchives.nseindia.com/content/equities/namechange.csv"
    #     try:
    #         nse_resp = requests.get(url, headers=self.headers, timeout=10)
    #         nse_resp.raise_for_status()
    #         bhav_df = pd.read_csv(BytesIO(nse_resp.content))
    #         return bhav_df
    #     except (requests.RequestException, ValueError):
    #         return None
        
    # def symbolchange(self):
    #     self.rotate_user_agent()
    #     url = f"https://nsearchives.nseindia.com/content/equities/symbolchange.csv"
    #     try:
    #         nse_resp = requests.get(url, headers=self.headers, timeout=10)
    #         nse_resp.raise_for_status()
    #         bhav_df = pd.read_csv(BytesIO(nse_resp.content))
    #         return bhav_df
    #     except (requests.RequestException, ValueError):
    #         return None

    def namechange(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/namechange.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))

            # Convert the 4th column (index 3) to date format YYYY-MM-DD using explicit format
            if bhav_df.shape[1] >= 4:  # Ensure 4 columns exist
                bhav_df.iloc[:, 3] = pd.to_datetime(
                    bhav_df.iloc[:, 3], 
                    format='%d-%b-%Y',  # specify the date format explicitly
                    errors='coerce'
                ).dt.strftime('%Y-%m-%d')

                # Sort by the 4th column descending (new to old)
                bhav_df = bhav_df.sort_values(by=bhav_df.columns[3], ascending=False).reset_index(drop=True)

            return bhav_df
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching or processing data: {e}")
            return None
        
    def symbolchange(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/symbolchange.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content), header=None)  # No header specified

            # Convert the 4th column (index 3) to date format YYYY-MM-DD using explicit format
            if bhav_df.shape[1] >= 4:  # Ensure 4 columns exist
                bhav_df.iloc[:, 3] = pd.to_datetime(
                    bhav_df.iloc[:, 3], 
                    format='%d-%b-%Y',  # specify the date format explicitly
                    errors='coerce'
                ).dt.strftime('%Y-%m-%d')  # Convert to string format for JSON serialization

                # Sort by the 4th column descending (new to old)
                bhav_df = bhav_df.sort_values(by=bhav_df.columns[3], ascending=False).reset_index(drop=True)

            return bhav_df
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching or processing data: {e}")
            return None


       
    def get_52_week_high_low(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/CM_52_wk_High_low_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
    

    #---------------------------------------------------------- F&O ----------------------------------------------------------------

    def fno_ban(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/archives/fo/sec_ban/fo_secban_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def fno_combine_oi(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/archives/nsccl/mwpl/combineoi_{trade_date.strftime('%d%m%Y').upper()}.zip"

        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()

            for file_name in zip_bhav.namelist():
                if file_name.lower().startswith("combineoi") and file_name.endswith(".csv"):
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
                    break

            if bhav_df.empty:
                print("No combineoi CSV file found in the ZIP archive.")
                return None

            return bhav_df

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        
    def fno_participant_wise_oi(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
    
    def fno_participant_wise_vol(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None

    def fno_mwpl_3(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/nsccl/mwpl_cli_{trade_date.strftime('%d%m%Y').upper()}.xls"
        
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()

            file_content = BytesIO(nse_resp.content)
            file_format = self.detect_excel_format(file_content)

            print(f"Detected File Format: {file_format}")

            if file_format == 'xls':
                bhav_df = pd.read_excel(file_content, engine='xlrd', dtype=str)
            elif file_format == 'xlsx':
                bhav_df = pd.read_excel(file_content, engine='openpyxl', dtype=str)
            elif file_format == 'xlsb':
                bhav_df = pd.read_excel(file_content, engine='pyxlsb', dtype=str)
            else:
                print("Unknown file format or corrupted file.")
                return None

            # Cleaning the DataFrame
            bhav_df = self.clean_mwpl_data(bhav_df)
            return bhav_df
        
        except requests.RequestException as e:
            print(f"Request Error: {e}")
        except ValueError as e:
            print(f"Value Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
        
        return None

    def clean_mwpl_data(self, df):
        """
        Cleans the MWPL DataFrame by avoiding 'Unnamed' columns and filling them automatically.
        """
        # Dropping any rows without valid data (optional, for extra cleaning)
        df.dropna(how='all', inplace=True)

        # Resetting the header (first row becomes the actual header)
        df.columns = df.iloc[0]  # Set the first row as header
        df = df[1:].reset_index(drop=True)  # Remove the header row

        # Automatically filling 'Unnamed' columns with "Client X" format
        new_columns = []
        client_counter = 1

        for col in df.columns:
            if "Unnamed" in str(col) or pd.isna(col):
                new_columns.append(f"Client {client_counter}")
                client_counter += 1
            else:
                new_columns.append(str(col).strip())

        df.columns = new_columns
        return df

    def detect_excel_format(self, file_content):
        """
        Detects the format of the Excel file using the first few bytes.
        Returns: 'xls', 'xlsx', 'xlsb', or 'unknown'.
        """
        signature = file_content.read(8)
        file_content.seek(0)  # Reset buffer pointer for reading

        print(f"File Signature: {signature}")

        if signature.startswith(b'\xD0\xCF\x11\xE0'):  # XLS (OLE2 Compound File)
            return 'xls'
        elif signature.startswith(b'\x50\x4B\x03\x04'):  # XLSX (ZIP)
            return 'xlsx'
        elif signature.startswith(b'\x09\x08\x10\x00'):  # XLSB (Binary Excel)
            return 'xlsb'
        else:
            return 'unknown'
        
    def fno_fii_stats(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        formatted_date = trade_date.strftime("%d-%b-%Y")
        formatted_date = formatted_date[:3] + formatted_date[3:].capitalize()
        url = f"https://nsearchives.nseindia.com/content/fo/fii_stats_{formatted_date}.xls"
        
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()

            file_content = BytesIO(nse_resp.content)
            file_format = self.detect_excel_format(file_content)

            print(f"Detected File Format: {file_format}")

            if file_format == 'xls':
                bhav_df = pd.read_excel(file_content, engine='xlrd', dtype=str)
            elif file_format == 'xlsx':
                bhav_df = pd.read_excel(file_content, engine='openpyxl', dtype=str)
            elif file_format == 'xlsb':
                bhav_df = pd.read_excel(file_content, engine='pyxlsb', dtype=str)
            else:
                print("Unknown file format or corrupted file.")
                return None

            return bhav_df
        
        except requests.RequestException as e:
            print(f"Request Error: {e}")
        except ValueError as e:
            print(f"Value Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
        
        return None

    def fno_top10_fut(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{trade_date.strftime('%d%m%Y').upper()}.zip"

        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()

            for file_name in zip_bhav.namelist():
                if file_name.lower().startswith("ttfut") and file_name.endswith(".csv"):
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
                    break

            if bhav_df.empty:
                print("No combineoi CSV file found in the ZIP archive.")
                return None

            return bhav_df

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        
    def fno_top20_opt(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{trade_date.strftime('%d%m%Y').upper()}.zip"

        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()

            for file_name in zip_bhav.namelist():
                if file_name.lower().startswith("ttopt") and file_name.endswith(".csv"):
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
                    break

            if bhav_df.empty:
                print("No combineoi CSV file found in the ZIP archive.")
                return None

            return bhav_df

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        
    def nifty_50(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def nifty_500(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
        
    def all_Nse(self):
        self.rotate_user_agent()
        url = f"https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None
    
    def get_index_historic_data(self, index: str, from_date: str = None, to_date: str = None):
        index_data_columns = ['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 'CLOSE_INDEX_VAL',
                              'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']
        if not from_date or not to_date:
            raise ValueError('Please provide valid parameters')
        try:
            from_dt = datetime.strptime(from_date, "%d-%m-%Y")
            to_dt = datetime.strptime(to_date, "%d-%m-%Y")
            if (to_dt - from_dt).days < 1:
                raise ValueError('to_date should be greater than from_date')
        except Exception as e:
            raise ValueError(f'Either or both from_date = {from_date} || to_date = {to_date} are not valid value')

        nse_df = pd.DataFrame(columns=index_data_columns)
        from_date = datetime.strptime(from_date, "%d-%m-%Y")
        to_date = datetime.strptime(to_date, "%d-%m-%Y")
        load_days = (to_date - from_date).days

        while load_days > 0:
            if load_days > 365:
                end_date = (from_date + timedelta(364)).strftime("%d-%m-%Y")
                start_date = from_date.strftime("%d-%m-%Y")
            else:
                end_date = to_date.strftime("%d-%m-%Y")
                start_date = from_date.strftime("%d-%m-%Y")

            data_df = self.get_index_data(index=index, from_date=start_date, to_date=end_date)
            if data_df is not None:
                from_date = from_date + timedelta(365)
                load_days = (to_date - from_date).days
                nse_df = pd.concat([nse_df, data_df], ignore_index=True)
        return nse_df
    
    def trading_holidays(self, list_only=False):
        self.rotate_user_agent()
        holiday_type = "trading"
        try:
            response = self.session.get(
                f"https://www.nseindia.com/api/holiday-master?type={holiday_type}",
                headers=self.headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract only "CM" (Capital Market) holiday data
            if "CM" in data:
                df = pd.DataFrame(data["CM"], columns=["Sr_no", "tradingDate", "weekDay", "description", "morning_session", "evening_session"])
                
                if list_only:
                    return df["tradingDate"].tolist()
                return df
            else:
                return None
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching trading holidays: {e}")
            return None

  
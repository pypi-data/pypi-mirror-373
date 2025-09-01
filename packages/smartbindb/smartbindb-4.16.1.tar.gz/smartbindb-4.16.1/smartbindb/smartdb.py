import asyncio
import json
import os
import time
import pycountry
import pycountry_convert
from typing import Optional, List, Dict
import struct
import mmap
from functools import lru_cache

class SmartBinDB:
    def __init__(self):
        self.COUNTRY_JSON_DIR = os.path.join(os.path.dirname(__file__), "data")
        self.BINARY_DB = os.path.join(os.path.dirname(__file__), "smartbin.db")
        self.BIN_INDEX = {}
        self.COUNTRY_DATA = {}
        self.START_TIME = time.time()
        self._country_cache = self._build_country_cache()
        
    def _build_country_cache(self):
        cache = {}
        try:
            for country in pycountry.countries:
                try:
                    continent_code = pycountry_convert.country_alpha2_to_continent_code(country.alpha_2)
                    continent = pycountry_convert.convert_continent_code_to_continent_name(continent_code)
                except:
                    continent = ""
                
                cache[country.alpha_2] = {
                    "A2": country.alpha_2,
                    "A3": country.alpha_3,
                    "N3": country.numeric,
                    "Name": country.name,
                    "Cont": continent
                }
        except:
            pass
        return cache

    def _build_binary_db(self):
        if not os.path.exists(self.COUNTRY_JSON_DIR):
            return False
            
        all_data = {}
        bin_index = {}
        
        json_files = [f for f in os.listdir(self.COUNTRY_JSON_DIR) if f.lower().endswith('.json')]
        
        for filename in json_files:
            country_code = filename.replace('.json', '').upper()
            file_path = os.path.join(self.COUNTRY_JSON_DIR, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                all_data[country_code] = data
                
                for entry in data:
                    if 'bin' in entry:
                        bin_index[entry['bin']] = entry
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
        
        combined_data = {
            'country_data': all_data,
            'bin_index': bin_index,
            'version': 1
        }
        
        try:
            import pickle
            with open(self.BINARY_DB, 'wb') as f:
                pickle.dump(combined_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            print(f"Error creating binary DB: {e}")
            return False

    def _load_binary_db(self):
        if not os.path.exists(self.BINARY_DB):
            return False
            
        try:
            import pickle
            with open(self.BINARY_DB, 'rb') as f:
                data = pickle.load(f)
            
            self.COUNTRY_DATA = data['country_data']
            self.BIN_INDEX = data['bin_index']
            return True
        except Exception as e:
            print(f"Error loading binary DB: {e}")
            return False

    def _needs_rebuild(self):
        if not os.path.exists(self.BINARY_DB):
            return True
            
        if not os.path.exists(self.COUNTRY_JSON_DIR):
            return False
        
        try:
            db_time = os.path.getmtime(self.BINARY_DB)
            
            for filename in os.listdir(self.COUNTRY_JSON_DIR):
                if filename.lower().endswith('.json'):
                    file_path = os.path.join(self.COUNTRY_JSON_DIR, filename)
                    if os.path.getmtime(file_path) > db_time:
                        return True
            return False
        except:
            return True

    async def load_file(self, file_path: str, country_code: str) -> bool:
        return True

    async def load_data(self):
        if self.BIN_INDEX and self.COUNTRY_DATA:
            return
            
        if self._needs_rebuild():
            print("Building optimized database...")
            if not self._build_binary_db():
                print("Failed to build binary database")
                return
        
        if self._load_binary_db():
            return
        
        if not os.path.exists(self.COUNTRY_JSON_DIR):
            print(f"Directory {self.COUNTRY_JSON_DIR} does not exist")
            return

        print("Fallback: Loading JSON files...")
        json_files = [f for f in os.listdir(self.COUNTRY_JSON_DIR) if f.lower().endswith('.json')]
        
        for filename in json_files:
            country_code = filename.replace('.json', '').upper()
            file_path = os.path.join(self.COUNTRY_JSON_DIR, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.COUNTRY_DATA[country_code] = data
                
                for entry in data:
                    if 'bin' in entry:
                        self.BIN_INDEX[entry['bin']] = entry
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    @lru_cache(maxsize=2000)
    def get_country_info(self, country_code: str) -> dict:
        country_code = country_code.upper()
        return self._country_cache.get(country_code, {
            "A2": country_code,
            "A3": "",
            "N3": "",
            "Name": "",
            "Cont": ""
        })

    def format_entry(self, entry: dict) -> dict:
        country_code = entry.get('country_code', '').upper()
        country_info = self.get_country_info(country_code)
        category = entry.get('category', '')
        brand = entry.get('brand', '')
        
        return {
            "bin": entry.get('bin', ''),
            "brand": brand,
            "category": category,
            "CardTier": f"{category} {brand}".strip(),
            "country_code": country_code,
            "Type": entry.get('type', ''),
            "country_code_alpha3": entry.get('country_code_alpha3', ''),
            "Country": country_info,
            "issuer": entry.get('issuer', ''),
            "phone": entry.get('phone', ''),
            "type": entry.get('type', ''),
            "website": entry.get('website', '')
        }

    async def get_bins_by_bank(self, bank: str, limit: Optional[int] = None) -> dict:
        if not self.BIN_INDEX:
            await self.load_data()
            if not self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }

        bank_lower = bank.lower()
        matching_bins = []
        
        for data in self.COUNTRY_DATA.values():
            for entry in data:
                if 'issuer' in entry and bank_lower in entry['issuer'].lower():
                    matching_bins.append(self.format_entry(entry))
                    if limit and len(matching_bins) >= limit:
                        break
            if limit and len(matching_bins) >= limit:
                break

        if not matching_bins:
            return {
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }

        return {
            "status": "SUCCESS",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }

    async def get_bins_by_country(self, country: str, limit: Optional[int] = None) -> dict:
        if not self.BIN_INDEX:
            await self.load_data()
            if not self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }

        country = country.upper()
        
        if country == 'US':
            matching_bins = []
            for country_code in ['US', 'US1', 'US2']:
                if country_code in self.COUNTRY_DATA:
                    for entry in self.COUNTRY_DATA[country_code]:
                        matching_bins.append(self.format_entry(entry))
                        if limit and len(matching_bins) >= limit:
                            break
                if limit and len(matching_bins) >= limit:
                    break
                    
            if not matching_bins:
                return {
                    "status": "error",
                    "message": "No data found for country code: US",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            
            if limit is None:
                limit = 1000
            if limit > 8000:
                return {
                    "status": "error",
                    "message": "Maximum limit allowed for US is 8000",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            
            return {
                "status": "SUCCESS",
                "data": matching_bins[:limit],
                "count": len(matching_bins[:limit]),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        else:
            if country not in self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"No data found for country code: {country}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            
            data = []
            for entry in self.COUNTRY_DATA[country]:
                data.append(self.format_entry(entry))
                if limit and len(data) >= limit:
                    break
            
            return {
                "status": "SUCCESS",
                "data": data,
                "count": len(data),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }

    async def get_bin_info(self, bin: str) -> dict:
        if not self.BIN_INDEX:
            await self.load_data()
            if not self.BIN_INDEX:
                return {
                    "status": "error",
                    "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
        
        if bin in self.BIN_INDEX:
            return {
                "status": "SUCCESS",
                "data": [self.format_entry(self.BIN_INDEX[bin])],
                "count": 1,
                "filtered_by": "bin",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        
        return {
            "status": "error",
            "message": f"No matches found for BIN: {bin}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }
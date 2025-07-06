# 三大法人買賣超資料爬蟲
# python 3.11.7
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import pandas as pd
import os
from io import StringIO
import random
import csv
import asyncio

# 一天抓三次 
# 1: 6:00 檔案在 fwbtin_6, 
# 2: 14:00 檔案在 fwbtin_14, 
# 3: 15:00 檔案在 fwbtin
def fetch_fwbtin(driver, date, hour=15):
    '''
        爬到三大法人的資料並存在 history_data/tw/fwbtin/ 資料夾中
    '''
    url = 'https://www.taifex.com.tw/cht/3/futContractsDate'
    url_ah = 'https://www.taifex.com.tw/cht/3/futContractsDateAh'
    
    file_name = f'fwbtin'
    # 現在時間
    if hour == 6:
        file_name = f'fwbtin_raw_6'
        url = url_ah
    elif hour == 14:
        file_name = f'fwbtin_raw_14'
    
    driver.get(url)


    print(f"Fetching 三大法人資料...")

    # search
    max_retries = 3
    for attempt in range(max_retries):
        try:
            input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div[2]/div[3]/div/div[3]/div/form/fieldset/ul/li[1]/div[2]/input")
            # 獲取輸入框的預設值
            original_value = input_search.get_attribute("value")
            print(f"原始輸入框值: {original_value}")
            if date is None:
                print("日期為 None，使用預設值")
                d = original_value
                date = datetime.strptime(original_value, '%Y/%m/%d')
                str_d = date.strftime('%Y%m%d')
            else:
                d = date.strftime('%Y/%m/%d')
                str_d = date.strftime('%Y%m%d')
            
                input_search.clear()
                input_search.send_keys(d)
                driver.find_element(By.XPATH, '//*[@id="button"]').click()
            break  # 成功就跳出迴圈
        except Exception as e:
            print(f"查無資料, 網頁異常 => 重新搜尋 (第{attempt+1}次)")
            time.sleep(random.uniform(1, 3))
    else:
        print("多次嘗試仍失敗，無法依照日期取得資料")
        return
    
    
    # 檢查該天檔案是否已存在
    if not os.path.exists(os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw',f'{file_name}', f'fwbtin_{str_d}.csv')):
        print(f"檔案 {str_d} 不存在，繼續爬蟲")
    else:
        print(f"檔案 {str_d} 已存在，跳過爬蟲")
        return
    
    # 等待資料載入
    time.sleep(random.uniform(1, 3))   
    
    # 找到 table
    try:
        tbody = driver.find_element(By.TAG_NAME, 'table')
        table_html = tbody.get_attribute('outerHTML')
        if table_html == '':
            print("Table HTML is empty, 無法取得資料")
            return
    except:
        print("Table HTML is empty, 無法取得資料")
        return
    
    df = pd.read_html(StringIO(table_html))[0]
    if df.isin(['查無資料']).any().any():
        print("     DataFrame 中包含[查無資料]，可能不是交易日 => 跳過")
        return
    
    # process data
    path = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw',f'{file_name}', f'fwbtin_{str_d}.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, mode='w', encoding='utf-8', index=False)
    print(f"成功取得三大法人資料 => 資料日期: {date}")
    return date

def write_data_handler(df, path):
    # 定義完整的欄位順序，寫入資料
    columns = ['日期', '自營商未平倉多', '自營商未平倉空', '自營商未平倉淨額', 
                '投信未平倉多', '投信未平倉空', '投信未平倉淨額',
                '外資未平倉多', '外資未平倉空', '外資未平倉淨額']
    df = df.reindex(columns=columns, fill_value='')

    if os.path.getsize(path) == 0:
        # old_data = pd.read_csv(path, encoding='utf-8')
        # old_data.set_index('日期', inplace=True
        
        df.to_csv(path, mode='w', encoding='utf-8', index=False, header=True)
    else:

        df.to_csv(path, mode='a', encoding='utf-8', index=False, header=False)
    
def get_tx_open_interest(path_raw, str_d):
    '''
        取得大台多空資料（只要口數）
    '''
    df_raw = pd.read_csv(path_raw, encoding='utf-8', header=[0, 1, 2])
    df_fwbtin = df_raw[df_raw[('Unnamed: 1_level_0', 'Unnamed: 1_level_1', '商品 名稱')] == '臺股期貨']

    df_open_interest = pd.DataFrame({
        '日期': str_d,
        '自營商交易多': df_fwbtin.xs(('交易口數與契約金額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        '自營商交易空': df_fwbtin.xs(('交易口數與契約金額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        '自營商交易多空淨額': df_fwbtin.xs(('交易口數與契約金額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        
        '投信交易多': df_fwbtin.xs(('交易口數與契約金額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(),
        '投信交易空': df_fwbtin.xs(('交易口數與契約金額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(),
        '投信交易多空淨額': df_fwbtin.xs(('交易口數與契約金額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(), 
        
        '外資交易多': df_fwbtin.xs(('交易口數與契約金額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[2].item(),
        '外資交易空': df_fwbtin.xs(('交易口數與契約金額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[2].item(),
        '外資交易多空淨額': df_fwbtin.xs(('交易口數與契約金額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[2].item(),
    }, index=[0])
    return df_open_interest
    
def get_tx_balance(path_raw, str_d):
    '''
        取得大台未平倉餘額（只要口數）
    '''

    df_raw = pd.read_csv(path_raw, encoding='utf-8', header=[0, 1, 2])
    df_fwbtin = df_raw[df_raw[('Unnamed: 1_level_0', 'Unnamed: 1_level_1', '商品 名稱')] == '臺股期貨']

    df_balance = pd.DataFrame({
        '日期': str_d,
        '自營商未平倉多': df_fwbtin.xs(('未平倉餘額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        '自營商未平倉空': df_fwbtin.xs(('未平倉餘額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        '自營商未平倉淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[0].item(),
        
        '投信未平倉多': df_fwbtin.xs(('未平倉餘額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(),
        '投信未平倉空': df_fwbtin.xs(('未平倉餘額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(),
        '投信未平倉淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[1].item(),
        
        '外資未平倉多': df_fwbtin.xs(('未平倉餘額', '多方', '口數'), level=[0, 1, 2], axis=1).iloc[2].item(),
        '外資未平倉空': df_fwbtin.xs(('未平倉餘額', '空方', '口數'), level=[0, 1, 2], axis=1).iloc[2].item(),
        '外資未平倉淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額', '口數'), level=[0, 1, 2], axis=1).iloc[2].item()
    }, index=[0]) 
    return df_balance

def get_tx_calculated(current_balance, date, hour=15):
    '''
        計算大台買賣超資料
    '''
    str_d = date.strftime('%Y%m%d')
    if hour == 15:
        print(f"[試算資料] 15點的資料是公布資料")
        return
    
    path_tx_calculated = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'calculated_data.csv')
    path_tx_announced = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'announced_data.csv')
    path_raw = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw',f'fwbtin_raw_{hour}', f'fwbtin_{str_d}.csv')
    
    if not os.path.exists(path_raw):
        print(f"[試算資料] {str_d} {hour}點的資料不存在 => 跳過")
        return
    
    df_balance = current_balance
    df_open_intrest = get_tx_open_interest(path_raw, str_d)
    
    # 要寫入兩行資料 1 日盤 2 夜盤
    # 日盤
    # print(df_balance)
    # print(df_open_intrest)
    
    # 夜盤 夜盤的資料是日盤的資料加上交易口數與契約金額
    # 創建新的 DataFrame
    new_balance = pd.DataFrame({
        '日期': str_d,
        # '自營商交易多空淨額': df_open_intrest['自營商交易多空淨額'].iloc[0],
        '自營商未平倉淨額': df_balance['自營商未平倉淨額'].iloc[0] + df_open_intrest['自營商交易多空淨額'].iloc[0],
        # '投信交易多空淨額': df_open_intrest['投信交易多空淨額'].iloc[0],
        '投信未平倉淨額': df_balance['投信未平倉淨額'].iloc[0] + df_open_intrest['投信交易多空淨額'].iloc[0],
        # '外資交易多空淨額': df_open_intrest['外資交易多空淨額'].iloc[0],
        '外資未平倉淨額': df_balance['外資未平倉淨額'].iloc[0] + df_open_intrest['外資交易多空淨額'].iloc[0],
    }, index=[0])
    
    return new_balance

def format_balance_simple(df):
    row = df.iloc[0]
    lines = [f"{col}: {row[col]}" for col in df.columns]
    return "\n".join(lines)

def announced_data_process(date, hour=15):
    '''
        公布資料處理
    '''
    str_d = date.strftime('%Y%m%d')
    path_tx_announced = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'announced_data.csv')    
    path_raw = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw',f'fwbtin', f'fwbtin_{str_d}.csv')
    if os.path.exists(path_raw):
        print(f"[公布資料] 處理 {str_d} 公布資料")
        df_balance = get_tx_balance(path_raw, str_d)
        write_data_handler(df_balance, path_tx_announced)
        return format_balance_simple(df_balance)
    else:
        print(f"[公布資料] {str_d} 今天資料還沒抓 或 不是交易日 => 跳過")
        return


def calculated_data_process(date, hour=15):
    '''
        資料處理，將試算資料與公布資料合併
        算夜盤或日盤資料，試算資料是當日資料，所以只要抓公布資料的最後一筆就好
    '''
    path_tx_calculated = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'calculated_data.csv')
    path_tx_announced = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'announced_data.csv')
    df_tx_calculated = pd.read_csv(path_tx_calculated, encoding='utf-8')   # 試算的資料
    df_tx_announced = pd.read_csv(path_tx_announced, encoding='utf-8')  # 已經有資料的資料
    df_last_announced = df_tx_announced.iloc[-1:]  # 使用 [-1:] 來取得 DataFrame 而不是 Series

    # 帶入前一天的資料以及新增資料試算
    new_balance = get_tx_calculated(df_last_announced, date, hour)
    
    if new_balance is None:
        print(f"[試算資料] {date.strftime('%Y%m%d')} {hour}點的試算資料不存在 => 跳過")
        return
    else:
        print(f"[試算資料] 寫入 {date.strftime('%Y%m%d')} {hour}點的試算資料")
        write_data_handler(new_balance, path_tx_calculated)
        # 回傳三大法人買賣超資料
        return format_balance_simple(new_balance)
        
        
def crawler(date, hour=15):
    driver = webdriver.Chrome()
    date = fetch_fwbtin(driver, date, hour)
    driver.quit()
    
    return date
    


# ================================ 以下測試用 ================================ 
# 這是爬蟲測試，會自動抓每天的夜盤、日盤資料
# 如果在 14~15點執行，14～15點的資料不會存在14的資料，要注意

# driver = webdriver.Chrome()
# while start_date <= end_date:
#     fetch_fwbtin(driver, start_date, 6)
#     fetch_fwbtin(driver, start_date)
#     # get_tx_calculated(start_date)
#     start_date += timedelta(days=1)
# driver.quit()

# --------------------------------------------------------------

# 這段是給我測試用的，要刪掉 fwbtin_tx 裡面的 announced_data.csv 和 calculated_data.csv 才能測試
# 建議在15:00 之後測試
# 爬蟲需要另外測試
# start_date = datetime(2025, 1, 3)
# end_date = datetime(2025, 6, 20)

# while start_date <= end_date:
#     print(f"處理 {start_date.strftime('%Y%m%d')} 資料")
#     announced_data_process(start_date - timedelta(days=1))
#     calculated_data_process(start_date, 6)  # 6點 處理夜盤資料
#     calculated_data_process(start_date, 14) # 14點 處理日盤資料
#     start_date += timedelta(days=1)
# ================================ 以上測試用 ================================ 

# 這行是給 scheduler 用的
__all__ = [
    "calculated_data_process",
    "announced_data_process",
    "crawler", 
]
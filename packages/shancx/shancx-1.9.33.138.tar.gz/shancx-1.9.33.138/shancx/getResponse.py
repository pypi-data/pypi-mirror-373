

import requests
import time
import traceback
from shancx import loggers as logger
def fetch_with_timeout(url, headers,cookies=None, params=None, max_attempts=4, timeout=7):
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=timeout)
            response.raise_for_status() 
            return response  
        except requests.Timeout:
            print(f"Attempt {attempts + 1}: Request timed out. Retrying...")
        except requests.RequestException as e:
            print(f"Attempt {attempts + 1}: An error occurred: {e}")
            logger.info(f"Attempt {attempts + 1}: An error occurred: {traceback.format_exc()}")
            if attempts + 1 < max_attempts:
                time.sleep(2 ** attempts)  # Exponential backoff
            else:
                print("Max attempts reached. Exiting.")
                return None  # 所有尝试失败，返回 None
        attempts += 1
        time.sleep(1) 
import os
import time
import asyncio
import threading
import logging
from typing import Union, Literal
import traceback
import netCDF4 as nc
from shancx.NN import setlogger
logger = setlogger(level=logging.INFO)
def smart_wait(
    path: str,
    timeout: Union[int, float] = 300,
    mode: Literal['auto', 'polling', 'async'] = 'auto',
    debug: bool = False
) -> bool:
    """
    智能文件等待方案（自动选择最优策略）    
    Args:
        path: 要监控的文件路径
        timeout: 最大等待时间（秒）
        mode: 运行模式，可选：
            - 'auto'：自动选择（默认）
            - 'polling'：指数退避轮询
            - 'async'：异步协程模式
        debug: 调试模式（立即返回当前状态）
    """
    if timeout <= 0:
        raise ValueError("Timeout must be positive")    
    if debug:
        return _immediate_check(path)
    if mode == 'auto':
        mode = 'async' if timeout > 60 else 'polling'    
    try:
        if mode == 'async':
            return asyncio.run(_async_wait(path, timeout))
        elif mode == 'polling':
            return _polling_wait(path, timeout)
        else:
            raise ValueError(f"Invalid mode: {mode}")
    except Exception as e:
        logger.error(f"Smart wait failed: {str(e)}")
        return False
def _immediate_check(path: str) -> bool:
    if not os.path.exists(path):
        logger.info(f"[DEBUG] File not exists: {path}")
        return False    
    try:
        if path.lower().endswith('.nc'):
            with nc.Dataset(path) as ds:
                if not ds.variables:
                    logger.info(f"[DEBUG] Empty NetCDF: {path}")
                    return False
        logger.info(f"[DEBUG] File valid: {path}")
        return True
    except Exception as e:
        logger.info(f"[DEBUG] Invalid file {path}: {str(e)}")
        logger.info(f"DEBUG {path} is missing")        
        return False

async def _async_wait(path: str, timeout: Union[int, float]) -> bool:    
    async def _check():
        logger.info(f"_async_wait {path} {timeout}")
        while True:
            if os.path.exists(path):
                try:
                    if path.lower().endswith('.nc'):
                        with nc.Dataset(path) as ds:
                            print(ds)
                            if ds.variables:
                                logger.info(f"_async_wait {path} waited ")
                                return True
                    else:
                        logger.info(f"_async_wait {path} waited ")
                        return True
                except Exception:
                    # return False
                        pass
            await asyncio.sleep(1)    
    try:
        return await asyncio.wait_for(_check(), timeout)
    except asyncio.TimeoutError:
        logger.info(f"_async_wait {path} is missing")
        return False

def _polling_wait(path: str, timeout: Union[int, float]) -> bool:
    logger.info(f"_polling_wait  {path} {timeout}")
    wait_sec = 1
    start_time = time.time()    
    while (time.time() - start_time) < timeout:
        if os.path.exists(path):
            try:
                if path.lower().endswith('.nc'):
                    with nc.Dataset(path) as ds:
                        if ds.variables:
                            logger.info(f"_polling_wait {path} waited ")
                            return True
                else:
                    logger.info(f"_polling_wait {path} waited ")
                    return True
            except Exception as e:
                logger.warning(f"File validation failed: {str(e)}")        
        elapsed = time.time() - start_time
        remaining = timeout - elapsed
        next_wait = min(wait_sec, remaining)        
        if next_wait <= 0:
            break            
        time.sleep(next_wait)
        wait_sec = min(wait_sec * 2, 60)  # 上限60秒    
    logger.info(f"_polling_wait {path} is missing")
    return False

"""
# 基本用法（自动选择最佳模式）
success = smart_wait("/data/sample.nc", timeout=120,mode="async")
1. flag = smart_wait(path, timeout=60,mode="async")
2.flag = True if os.path.exists(path) else smart_wait(path, timeout=60,mode="async")

# 强制使用watchdog模式
success = smart_wait("/data/sample.nc", mode='watchdog')

# 调试模式
print(smart_wait("/data/sample.nc", debug=True))

"""
import time
from typing import List, Optional
import glob
def waitFiles(pattern,next=180,interval=5,alls = 1) -> Optional[List[str]]:
    logger.info(f"_polling_wait {pattern} waiting {next} ")
    for _ in range(next):
        if files := glob.glob(pattern):
            if len(files)>alls:
                logger.info(f"_polling_wait {files[0]} waited ")
                return files
        else:            
            time.sleep(interval)
            continue
    return None

"""
waitFiles(pattern,timeout=180,interval=5)
"""
 
import time, glob, os
from typing import Optional, Tuple, List
def checkSize(pattern: str,size_mb: float = 50.0,timeout: int = 180,interval: int = 5) -> Optional[List[str]]:  
    size = size_mb * 1024 * 1024
    logger.info(f"_polling_wait {pattern} waiting {timeout} size {size}")
    for _ in range(timeout // interval):
        if files := [f for f in glob.glob(pattern) if os.path.isfile(f)]:
            if large := [f for f in files if os.path.getsize(f) > size]:
                return large   
            time.sleep(interval)    
    return None  
"""
checkSize(pattern: str,size_mb: float = 50.0,timeout: int = 180,interval: int = 5)
""" 

import os
import time
def is_process_alive(pid):
    try:
        os.kill(pid, 0)  
        return True
    except OSError:
        return False
def check_lock(lock_file):
    if not os.path.exists(lock_file):
        return False    
    try:
        with open(lock_file, 'r') as f:
            content = f.read().strip()        
        if 'process_id:' in content and 'create_time:' in content:
            pid_str = content.split('process_id:')[1].split(',')[0]
            pid = int(pid_str)            
            if not is_process_alive(pid):
                print(f"进程 {pid} 已消亡，清理锁文件")
                os.remove(lock_file)
                return False 
            else:
                print(f"进程 {pid} 仍在运行，跳过执行")
                return True                
    except Exception as e:
        print(f"锁文件解析错误，清理: {e}")
        os.remove(lock_file)
        return False    
    return False
"""
if  check_lock(lock_file):
    return False
"""

import numpy as np
from typing import Union
def check_nans(data=None, threshold= 0.5) -> bool:
    if not isinstance(data, np.ndarray):
        try:
            data = data.cpu().numpy()
        except RuntimeError as e:
            logger.info(f"Tensor转换失败: {str(e)}")
            return False
    elif not isinstance(data, np.ndarray):
        return False
    if data.ndim == 2:
        data = data[np.newaxis, ...]  
    elif data.ndim != 3:
        return False
    try:
        return any(
            (nan_ratio := np.isnan(channel).mean()) > threshold
            and (logger.warning(f"Channel {i} exceeds threshold: {nan_ratio:.4%} > {threshold:.4%}") or True)
            for i, channel in enumerate(data)
        )
    except Exception as e:
        logger.info(f"NaN检查出错: {str(e)}")
        logger.info(traceback.format_exc())
        return False
"""
        flagnan = check_nans(satdata,threshold=0)
        if flagnan:
            # plotA2b(satdata[:3],satdata[3:])
            radio = np.isnan(satdata).sum()/satdata.size    
            if radio>0.0001 and radio <0.01:
                plotA2b(satdata[:3],satdata[3:],saveDir="plotA2bN")
            return 
"""

import time 
import shutil
import traceback
def safe_delete(path_pattern):
    for path in glob.glob(path_pattern):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(traceback.format_exc())
            logger.warning(f"删除失败 {path}: {e}")
"""
            if os.path.exists(zip_file):
                safe_delete(zip_file)
"""


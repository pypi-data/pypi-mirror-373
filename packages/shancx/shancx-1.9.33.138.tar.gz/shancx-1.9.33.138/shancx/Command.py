

import subprocess
import logging
from shancx.NN import setlogger
logger = setlogger(level=logging.INFO)
def runcommand(cmd, timeout= 300) -> bool:
    try:
        result = subprocess.run(
            cmd,
            shell=True,  # 关键修改
            timeout=timeout,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  
        )
        if result.stdout:
            logger.info(f"Command output:\n{result.stdout}")
        if result.stderr:
            logger.info(f"Command error output:\n{result.stderr}")        
        logger.info("Command succeeded!")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout after {timeout} seconds! File may be too large or network is slow.")
        return False
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else "Unknown error"
        logger.error(f"Download failed! Return code: {e.returncode}, Error: {error_msg}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False
"""
allDf.dtypes

vim ~/.bash_history
git checkout main  -- /home/scx/mqpf_pmsc/backup/of_ref_pre.py
du -sh * | sort -h
rsync -avid scx@10.1.98.7:/home/scx/test/project   ./
rsync -avid scx@10.1.98.7:/home/scx/ESRGAN-PyTorch-main /home/scx/test/   整个文件夹以及文件夹下
find . -type f -name "project1.log*" -exec rm -f {} \;
find . -type f -name "project*.log*" -exec rm -f {} \;
sudo nvidia-smi -i 2 -pm 0
ssh scx@10.1.98.7     cmd 链接
   
grep users /etc/group
sudo groupdel scx
sudo useradd -u 1015 -g 1015 scx
id scx


more /etc/passwd  

sudo usermod -g users scx
sudo groupdel users1
sudo groupadd -g 1015 scx
sudo usermod -g 1015 scx
id scx
grep scx /etc/group
sudo chown -R scx:scx /mnt/wtx_weather_forecast/scx/mqpf_0722_wtyN/
ssh-keygen -t rsa -b 4096 -C "shanhe12@163.com"  
cat id_rsa111.pub   >>  /home/scx/.ssh/authorized_keys   centos 链接ssh秘钥链接问题用升级为ubuntu22.04
df  -h
data_r_com = np.max([data_r_700, data_r_850], axis=0)
traceback.format_exc()
np.unique(pre, return_counts=True)
data = instantiate_from_config(config.data) 类动态传参
id scx
sudo usermod -u 1015 scx
sudo groupmod -g 1015 scx
systemctl | grep scx
sudo loginctl terminate-user scx
sudo pkill -9 -u scx
.gitignore
pip.conf
w
python main.py -h
export  CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
cuda:0  export CUDA_VISIBLE_DEVICES=7,1,2,3,4,5,6,0  
tmux kill-session -t 1
passwd
pgrep -u scx | wc -l
sudo chmod -R u+w /mnt/wtx_weather_forecast/scx/sever7/exam/.git/objects   ls -l  
rsync -avid scx@10.1.98.5: 
echo 'alias pgrep="pgrep -u $(whoami) | wc -l"' >> ~/.bashrc   source ~/.bashrc
netstat -antp
netstat -antp | grep 140.90.101.79:443 | wc -l
ps aux|grep scx
ssh-keygen -t rsa -b 4096
export PATH="/home/scx1/miniconda3/bin:$PATH"
for i in reversed(range(n_steps)):
Every letter and function needs to be understood, and the best way is easy to learn
nano /home/scx1/miniconda3/envs/mqpf/bin/pip   
/home/scx1/miniconda3/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/  copy  simhei.ttf  rm -rf .cache .cache/matplot/*
chmod -R u+w ./sever7/mqpf_pmsc/.git/objects/  cannot create regular file './sever7/mqpf_pmsc/.git/objects/: Permission denied
vim 10w 2b ?scx
pip install git+
git config --global user.email "shanhe12@163.com"
git config --global user.name "shancx"
df.loc['Average'] = averages
df.at['Average', 'time1'] = 'Average'
conda init bash && source ~/.bashrc    init bash
export CUDA_HOME=$CONDA_PREFIX
export PATH=$CUDA_HOME/bin:$PATH   .bash or  conda init bash && source ~/.bashrc   
unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=""
hostname -I
locate libcublasLt.so.11  Could not load library libcublasLt.so.11. Error: libcublasLt.so.11: cannot open shared object file: No such file or directory  libcublasLt 是 cuBLAS 库的一个扩展  cudatoolkit 安装
nano /home/scx1/miniconda3/envs/mqpf/bin/nvitop
DS_BUILD_FUSED_LAMB=1 pip install deepspeed
DS_BUILD_OPS=1 pip install deepspeed
xception has occurred: SystemExit (note: full exception trace is shown but execution is paused at: _run_module_as_main)
CST.strftime("%Y%m%d%H%M")
TypeError: 'module' object is not callable   
MAILTO="shanhe12@163.com"
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3,4,5,6,7"
python setup.py sdist bdist_wheel
twine upload dist/*
pip install setuptools twine
wmic bios get serialnumber
wmic diskdrive get serialnumber
"""
"""
sudo chmod a+w /mnt/wtx_weather_forecast/scx/MSG/MSG_Data/2025/20250612/    多人文件夹权限
"""
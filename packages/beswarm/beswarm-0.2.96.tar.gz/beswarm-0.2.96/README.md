# beswarm

beswarm: be swarm

beswarm is a tool for creating a swarm of agents to complete a task.

## 任务

```
DiT-Air 架构与MMDiT和PixArt的区别是什么？详细分析三个模型的架构，并给出代码实现。
```

```
arXiv:2502.14831v2 和 arXiv:2503.10618v2 的 渐进式 VAE 训练方法有一定的相似性，请详细分析这两种方法的异同，底层原理的异同。
```

```
论文地址：'/Users/yanyuming/Library/Mobile Documents/iCloud~QReader~MarginStudy~easy/Documents/论文/EQ-VAE Equivariance Regularized Latent Space for Improved Generative Image Modeling.pdf'
仓库地址：https://github.com/zelaki/eqvae
```

```
论文地址：'/Users/yanyuming/Library/Mobile Documents/iCloud~QReader~MarginStudy~easy/Documents/论文/Vector Quantized Diffusion Model for Text-to-Image Synthesis.pdf'

查看代码库，我需要将论文的公式，代码，理论，实验结果，总结，形成一个文档。请进行彻底的分析。

找到每一个数学概念对应的代码实现。整理成文档保存到本地。
```

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t yym68686/beswarm:latest --push .
docker pull yym68686/beswarm
```

```bash
cd ~/Downloads/GitHub/beswarm && docker run --rm \
--env-file .env \
-v ./work:/app/work beswarm \
--goal "分析这个仓库 https://github.com/cloneofsimo/minRF"
```

测试 docker 是否可以用 GPU：

```bash
docker run --gpus all -it --rm --entrypoint nvidia-smi yym68686/beswarm

docker run -it --rm --entrypoint cat yym68686/beswarm /app/beswarm/aient/src/aient/models/chatgpt.py
```

beswarm docker debug 命令

```bash
cd /Users/yanyuming/Downloads/GitHub/beswarm
docker run --rm -it \
--network="host" \
--env-file .env \
-v ./work/test:/app/work yym68686/beswarm \
--goal '帮我写一个简单的python脚本打印hello world' /bin/bash
```

服务器安装

```bash
pip install pipx
pipx ensurepath
source ~/.bashrc
pipx install nvitop
pip install beswarm -i https://pypi.tuna.tsinghua.edu.cn/simple

# 升级 从海外官方 pypi 升级
pip install --upgrade beswarm -i https://pypi.org/simple
pip install --upgrade beswarm -i https://pypi.tuna.tsinghua.edu.cn/simple
```

main.py

```python
import os
import asyncio
import nest_asyncio
nest_asyncio.apply()

from beswarm.tools import (
    worker,
    get_code_repo_map,
    search_arxiv,
    read_file,
    list_directory,
    excute_command,
    write_to_file,
    download_read_arxiv_pdf,
)

os.environ['API_KEY'] = ''
os.environ['BASE_URL'] = 'https://api.xxx.xyz/v1/chat/completions'
os.environ['MODEL'] = 'gemini-2.5-pro'

# 设定任务目标
goal = """

"""
work_dir = '/work_dir'

tools = [read_file, list_directory, write_to_file, excute_command, search_arxiv, download_read_arxiv_pdf, get_code_repo_map]
asyncio.run(worker(goal, tools, work_dir))
```

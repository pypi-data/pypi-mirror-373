# TorTitle

一个用于从种⼦标题中解析电影、剧集信息的 Python 库，支持主标题和副标题的提取。

## 安装

```bash
pip install tortitle
```

## 使用方法

### 解析主标题

`TorTitle` 用于解析种⼦标题，并提取主要信息，例如标题、年份、季数、集数、分辨率等。

```python
from tortitle import TorTitle
torrent_name = "The.Mandalorian.S01E01.1080p.WEB-DL.DDP5.1.H.264-NTC"
title = TorTitle(torrent_name)

print(f"标题: {title.title}")
print(f"中文标题: {title.cntitle}")
print(f"年份: {title.year}")
print(f"季: {title.season}")
print(f"集: {title.episode}")
print(f"分辨率: {title.resolution}")
print(f"片源: {title.media_source}")
print(f"制作组: {title.group}")

# another example
torrent_name = "[美国][金钱世界][All.the.Money.in.the.World.2017.1080p.BluRay.x264.DTS.5.1-CMCC][中英字幕]"
print(TorTitle(torrent_name).to_dict())
# 输出：
# {'title': 'All the Money in the World', 'cntitle': '金钱世界', 'year': '2017', 'type': 'movie', ....}
```

### 解析副标题

`TorSubtitle` 用于从 PT 站的种⼦副标题中提取`可能是标题`的信息(这里叫extitle)，以及season, episode等。

```python
from tortitle import TorSubtitle
torrent_name = "舌尖上的中国 第一季 | 全7集 | 导演: 陈晓卿 | 主演: 李立宏 国语/中字 4K高码版"
subtitle = TorSubtitle(torrent_name)

print(f"副标题: {subtitle.extitle}")
print(f"季: {subtitle.season}")
print(f"集: {subtitle.episode}")
```

## Contribution

欢迎提交 Pull Request

## License

[MIT](https://choosealicense.com/licenses/mit/)
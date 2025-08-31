import requests
from io import BytesIO
from PIL import Image
import os
import random

try:
    from IPython.display import display
except ImportError:
    display = None


class AnimeGifViewer:
    """
    随机动漫动图查看器
    """

    GIPHY_API_KEY = "dc6zaTOxFJmzC"  # Giphy 测试 Key
    GIPHY_SEARCH_ENDPOINT = "https://api.giphy.com/v1/gifs/search"

    def __init__(self):
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".anime_gif_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_random_gif_url(self, query="anime"):
        """
        从 Giphy 获取随机动漫 GIF URL
        """
        params = {
            "api_key": self.GIPHY_API_KEY,
            "q": query,
            "limit": 50,
            "rating": "g"
        }
        resp = requests.get(self.GIPHY_SEARCH_ENDPOINT, params=params)
        data = resp.json()
        if "data" not in data or len(data["data"]) == 0:
            raise Exception("没有找到 GIF")
        gif = random.choice(data["data"])
        return gif["images"]["original"]["url"]

    def show_gif(self, url=None, query="anime"):
        """
        显示 GIF
        如果未提供 URL，则随机获取
        """
        if url is None:
            url = self.get_random_gif_url(query)

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("下载失败")

        gif_data = BytesIO(response.content)

        if display:
            img = Image.open(gif_data)
            display(img)
        else:
            # 本地保存并用默认程序打开
            path = os.path.join(self.cache_dir, "temp.gif")
            with open(path, "wb") as f:
                f.write(response.content)
            os.system(f'start "" "{path}"' if os.name == 'nt' else f'xdg-open "{path}"')

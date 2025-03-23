import requests
from bs4 import BeautifulSoup
import time
import os

class BlueArchiveWikiCrawler:
    def __init__(self):
        self.base_url = "https://bluearchive.wiki"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_page(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"获取页面失败: {url}")
            print(f"错误: {e}")
            return None

    def get_episode_content(self, url):
        soup = self.get_page(url)
        if not soup:
            return None
        
        content = []
        # 获取对话内容区域
        story_container = soup.find('div', {'class': 'story-container'})
        if story_container:
            # 获取所有对话行
            for row in story_container.find_all('tr'):
                # 获取包含角色名和台词的td
                dialog_td = row.find_all('td')[-1]  # 取最后一个td，它包含对话内容
                
                if dialog_td:
                    name = dialog_td.find('div', {'class': 'story-student-name'})
                    line = dialog_td.find('div', {'class': 'story-student-line'})
                    
                    if name and line:
                        name_text = name.get_text().strip()
                        line_text = line.get_text().strip()
                        if name_text and line_text:
                            content.append(f"{name_text}: {line_text}")
        
        return '\n'.join(content)

    def get_volume_episodes(self, volume):
        url = f"{self.base_url}/wiki/Main_Story/Volume_{volume}"
        soup = self.get_page(url)
        if not soup:
            return []

        episodes = []
        # 查找所有包含 Episode 链接的元素
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'Episode' in href and 'Main_Story/Volume' in href:
                episodes.append(f"{self.base_url}{href}")
        
        return episodes

    def crawl_all_content(self):
        volumes = ['0', '1', '2', '3', '4', '5', 'F']
        # volumes = ['0']
        for volume in volumes:
            print(f"正在爬取 Volume {volume}...")
            episodes = self.get_volume_episodes(volume)
            
            for episode_url in episodes:
                print(f"正在处理: {episode_url}")
                content = self.get_episode_content(episode_url)
                
                if content:
                    # 从URL中提取文件名
                    filename = episode_url.split('/')[-4:]
                    filename = '_'.join(filename) + '.txt'
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"已保存: {filepath}")
                    # 添加延迟以避免请求过于频繁
                    time.sleep(1)

def main():
    crawler = BlueArchiveWikiCrawler()
    crawler.crawl_all_content()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
靳涵IP内容仪表盘 - 数据采集脚本
采集源: B站热门(bilibili API) + 百度热搜(百度API)
输出: trends_data.json
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime

def fetch_json(url, headers=None, timeout=15):
    """获取 JSON 数据"""
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_bilibili_popular():
    """获取 B站 综合热门视频"""
    try:
        data = fetch_json('https://api.bilibili.com/x/web-interface/popular?ps=30')
        if data.get('code') != 0:
            print(f"  B站API返回错误: {data.get('message')}")
            return []
        
        videos = []
        for item in data.get('data', {}).get('list', [])[:20]:
            videos.append({
                'title': item.get('title', ''),
                'author': item.get('owner', {}).get('name', ''),
                'bvid': item.get('bvid', ''),
                'play': item.get('stat', {}).get('view', 0),
                'danmaku': item.get('stat', {}).get('danmaku', 0),
                'tag': item.get('tname', ''),
                'pic': item.get('pic', ''),
                'duration': item.get('duration', ''),
            })
        return videos
    except Exception as e:
        print(f"  B站采集失败: {e}")
        return []

def fetch_bilibili_ranking():
    """获取 B站 排行榜"""
    try:
        data = fetch_json('https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all')
        if data.get('code') != 0:
            print(f"  B站排行API返回错误: {data.get('message')}")
            return []
        
        videos = []
        for item in data.get('data', {}).get('list', [])[:20]:
            videos.append({
                'title': item.get('title', ''),
                'author': item.get('owner', {}).get('name', ''),
                'bvid': item.get('bvid', ''),
                'play': item.get('stat', {}).get('view', 0),
                'danmaku': item.get('stat', {}).get('danmaku', 0),
            })
        return videos
    except Exception as e:
        print(f"  B站排行采集失败: {e}")
        return []

def fetch_baidu_hot():
    """获取百度热搜"""
    try:
        # 百度热搜API
        data = fetch_json('https://top.baidu.com/board?tab=realtime', headers={
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://top.baidu.com/',
        })
        # 百度返回的是HTML，需要从HTML中提取JSON
        # 改用备用API
        raise Exception("备用方案")
    except:
        pass
    
    try:
        # 使用百度热搜API (v2)
        url = 'https://top.baidu.com/api/board?platform=wise&tab=realtime'
        data = fetch_json(url)
        items = []
        cards = data.get('data', {}).get('cards', [])
        for card in cards:
            # 百度卡片结构: card.content 是外层列表，内层 content 才是热搜条目
            for outer_item in card.get('content', []):
                inner_list = outer_item.get('content', [])
                for item in inner_list[:50]:
                    items.append({
                        'title': item.get('word', item.get('query', '')),
                        'score': item.get('hotScore', item.get('heat_score', item.get('hotTag', 0))),
                        'is_top': item.get('isTop', False),
                        'url': item.get('url', ''),
                        'desc': item.get('desc', ''),
                    })
        return items
    except Exception as e:
        print(f"  百度热搜采集失败: {e}")
    
    # 最终备用：用web搜索
    return []

def fetch_bing_news():
    """获取行业趋势报道"""
    # Bing News 在国内墙内可能无法访问，返回空
    return {
        '体育': [],
        '科技': [],
        '文创': [],
        '消费': [],
    }

def main():
    print("🔍 开始采集热点数据...")
    
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'collected_at': datetime.now().isoformat(),
        'sources': {}
    }
    
    # B站热门
    print("📺 采集 B站热门...")
    bili_popular = fetch_bilibili_popular()
    result['sources']['bilibili_popular'] = bili_popular
    print(f"   获取到 {len(bili_popular)} 条")
    
    # B站排行
    print("📊 采集 B站排行榜...")
    bili_ranking = fetch_bilibili_ranking()
    result['sources']['bilibili_ranking'] = bili_ranking
    print(f"   获取到 {len(bili_ranking)} 条")
    
    # 百度热搜
    print("🔍 采集百度热搜...")
    baidu_hot = fetch_baidu_hot()
    result['sources']['baidu_hot'] = baidu_hot
    print(f"   获取到 {len(baidu_hot)} 条")
    
    # Bing News
    print("📰 采集行业趋势...")
    bing_news = fetch_bing_news()
    result['sources']['bing_news'] = bing_news
    
    # 写入文件
    output_path = '/home/meinv/trends-jinhan/trends_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到 {output_path}")
    print(f"   总计: B站热门 {len(bili_popular)} + B站排行 {len(bili_ranking)} + 百度 {len(baidu_hot)} 条")
    
    return result

if __name__ == '__main__':
    main()

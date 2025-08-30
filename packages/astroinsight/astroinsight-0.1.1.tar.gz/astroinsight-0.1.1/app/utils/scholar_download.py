#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/8/21 9:58
# @Author : 桐
# @QQ:1041264242
# 注意事项：

import json
import os
import re
import arxiv
import requests
from bs4 import BeautifulSoup
import urllib.parse
from scihub_cn.scihub import SciHub
from app.core.config import OUTPUT_PATH, Proxies


### 下载PDF的保存路径

def check_pdf(file_path):
    """
    检查PDF文件是否能正常打开。

    参数:
    file_path (str): PDF文件路径。

    返回:
    bool: 如果文件能正常打开则返回True，否则返回False。
    """
    try:
        with open(file_path, 'rb') as f:
            # 读取文件的前5个字节，PDF文件通常以"%PDF-"开头
            # 这里我们读取5个字节是因为"%PDF-"是5个字节（包括百分号）
            header = f.read(5)
            # 检查文件开头是否为"%PDF-"（PDF文件的魔数）
            if header != b'%PDF-':
                # 如果不是PDF开头，则抛出异常
                print("File does not start with PDF header.")
                return False
            # 如果需要，可以在这里添加更多的检查逻辑
            return True
    except Exception as e:
        print(f"Error opening PDF file {file_path}: {e}")
        return False


def sanitize_folder_name(folder_name):
    # 定义需要替换的违规字符集
    illegal_chars = r'<>:"/\\|\?*'
    # 使用正则表达式替换违规字符为下划线 _
    sanitized_name = re.sub(f'[{illegal_chars}]', '_', folder_name)
    return sanitized_name


def search_google_scholar(doi):
    # Google Scholar的搜索URL
    search_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(doi)}"

    # 模拟请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers, proxies=Proxies)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找包含[PDF]文本的链接
    pdf_links = []
    for link in soup.find_all('a'):
        if '[PDF]' in link.get_text():
            pdf_links.append(link['href'])

    # 输出找到的链接
    for pdf_link in pdf_links:
        print(pdf_link)
        return pdf_link


def download_pdf_from_google(pdf_url, title, output_path):
    save_path = f"{output_path}/{title}.pdf"

    # 发送HTTP GET请求来获取PDF文件
    response = requests.get(pdf_url, stream=True, proxies=Proxies)
    # response = requests.get(url, stream=True)
    # 检查请求是否成功
    response.raise_for_status()
    # 以二进制模式写入文件
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return save_path


def download_pdf_from_scihub(doi, output_path):
    sh = SciHub(proxy=Proxies)
    # save_path = sh.download({"doi": doi}, destination=output_path, is_translate_title=False)
    try:
        # 设置is_translate_title可将paper's title进行翻译后下载存储
        save_path = sh.download({"doi": doi}, destination=output_path, is_translate_title=False)
    except:
        save_path = None

    # print(result)
    return save_path


def download_pdf_from_unpaywall(doi, title, output_path, email="z1041264242@gmail.com"):
    print(f"\033[1;32m | INFO     | Getting paper from unpaywall: ... \033[0m")
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    response = requests.get(api_url, proxies=Proxies)

    if response.status_code == 200:
        data = response.json()
        oa_location = data.get("best_oa_location")
        if oa_location and oa_location.get("url_for_pdf"):
            pdf_url = oa_location["url_for_pdf"]
            pdf_data = requests.get(pdf_url)
            if pdf_data.status_code == 200:
                file_name = fr"{title}.pdf"
                file_path = os.path.join(output_path, file_name)
                with open(file_path, "wb") as f:
                    f.write(pdf_data.content)
                return file_path
    return None


def download_pdf_from_arxiv(doi, title, output_path):
    """
    根据 Titel 从 arXiv 下载 PDF（前提是该 DOI 有对应）
    """
    print(f"\033[1;32m | INFO     | Getting paper from ArXiv: ... \033[0m")

    search_engine = arxiv.Search(
        query=title,
        max_results=1,
        sort_by=arxiv.SortCriterion.Relevance
    )
    for result in search_engine.results():
        pdf_url = result.pdf_url
        pdf_doi = result.doi
        print(result.doi)
        print(pdf_url)
        print(doi)
        if pdf_doi == doi:
            print("ok")
            # 使用流式请求
            with requests.get(pdf_url, proxies=Proxies, stream=True) as r:
                if r.status_code == 200:
                    file_name = fr"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):  # 每次读8KB
                            if chunk:  # 过滤掉 keep-alive 块
                                f.write(chunk)
                    return file_path
    return None


def download_pdf_from_crossref(doi, title, output_path):
    url = f"https://api.crossref.org/works/{doi}"
    headers = {"Accept": "application/json"}
    r = requests.get(url, headers=headers, proxies=Proxies)

    if r.status_code == 200:
        data = r.json()
        # 获取 publisher-hosted PDF 链接（如果有）
        for link in data["message"].get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link["URL"]
                print(pdf_url)
                pdf_data = requests.get(pdf_url)
                if pdf_data.status_code == 200:
                    file_name = fr"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        f.write(pdf_data.content)
                    return file_path
    return None


def getdown_pdf_google_url(doi, title, output_path):
    print(f"\033[1;32m | INFO     | Getting paper from Google: ... \033[0m")

    pdf_url = search_google_scholar(doi)

    if pdf_url:
        print("找到PDF链接:", pdf_url)
        save_path = download_pdf_from_google(pdf_url, title, output_path)
        return save_path
    else:
        print("未找到PDF链接。")
        return False


def download_pdf_from_Giiisp(doi, title, output_path):
    """
    搜索论文API

    参数:
    search_query: 搜索关键词
    count: 搜索数量（最大200）
    sortOrder: 排序顺序 1-降序 2-升序
    sortBy: 排序方式 1-相关性 2-出版日期
    search_type: 搜索类型 1-标题/摘要 2-作者
    """
    print(f"\033[1;32m | INFO     | Getting paper from Giiisp: ... \033[0m")

    # API地址
    url = "https://giiisp.com/first/oaPaper/api/filter"

    # 请求参数
    payload = {
        "count": 5,
        "sortOrder": 1,
        "sortBy": 1,
        "searchQuery": title,
        "searchType": 1
    }

    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "85d7e5806950935fa3bf11f8e017c38f",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # 发送POST请求
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        # 检查响应状态
        response.raise_for_status()

        # 解析JSON响应
        result = response.json()

        if result['data'] != [] and result['data'][0]['giiispPdfUrl'] != None:
            # print(result)
            pattern = r"https?://(dx\.)?doi\.org/"
            pdf_url = result['data'][0]['giiispPdfUrl']
            pdf_doi = re.sub(pattern, "", result['data'][0]['doi'])

            if pdf_doi == doi:
                pdf_data = requests.get(pdf_url)
                if pdf_data.status_code == 200:
                    file_name = fr"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        f.write(pdf_data.content)
                    return file_path
        return None

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None


def download_pdf(doi, title, output_path):
    """
    尝试通过多个方法下载 PDF 文件。
    成功则返回文件路径，失败则返回 None。
    """
    download_methods = [
        lambda: download_pdf_from_arxiv(doi, title, output_path),
        lambda: download_pdf_from_Giiisp(doi, title, output_path),
        lambda: download_pdf_from_unpaywall(doi, title, output_path),
        lambda: getdown_pdf_google_url(doi, title, output_path),
        lambda: download_pdf_from_scihub(doi, output_path),
    ]

    for method in download_methods:
        result = method()
        if result and check_pdf(result):
            print(f"\033[1;32m | INFO     | Getting paper: Success \033[0m")
            return result
        print(f"\033[1;31m | INFO     | Getting paper: Failed \033[0m")

    return None


def download_all_pdfs(dois, title, topic, user_id, task):
    """
    下载给定DOI列表中的PDF文件。

    参数:
    dois (list): 包含若干个DOI的列表。

    返回:
    list: 包含所有下载结果的列表，每个元素是对应DOI的下载结果信息。
    """

    output_path = fr"{OUTPUT_PATH}/{user_id}/{task.id}/{topic}/Paper/pdf"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print(f"\033[1;32m | INFO     | Getting paper, doi:{dois}, title:{title} \033[0m")
    paper_pdf = download_pdf(dois, sanitize_folder_name(title), output_path)

    #返回的是下载后pdf的路径

    return paper_pdf


if __name__ == "__main__":
    print(os.environ)
    dois = '10.1088/1674-4527/19/9/133'
    download_all_pdfs(dois=dois, title='Pulsar Candidates Classification with Deep Convolutional Neural Networks',
                      topic='pulsar candidate classification')

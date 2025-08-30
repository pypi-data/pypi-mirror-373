#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/8/21 12:04
# @Author : 桐
# @QQ:1041264242
# 注意事项：
"""
该文件用于调用PDF转换为Markdown格式的方法
"""

from app.core.config import MinerU_Token, OUTPUT_PATH
import re
import time
import zipfile
import pandas as pd
import requests
import os


def download_zip_file(url, zip_save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(zip_save_path, 'wb') as file:
            file.write(response.content)
        print(f"ZIP 文件已下载到: {zip_save_path}")
    else:
        print(f"无法下载 ZIP 文件，状态码: {response.status_code}")


def find_md_files_in_zip(zip_path, copy_path, batch_id):
    md_files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.md'):
                md_files.append(file)
        if md_files:
            print("在 ZIP 文件中找到的 MD 文件")
            for md_file in md_files:
                # 提取文件到指定目录
                extracted_path = zip_ref.extract(md_file, copy_path)
                # 重命名文件
                new_file_path = os.path.join(copy_path, batch_id)
                os.rename(extracted_path, new_file_path)
                print(f"已提取并重命名为: {new_file_path}")
        else:
            print("ZIP 文件中没有找到 MD 文件")
    return md_files


def extract_pdf_name(path):
    # 使用正则表达式提取 PDF 文件名称
    match = re.search(r"([^\\]+)\.pdf$", path, re.IGNORECASE)

    if match:
        pdf_name = match.group(1)
        print("提取的 PDF 文件名称:", pdf_name)
    else:
        print("未找到 PDF 文件名称")
    return pdf_name


def download_file_mineruapi(batch_id, topic, user_id, task):
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task.id}/{topic}/Paper"
    while True:
        url = f'https://mineru.net/api/v4/extract-results/batch/{batch_id}'
        token = MinerU_Token
        header = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {token}"
        }
        res = requests.get(url, headers=header)
        print(res.json())

        if res.json()["data"]["extract_result"][0]["state"] == "done":
            # 文件转换成功，保存base64编码的数据到文件
            directory = fr"{file_path_prefix}/markdown"
            zip_dir = fr"{file_path_prefix}/zip"
            if not os.path.exists(directory):
                os.makedirs(directory)
            if not os.path.exists(zip_dir):
                os.makedirs(zip_dir)

            download_zip_file(url=res.json()["data"]["extract_result"][0]["full_zip_url"],
                              zip_save_path=zip_dir + fr"/{batch_id}.zip")
            find_md_files_in_zip(zip_path=zip_dir + f"/{batch_id}.zip", copy_path=directory, batch_id=f"{batch_id}.md")
            break

        elif res.json()["data"]["extract_result"][0]["state"] == "waiting-file" or res.json()["data"][0][
            "state"] == "running":
            print("File is still processing or waiting. Retrying in 5 seconds...")
            time.sleep(5)  # 等待5秒后重试
        else:
            print("Error downloading file:", res.json()["data"]["state"], "batch_id:", batch_id)
            break


def pdf2md_mineruapi(file_path, topic, user_id, task):
    # 读取 Excel 文件，如果不存在则创建
    down_history = fr"{OUTPUT_PATH}/{user_id}/{task.id}/{topic}/down_history.xlsx"
    # 检查目录是否存在，不存在则创建
    os.makedirs(os.path.dirname(down_history), exist_ok=True)
    # 检查文件是否存在，不存在则创建空的DataFrame并保存为Excel
    if not os.path.exists(down_history):
        pd.DataFrame().to_excel(down_history, index=False)
    df = pd.read_excel(down_history)
    pdf_name = extract_pdf_name(path=file_path)
    # 遍历每一行
    for index, row in df.iterrows():
        if row['Paper'] == pdf_name:
            download_file_mineruapi(batch_id=row['Batch_ID'], topic=topic, user_id=user_id, task=task)
            return row['Batch_ID']

    url = 'https://mineru.net/api/v4/file-urls/batch'
    token = MinerU_Token
    header = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }
    data = {
        "enable_formula": True,
        "language": "en",
        "layout_model": "doclayout_yolo",
        "enable_table": True,
        "files": [
            {"name": file_path, "is_ocr": True, "data_id": "abcd"}
        ]
    }
    try:
        response = requests.post(url, headers=header, json=data)
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 0:
                batch_id = result["data"]["batch_id"]
                urls = result["data"]["file_urls"]

                with open(file_path, 'rb') as f:
                    res_upload = requests.put(urls[0], data=f)

                if res_upload.status_code == 200:
                    print("upload success")
                else:
                    print("upload failed")
                download_file_mineruapi(batch_id=batch_id, topic=topic, user_id=user_id, task=task)
                # 创建新行的数据（假设你要添加一行数据）
                new_row = {'Paper': pdf_name, 'Batch_ID': batch_id}  # 替换为你的新行数据
                # 将新行添加到 DataFrame 中
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                # 保存修改后的 DataFrame 回原始文件
                df.to_excel(down_history, index=False)
                return batch_id
            else:
                print('apply upload url failed,reason:{}'.format(result.msg))
        else:
            print('response not success. status:{} ,result:{}'.format(response.status_code, response))
    except Exception as err:
        print(err)

    return 0

# print(pdf2md_mineruapi(file_path="..\\Temp\\pulsar candidate classification\\Paper\\pdf\\AnomalyR1_ A GRPO-based End-to-end MLLM for Industrial Anomaly Detection.pdf",topic="pulsar candidate classification"))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/8/19 16:08
# @Author : 桐
# @QQ:1041264242
# 注意事项：
import os
import re

from app.core.prompt import get_related_keyword_prompt, paper_compression_prompt, extract_entity_prompt, \
    extract_tec_entities_prompt, review_mechanism_prompt
from app.utils.llm_api import call_with_deepseek, call_with_deepseek_jsonout, call_with_qwenmax
from app.utils.arxiv_api import search_paper
from app.utils.scholar_download import download_all_pdfs
from app.utils.pdf_to_md import pdf2md_mineruapi
from app.utils.wiki_search import get_description, search
from app.core.config import OUTPUT_PATH, graph
import ast


def SearchKeyWordScore(Keywords):
    print(f"\033[1;32m | INFO     | calculate Keyword score... \033[0m")

    for index, keyword in enumerate(Keywords):
        entity = keyword['entity']

        # 定义Cypher查询语句
        query = f"""
        MATCH (n:Words)
        WHERE n.other CONTAINS '\\'{entity}\\'' OR n.name = '{entity}'
        RETURN n.count,n
        ORDER BY n.count DESC
        LIMIT 1
        """

        # 执行查询并获取结果
        nodes = graph.run(query).data()

        if len(nodes) != 0:
            Keywords[index]['count'] = nodes[0]['n.count']
        else:
            Keywords[index]['count'] = 0

    # 计算最小和最大count值
    min_count = min(item['count'] for item in Keywords)
    max_count = max(item['count'] for item in Keywords)

    # 权重分配
    weight_importance = 0.4
    weight_count = 0.6

    # 计算综合得分
    for item in Keywords:
        normalized_count = (item['count'] - min_count) / (max_count - min_count)
        composite_score = (item['importance_score'] * weight_importance) + (normalized_count * weight_count)
        item['composite_score'] = composite_score

        # 排序并输出结果（可选）
    sorted_data = sorted(Keywords, key=lambda x: x['composite_score'], reverse=True)

    print(f"\033[1;32m | INFO     | calculate Keyword score:OK!\n{sorted_data} \033[0m")

    return sorted_data


def get_related_keyword(Keyword):
    print(f"\033[1;32m | INFO     | geting related keyword... \033[0m")
    user_prompt = get_related_keyword_prompt(Keyword=Keyword)
    result = call_with_deepseek(system_prompt="You are a helpful assistant.", question=user_prompt)

    print(f"\033[1;32m | INFO     | The related keyword is :{result} \033[0m")

    print(f"\033[1;32m | INFO     | geting related keyword:OK! \033[0m")

    return ast.literal_eval(result)


def remove_number_prefix(paragraph):
    # # 定义一个正则表达式模式，用于匹配句子开头的数字和随后的句点空格
    # pattern = r'^\d+\. '
    # # 利用re.sub函数，将匹配到的部分替换为空字符串，以此移除它
    # modified_sentence = re.sub(pattern, '', sentence)
    # return modified_sentence
    # 定义一个正则表达式模式，用于匹配句子开头的数字和随后的句点空格
    pattern = r'^\d+\. |(?<=\n)\d+\. '
    # 利用re.sub函数，将匹配到的部分替换为空字符串，以此移除它
    modified_paragraph = re.sub(pattern, '', paragraph, flags=re.MULTILINE)
    return modified_paragraph


def read_markdown_file(file_path):
    """
    读取指定Markdown文件的内容，并将其打印到控制台。

    参数:
    file_path (str): Markdown文件的路径。
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content

    except FileNotFoundError:
        print(f"\033[1;31m | ERRO     | file can't find: {file_path} \033[0m")
    except IOError as e:
        print(f"\033[1;31m | ERRO     | load file erro: {e} \033[0m")


def extract_hypothesis(file, split_section="Hypothesis"):
    print(f"\033[1;32m | INFO     | extract hypothesis... \033[0m")

    text = read_markdown_file(file)

    # 正则表达式匹配 Hypothesis 后的内容
    pattern = re.compile(fr"{split_section} \d+:(.+?)\n", re.DOTALL)

    # 查找所有匹配项
    matches = pattern.findall(text)

    # 去除每个匹配项前后的空白字符
    hypotheses = [match.strip() for match in matches]

    # # 打印结果
    # for i, hypothesis in enumerate(hypotheses, start=1):
    #     print(f"Hypothesis {i}:\n{hypothesis}\n")

    return hypotheses


def paper_compression(doi, title, topic, user_id, task):
    paper_pdf_path = download_all_pdfs(dois=doi, title=title, topic=topic, user_id=user_id, task=task)
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task.id}/{topic}/Paper"
    directory = fr"{file_path_prefix}/compression"

    task_id = pdf2md_mineruapi(file_path=paper_pdf_path, topic=topic, user_id=user_id, task=task)

    # 匹配任意数量的#号开头后跟References（不区分大小写）及其后所有内容
    pattern = r'#{0,}\s*References.*'

    if task_id != 0:
        paper_content = read_markdown_file(file_path=fr"{file_path_prefix}/markdown/{task_id}.md")
        paper_content = re.sub(pattern, '', paper_content, flags=re.DOTALL | re.IGNORECASE)
    else:
        return 'None'
    system_prompt = paper_compression_prompt()

    # compression_result = call_with_deepseek(question=f"The content is '''{paper_content}'''",system_prompt=system_prompt)
    compression_result = call_with_qwenmax(question=f"The content is '''{paper_content}'''",
                                           system_prompt=system_prompt)

    # directory = fr"{OUTPUT_PATH}/{topic}/Paper/compression"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(fr"{directory}/{task_id}.md", 'w', encoding='utf-8') as f:
        f.write(compression_result)

    return compression_result


def search_releated_paper(topic, max_paper_num=5, compression=True, user_id="", task=None):
    keynum = 0
    relatedPaper = []
    Entities = []

    papers = search_paper(Keywords=[topic], Limit=max_paper_num)

    for paper in papers:
        if compression:
            try:
                print(f"\033[1;32m | INFO     | Getting compressed paper information: {paper['title']} \033[0m")
                compression_result = paper_compression(doi=paper["doi"], title=paper["title"], topic=topic, user_id=user_id, task=task)
                print(
                    f"\033[1;32m | INFO     | Getting compressed paper information: {paper['title']} State: OK! \033[0m")
            except Exception as e:
                print(f"\033[1;31m | ERRO     | compressed paper information: {paper['title']} State: Miss! \033[0m")
                print(f"\033[1;31m | ERROR    | Error details: {str(e)} \033[0m")
                print(f"\033[1;31m | ERROR    | Error type: {type(e).__name__} \033[0m")
                compression_result = "None"
        else:
            compression_result = "None"

        try:
            relatedPaper.append({
                "title": paper["title"],
                "abstract": paper["abstract"],
                "compression_result": compression_result
            })

            for keyword in paper["keyword"]:
                Entities.append(keyword)
        except:
            pass

    Keywords = \
        call_with_deepseek_jsonout(system_prompt=extract_entity_prompt(), question=f"""The content is: {Entities}.""")[
            'keywords']

    keyword_str = ""

    print(f"\033[1;32m | INFO     | Analyzing and processing Keywords:\n{Keywords}\n \033[0m")

    for keyword in Keywords:
        keynum += 1
        temp = get_description(search(query=keyword))
        if not temp:
            print(f"\033[1;31m | Warning     | {keyword}'s description  is empty \033[0m")
            keyword_str += f"{keyword};\n"
        else:
            keyword_str += f"{keyword}:{temp[0]};\n"
    # 可能keyword解释会有问题
    print(f"\033[1;32m | INFO     | Analyzing and processing Keywords' Result:\n{keyword_str}\n \033[0m")

    return keynum, relatedPaper, keyword_str


def extract_message(file, split_section):
    print(f"\033[1;32m | INFO     | extracting message... \033[0m")
    text = read_markdown_file(file)

    if split_section != "":
        match = re.search(fr'### \S*{split_section}\S*(.*?)(?=###|---|\Z)', text, re.DOTALL)
        if match:
            problem_statement = match.group(1).strip()
            print(problem_statement)
    return text, problem_statement


def extract_technical_entities(file, split_section):
    print(f"\033[1;32m | INFO     | extracting technical entities... \033[0m")

    text, problem_statement = extract_message(file, split_section)

    system_prompt = extract_tec_entities_prompt()

    Keywords = call_with_deepseek_jsonout(system_prompt=system_prompt, question=f'The content is: {problem_statement}')[
        'keywords']

    sorted_entities = SearchKeyWordScore(Keywords)

    print(f"\033[1;32m | INFO     | extracting technical entities:OK! \033[0m")

    return sorted_entities, text


def extract_message_review(file, split_section):
    print(f"\033[1;32m | INFO     | Info: extracting message review... \033[0m")
    text = read_markdown_file(file)

    if split_section != "":
        match = re.search(fr'(#.*{split_section}\**\:*)(.*?)(?=#|\Z|---)', text, re.DOTALL)
        if match:
            problem_statement = match.group(2).strip()
        else:
            print(f"\033[1;31m | ERRO     | extracting message review：erro！\033[0m")

    if split_section == "Iterative Optimization Search Keywords":
        question = f"""Based on the content provided below, extract the next optimization search keywords. Return the 
        result only in the following JSON format. Do not add any explanations or irrelevant information. JSON output 
        format: {{ "optimization_keyword": "xxx", ... }}

        Content to extract:
        '''
        #{split_section}\n{problem_statement}
        '''"""
    elif split_section == "Next Steps for Optimization":
        question = f"""Based on the content provided below, extract the next optimization goal. Return the result 
        only in the following JSON format. Do not add any explanations or irrelevant information. JSON output format: 
        {{ "optimization_goal": "xxx", ... }}

        Content to extract:
        '''
        #{split_section}\n{problem_statement}
        '''"""
    else:
        print(split_section)

    result = call_with_deepseek_jsonout(question=question, system_prompt="")
    print(result)

    return text, result


def review_mechanism(topic, draft="", user_id="", task=None):
    # system_prompt = "You are a helpful assistant."
    print(f"\033[1;32m | INFO     | now review is running... \033[0m")

    system_prompt = review_mechanism_prompt()

    user_prompt = f"""# Idea Draft\n{draft}"""

    result = call_with_qwenmax(system_prompt=system_prompt, question=user_prompt)
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task.id}/{topic}/Review"
    # 检查目录是否存在，不存在则创建
    os.makedirs(file_path_prefix, exist_ok=True)
    with open(fr"{file_path_prefix}/{topic}_review.md", 'w', encoding='utf-8') as f:
        f.write(result)

    text, optimize_messages = extract_message_review(file=fr"{file_path_prefix}/{topic}_review.md",
                                                     split_section="Iterative Optimization Search Keywords")

    keywords = []

    for optimize_message in optimize_messages.values():
        # temp=optimize_message.split('\n')
        # print(temp)
        keywords.append({'keyword': optimize_message})

    print(keywords)

    print(f"\033[1;32m | INFO     | now review is running:OK! \033[0m")

    return keywords


def extract_message_review_moa(file, split_section):
    print(f"\033[1;32m | INFO     | Info: extracting message review... \033[0m")
    text = read_markdown_file(file)

    if split_section != "":
        match = re.search(fr'(#.*{split_section}\**\:*)(.*?)(?=#|\Z|---)', text, re.DOTALL)
        if match:
            problem_statement = match.group(2).strip().split('\n')
            print(problem_statement)
        else:
            print(f"\033[1;31m | ERRO     | extracting message review：erro！\033[0m")
    return text, problem_statement

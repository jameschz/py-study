import requests
import wikipedia
import re

from retry import retry
from pathlib import Path
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

class WikiSpider:
    def __init__(self):
        self.data_dir = "./demo-plmap/data"
        self.parse_list = []

    def get_raw_data(self):
        # ua = UserAgent()
        # self.wiki_url = "https://en.wikipedia.org/wiki/Timeline_of_programming_languages"
        # self.headers = {
        #     "User-Agent": ua.random,
        #     "Referer": "https://www.google.com",
        #     "Connection": "keep-alive",
        # }
        # self.content = requests.get(self.wiki_url, headers=self.headers).content.decode()
        self.replace_list = {
            '(concept)' : '',
            '(implementation)' : '',
            'Polymorphic Programming Language (PPL)' : 'PPL',
            'Compiler Description Language (CDL)' : 'CDL',
            'Structured Query language (SQL)' : 'SQL',
            'Perl Data Language (PDL)' : 'PDL',
            'Ada 80 (MIL-STD-1815)' : 'Ada 80',
        }
        self.content = wikipedia.page("Timeline_of_programming_languages").html()

    def parse_data(self):
        html_all = BeautifulSoup(self.content, "html.parser")
        td_list = html_all.find_all('td')
        record_switch = False
        record_count = 0
        this_year = None
        for td_item in td_list:
            td_text = self._format_text(td_item.get_text())
            # 开始记录，计数3次之后，重新判断年份
            if record_switch:
                record_count = record_count + 1
                if record_count == 1:
                    td_lang = td_text
                elif record_count == 2:
                    td_author = td_text
                elif record_count == 3:
                    td_parent = td_text
                else:
                    record_switch = False
                    td_parent_list = td_parent.split(',')
                    for td_parent_item in td_parent_list:
                        self.parse_list.append({
                            'year': this_year,
                            'lang': td_lang,
                            'author': td_author,
                            'parent': td_parent_item.strip()
                        })
            # 判断年份，是否开启记录
            if not record_switch:
                td_match = re.match(r'^\d{4}', td_text)
                if td_match:
                    td_year = int(td_text[:td_match.end()])
                    if td_year >= 1950:
                        this_year = td_year
                        record_switch = True
                        record_count = 0

    def build_data_family(self):
        build_list = []
        build_key_index = 0
        # 获取所有顶层节点
        for parse_item in self.parse_list:
            if not parse_item['parent'] or parse_item['parent'] == 'none':
                build_key_index = build_key_index + 1
                build_list.append({
                    'key': build_key_index,
                    'name': parse_item['lang']
                })
        # 遍历查找所有节点
        for _ in range(1):
            for parse_item in self.parse_list:
                for build_item in build_list:
                    if parse_item['parent'] == build_item['name']:
                        build_key_index = build_key_index + 1
                        build_list.append({
                            'key': build_key_index,
                            'name': parse_item['lang'],
                            'parent': build_item['key']
                        })
        # 构造代码
        data_str = "var nodeDataArray = [\n"
        for build_item in build_list:
            if 'parent' in build_item.keys():
                data_str = data_str + '{ key: ' + str(build_item['key']) + ', name: "'+build_item['name'] + '", parent: ' + str(build_item['parent']) + ' },' + "\n"
            else:
                data_str = data_str + '{ key: ' + str(build_item['key']) + ', name: "'+build_item['name'] + '" },' + "\n"
        data_str = data_str + "];"
        # 保存文件
        self._save_data('family', data_str)

    # 保存图形
    def build_data_graph(self):
        # 构造代码
        node_list = []
        data_str = "var nodeDataArray = [\n"
        for parse_item in self.parse_list:
            if parse_item['lang'] not in node_list:
                data_str = data_str + '{ key: "' + parse_item['lang'] + '", color: "lightgreen" },' + "\n"
                node_list.append(parse_item['lang'])
        data_str = data_str + "];\n"
        # 构造代码
        data_str = data_str + "var linkDataArray = [\n"
        for parse_item in self.parse_list:
            if parse_item['parent'] and parse_item['parent'] != 'none':
                data_str = data_str + '{ from: "' + parse_item['parent'] + '", to: "' + parse_item['lang'] + '", color: "black" },' + "\n"
        data_str = data_str + "];"
        # 保存文件
        self._save_data('graph', data_str)

    # 去除干扰的tag标签
    def _format_text(self, text):
        for k, v in self.replace_list.items():
            text = text.replace(k, v)
        text = re.sub(r'\((.*?)\)', '', text)
        text = re.sub(r'\[(.*?)\]', '', text)
        return text.strip()

    # 保存js文件
    @retry(tries=3)
    def _save_data(self, file, text):
        self.data_path = Path(self.data_dir)
        if not self.data_path.exists():
            self.data_path.mkdir()
        with open(self.data_dir + '/' + file + '.js', 'w', encoding='utf-8') as fp:
            fp.write(text)
        print("save " + file + " successfully.")


if __name__ == '__main__':
    ws = WikiSpider()
    ws.get_raw_data()
    ws.parse_data()
    # print(ws.parse_list)
    ws.build_data_family()
    ws.build_data_graph()

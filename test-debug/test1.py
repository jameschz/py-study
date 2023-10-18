import re

# list = re.findall(r'<td>(.*?)</td>', '<table><tr><td>test1</td><td>test2</td><td>test3</td></tr></table>')
# for item in list:
#     print(item)

# str = re.sub(r'<.*?>', '', '<table><tr><td>test</td></tr></table>')
# print(str)

# txt = "1920d"
# res = re.match(r'^\d{4}', txt)
# print(txt[:res.end()])

txt = "1920d[5]"
txt = re.sub(r'\[(.*?)\]', '', txt)
print(txt)


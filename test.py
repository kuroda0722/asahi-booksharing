# coding:utf-8
import cgitb
import sys
import io
sys.stdin = open(sys.stdin.fileno(),  'r', encoding='UTF-8')
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='UTF-8')
sys.stderr = open(sys.stderr.fileno(), 'w', encoding='UTF-8')
cgitb.enable()
 
print("Content-type: text/html; charset=utf-8")
print("")
bb = ccc
aa = "aaa" + "bbbb"
HtmlData = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <title>Hello World | python</title>
</head>
<body>
<h1>Hello world for Python</h1>
"""
HtmlData+=aa
HtmlData += """
<h2>‚ ‚ ‚ ‚ </h2>
</body>
"""
 
print(HtmlData)
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import networkx as nx
import re
from matplotlib import font_manager

# 使用 GB18030 编码读取数据
file_path = 'Comments.csv'
data = pd.read_csv(file_path, encoding='gb18030')

# 提取评论列并进行空值过滤，并保留原始索引
comments = data['评论'].dropna()

# 加载停用词表
stopwords = set()
with open('cn_stopwords.txt', 'r', encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.strip())

# 加载情感词典
positive_words = set()
with open('positive_submit.txt', 'r', encoding='utf-8') as f:  # 正面词词典
    for line in f:
        positive_words.add(line.strip())

negative_words = set()
with open('negative_submit.txt', 'r', encoding='utf-8') as f:  # 负面词词典
    for line in f:
        negative_words.add(line.strip())

# 清除标点符号、表情符号和停用词
def clean_text(text):
    # 去除标点符号和特殊字符
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    # 剔除纯表情符号或明显与主题无关的内容
    irrelevant_patterns = ['捂脸', '笑哭', '点赞', '哈哈哈', '赞', '表情',
                           '[九转大肠]', '[比心]', '[玫瑰]', '[看]', '[感谢]', '[发怒]',
                           '给你点一百个赞', '强烈建议恢复八抬大轿', '抠鼻', '呲牙']
    for pattern in irrelevant_patterns:
        text = text.replace(pattern, '')

    # 分词
    words = jieba.cut(text)
    # 去除停用词
    words = [word for word in words if word not in stopwords and word.strip() != '']
    return words

# 对评论进行分词和清理
tokens = [clean_text(comment) for comment in comments]

# 情感分析函数
def sentiment_analysis(token_list):
    pos_count = 0
    neg_count = 0
    for word in token_list:
        if word in positive_words:
            pos_count += 1
        elif word in negative_words:
            neg_count += 1
    if pos_count > neg_count:
        return '正面'
    elif neg_count > pos_count:
        return '负面'
    else:
        return '中性'

# 对所有评论进行情感分析
sentiments = [sentiment_analysis(token) for token in tokens]

# 将情感分析结果合并回原始数据框
data.loc[comments.index, '情感倾向'] = sentiments

# 统计各情感类别的数量
sentiment_counts = data['情感倾向'].value_counts()
print(sentiment_counts)

# 设置中文字体
font_path = 'SimHei.ttf'
font_prop = font_manager.FontProperties(fname=font_path)

# 可视化情感分类结果
plt.figure(figsize=(8, 6))
sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'])
plt.title('评论情感倾向分析', fontproperties=font_prop)
plt.xlabel('情感类型', fontproperties=font_prop)
plt.ylabel('评论数量', fontproperties=font_prop)

plt.xticks(ticks=range(len(sentiment_counts)), labels=['中性', '正面', '负面', '无法预测'], fontproperties=font_prop)

plt.savefig('sentiment_analysis.png', format='png', dpi=300)
plt.show()

# 统计所有词的出现次数
flat_tokens = [word for sublist in tokens for word in sublist]
word_freq = Counter(flat_tokens)

# 显示前50个词及其出现次数
top_50_words = word_freq.most_common(50)
print("前50个词出现的次数：")
for word, freq in top_50_words:
    print(f"{word}: {freq}")

# 生成词云图
wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate(
    ' '.join(flat_tokens))

# 显示并保存词云图
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('wordcloud.png', format='png', dpi=300)  # 保存词云图
plt.show()

# 构建词语共现矩阵
co_occurrence = Counter()
for token_list in tokens:
    for i in range(len(token_list)):
        for j in range(i + 1, len(token_list)):
            if token_list[i] != token_list[j]:
                pair = tuple(sorted([token_list[i], token_list[j]]))
                co_occurrence[pair] += 1

# 创建语义网络图
G = nx.Graph()
for (word1, word2), freq in co_occurrence.items():
    if freq > 100:  # 设置阈值，过滤掉共现频率低的词对
        G.add_edge(word1, word2, weight=freq)

# 绘制并保存语义网络图
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=2.0)
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='skyblue')
nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.7)
nx.draw_networkx_labels(G, pos, font_size=8, font_family='SimHei')

plt.title('语义网络图', fontproperties=font_prop)
plt.axis('off')
plt.savefig('semantic_network.png', format='png', dpi=300)  # 保存语义网络图
plt.show()

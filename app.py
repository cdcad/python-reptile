import numpy as np
import requests
import re
import jieba
from bs4 import BeautifulSoup
from collections import Counter
import streamlit as st
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, font_manager
from pyecharts.charts import Bar, Pie, Line, WordCloud, Scatter
import streamlit_echarts
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import statsmodels.api as sm
import matplotlib.font_manager as fm

def main():
    st.title("词语频率分析")

    plt.rcParams["font.sans-serif"] = "SimSun"
    font_manager.fontManager.addfont('fonts/SimSun.ttc')  # 临时注册新的全局字体

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签

    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    url = st.text_input("请输入URL")
    chart_type = st.sidebar.selectbox("选择图表类型", ["柱状图", "饼状图", "折线图", "词云图", "散点图", "数据表格", "直方图", "成对关系图", "回归图"])

    if st.button("分析") or url:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        response.encoding = "utf-8"
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            # 获取正文
            content = soup.get_text()

            # 使用正则表达式去除HTML标签
            content = re.sub(r'<.*?>', '', content)
            # 去除标点符号和多余空格
            content = re.sub(r'[^\w\s]', '', content)
            filtered_content = re.sub(r'\s+', '', content).strip()  # 去除多余空格并去除首尾空格
            stop_words = [
                "的", "了", "和", "是", "在", "我", "他", "她", "你", "我们", "大家", "这个", "那个",
                "一些", "有", "没有", "可以", "不可以", "就是", "也是", "还是", "不是", "这样", "那样",
                "这里", "那里", "如何", "怎么", "因为", "所以", "然后", "但是", "虽然", "但", "因", "所",
                "而", "且", "或者", "并且", "如果", "只是", "只有", "无论", "例如", "如", "即使", "甚至",
                "从", "到", "向", "对于", "关于", "很", "非常", "太", "更", "最", "比较", "只", "就",
                "再", "也", "还", "就是说", "的话", "之类", "这", "那", "他们", "它们", "自己", "一切",
                "不要", "不能", "应该", "需要", "可以", "可能", "如何", "什么", "多"
            ]

            # 将正文内容拆分为词语
            words = jieba.cut(filtered_content)
            words = [word for word in words if word not in stop_words]
            # 统计词语频率
            word_counts = Counter(words)
            # 获取最常见的词语和对应的频率
            top_words = word_counts.most_common(20)  # 获取前20个最常见的词语

            if chart_type == "柱状图":
                # 创建柱状图
                chart = (
                    Bar()
                    .add_xaxis([word[0] for word in top_words])
                    .add_yaxis("频率", [word[1] for word in top_words])
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="词语频率柱状图", pos_bottom=True),
                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45, font_size=8, font_style='italic'))
                    )
                )

            elif chart_type == "饼状图":
                # 创建饼状图
                chart = (
                    Pie()
                    .add("", [list(word) for word in top_words])
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="词语频率饼状图", pos_bottom=True),
                        legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_right="2%")
                    )
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                )

            elif chart_type == "折线图":
                # 创建折线图
                chart = (
                    Line()
                    .add_xaxis([word[0] for word in top_words])
                    .add_yaxis("频率", [word[1] for word in top_words])
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="词语频率折线图", pos_bottom=True),
                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45, font_size=8, font_style='italic'))
                    )
                )

            elif chart_type == "词云图":
                # 创建词云图
                chart = (
                    WordCloud()
                    .add("", [list(word) for word in top_words],word_size_range=[20,60],shape ='circle')
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="词语频率词云图", pos_bottom=True)
                    )
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                )

            elif chart_type == "散点图":
                # 创建散点图
                chart = (
                    Scatter()
                    .add_xaxis([word[0] for word in top_words])
                    .add_yaxis("频率", [word[1] for word in top_words])
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title="词语频率散点图", pos_bottom=True),
                        xaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(rotate=-45, font_size=8, font_style='italic'))
                    )
                )

            elif chart_type =="数据表格":
                # 将词语频率转换为DataFrame
                df = pd.DataFrame(top_words, columns=["词语", "频率"])
                # 将索引从0开始改为从1开始
                df.index = df.index + 1
                # 显示表格
                st.dataframe(df)
                return

            elif chart_type == "直方图":
                frequencies = [word[1] for word in top_words]
                # 使用Seaborn创建直方图
                sns.histplot(frequencies)
                # 获取当前的Matplotlib图形对象
                fig = plt.gcf()
                plt.xlabel("频率")
                plt.ylabel("个数")
                # 在Streamlit中渲染图表
                st.pyplot(fig)
                return

            elif chart_type == "成对关系图":
                df = pd.DataFrame(top_words, columns=["词语", "频率"])
                # 使用 Seaborn 创建成对关系图
                sns.pairplot(df)
                # 在 Streamlit 中显示图表
                fig = plt.gcf()
                st.pyplot(fig)
                return

            elif chart_type == "回归图":
                # 创建回归图
                df = pd.DataFrame(top_words, columns=["词语", "频率"])
                X = np.arange(len(df))
                y = df["频率"].values
                X = sm.add_constant(X)
                plt.figure(figsize=(10, 6))
                sns.regplot(x=X[:, 1], y=y)
                plt.xlabel("词语")
                plt.ylabel("频率")
                plt.title("回归图")
                fig = plt.gcf()
                st.pyplot(fig)
                return


            # 在streamlit中渲染图表
            streamlit_echarts.st_pyecharts(
                chart,
                theme=ThemeType.DARK
            )

        else:
            st.write("无法访问网址：" + url)

if __name__ == '__main__':
    main()
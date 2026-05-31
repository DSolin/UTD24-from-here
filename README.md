
![UTD24 from here](./image/banner.png)


<h3> UTD24 from here · UTD24 可视化平台 <h3>

简体中文 | [English](./README_En.md)

> *“博观而约取，厚积而薄发。”一一苏轼*

 **UTD24作为经管领域的顶级期刊列表，记录了经济和管理领域最伟大、最前沿的学术成果，奠定了整个经管学术大厦的基座。为了让研究人员更好地探索、吸收这24本学术期刊中的最新成果，UTD24-from-here通过一个平台搜集所有期刊，并将原始文献数据转化为交互式仪表板：世界地图、词云、趋势图、作者合作网络，一应俱全，方便学习者通过文献计量的方式获得价值增值**



## 📄 项目简介
* **UTD24介绍**：UTD24，全称The University of Texas at Dallas 24期刊，是美国德克萨斯大学达拉斯分校纳文金达尔管理学院创建的期刊数据库，包含24本顶级商业和管理学期刊，用于对全世界前100名商学院进行科研排名。
* **数据源**：接入 CrossRef、Semantic Scholar、OpenAlex 三大数据源
* **可视化**：自动爬取、去重、存储全部文献元数据，提供多个交互式 BI 图表，支持下钻和日期筛选
* **一键更新**：一键更新数据，保持文献库始终最新


## 页面展示
![主仪表板](./image/screenshot-dashboard.png)
![文献爬虫](./image/crawl.png)
![文献可视化](./image/visualization.png)
![文献列表](./image/screenshot-literature.png)
![文献详情](./image/detail.png)
![搜索页](./image/screenshot-search.png)
![收藏页](./image/Favorites.png)


## 🚀 快速开始

### 步骤 1: 确保你的电脑中有docker并运行
[docker下载](https://www.docker.com/)

### 步骤 2: 在cmd中输入下列命令
```bash
git clone https://github.com/DSolin/UTD24-From-Here.git
cd UTD24-From-Here
cp .env.example .env
docker compose up -d --build
```

### 步骤 3: 打开浏览器
浏览器打开 [http://localhost:8000](http://localhost:8000) 即可使用。


## 功能一览
| 功能 | 说明 |
| ------------ | ----------- |
|世界地图|作者全球分布，支持国家下钻|
|关键词词云|高频关键词可视化|
|趋势图|发文量随时间变化|
|作者网络|合作关系图谱|
|期刊排行|各期刊发文量对比|
|引用分析|高引论文排名|
|文献检索|标题、摘要、作者全文搜索|
|收藏星标|一键收藏关注文献|
|CSV 导出|筛选结果一键导出|
|更新数据|一键爬取最新文献，带实时进度条|


## 数据来源
| 来源 | 顺序 |
| ------------ | ----------- |
|CrossRef|主力|
|Semantic Scholar|第二|
|OpenAlex|第三|


## 技术栈
| 层级 | 技术 |
| ------------ | ----------- |
|后端|	FastAPI + SQLAlchemy + PostgreSQL|
|前端|	Vue 3 + TypeScript + Tailwind CSS|
|图表|	Apache ECharts|
|基础设施|	Docker Compose|


## API 文档
http://localhost:8000/docs


## 常用命令
```bash
docker compose ps                           # 查看状态
docker compose logs app --tail 50           # 查看日志
docker compose restart app                  # 重启
docker compose exec app python crawl_all.py # 爬取数据
docker compose down                         # 停止
```

## 声明
* 本项目只是搜集期刊标题、作者等公开信息，不涉及文章版权内容。
* 项目仅用于个人学习，不建议大规模使用。
* 项目在文献爬取和作者国籍识别方面还有待优化，准确率有一定偏差，不建议将统计结果用于严谨的研究中

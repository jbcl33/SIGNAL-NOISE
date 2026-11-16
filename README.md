# SIGNAL / NOISE

中文移动端数字杂志。瑞士网格、构成主义几何封面、红黑白配色。首版整理自用户提供的 `index-7.html`，包含第 001 期模拟试刊的晨刊、午刊、晚刊与可检索的历史归档。

**尚未实现每日 AI 自动写稿、自动采集或内容事实核查。** GitHub Actions 仅构建和部署已有内容，不按日生成文章。附件中的发行描述未重新核实，历史项目不作为当日新闻；外部图片和视频可能因原站策略不可用，保留来源链接与图片错误提示。

## 本地运行

需要 Python 3，无第三方构建依赖：

```sh
python scripts/build.py
python -m http.server 8000 --directory _site
```

打开 http://localhost:8000 。生产使用 `_site`；根目录 `index.html`、`archive.html` 为生成的可审阅副本，请改模板后重新生成。

## 期刊数据

- `data/issues.json`：目录，`schemaVersion` 与 `issues`（id、date、title、status、description），按日期倒序展示。
- `data/issues/001.json`：完整期刊；`editions` 按 morning / noon / night 排列，每刊含 id、label、time、contentHtml。
- `contentHtml` 是可信编辑者维护的富文本，不接受访客提交；禁止放入脚本或不可信 HTML。
- `scripts/issue.template.html`：封面与版式模板。首版封面/期号文案对应 001，新增期刊时需同步调整模板，或先将这些字段模板化。
- 历史页地址 `issues/001.html` 保持稳定。当前只有一期，未伪造历史记录。

## 部署

仓库 Settings → Pages → Source 选择 **GitHub Actions**。推送 main 或手动运行 `Deploy magazine to GitHub Pages`，工作流校验期刊结构、构建 `_site`、上传并部署 Pages。无密钥、无付费 API、无定时写稿任务。项目路径使用相对链接，兼容 GitHub Pages 仓库子路径。

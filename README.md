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

## 独立晨刊

`static/morning/001/index.html` 为 2026-11-17 独立晨刊，来自用户提供的 `SIGNAL_NOISE_MORNING_001_REDOWNLOAD.zip`，随构建复制到 `/morning/001/`。保留原稿、原创封面及原始来源链接；仅增加首页返回入口和目录键盘交互。首页新增独立晨刊入口，原三刊内容保留。外部 Bandcamp 播放器依赖原站网络，本文不代表已重新核实全部报道或实现自动写稿。

晨刊视觉修订：七张真实专辑封面、四条技术简报配图与三张深读/制作图，均为对应来源的本地展示副本；详细出处在 `static/morning/001/assets/credits.json`。新版刊封面为 AI 辅助生成的原创几何视觉，保留像素字体、侧边目录与 Bandcamp 展开试听。

## 制作与手机通知

见 [OPERATIONS.md](OPERATIONS.md)。`data/publications.json` 登记独立分刊，构建后首页生成阅读入口，并输出线上 `publications.json` 供通知任务核实本期是否可读。制作和提醒是独立任务，首次定时生产尚需实际运行验证。

2026-11-17 最新修订：独立晨刊使用完整杂志刊封面；音乐改为六张乐评电子精选，用户分/媒体分、原始分制、样本数、核查日期与来源在 `static/morning/001/music-selection.json` 记录。RYM 实时评分无法读取，本期未虚构 RYM 评分，展示核实的 AOTY 分数并保留确认的 RYM 专辑入口。其余栏目保留。

## 乐评采集与发现

`python scripts/collect_music_sources.py` 采集七个音乐媒体/独立博客的公开 RSS 元数据（每站最多5条，限制响应体、超时、并发，失败保留历史记录并标注）。采集结果仅供内部选题，页面不提供评分系统或独立雷达入口。原文评分与证据独立存储，不从标题或 RSS 自动推测评分；目前已有 Pitchfork 8.2/10 和 Fantano 8/10 的原始来源核实示例。

最新视觉以纯白、黑字、荧光绿及原创波形 SVG 为准。音乐恢复10张 Bandcamp 发现（7张原小众推荐 + 3张媒体发现），附发行页中文简述；当前记录为 `static/morning/001/bandcamp-selection.json`。旧评分资料保留为历史来源，不作为页面评分面板。

首页已独立为汇编动画门户，代码位于 `scripts/home.template.html`、`scripts/render_home.py` 与 `assets/home.*`；包含分刊入口、固定技术选读、归档，以及可暂停和单步的RISC-V风格视觉演示。原整期继续保存在 `issues/001.html`。晨刊音乐现压缩为三张紧凑卡片，位于技术内容之后。

最新首页为黑底白色汇编字符组成的旋转像素立方体，保留暂停与减少动态效果；不再采用白色仪表盘门户。内页保持白底。音乐配额在 `data/editorial-policy.json`：晨3、午3、晚1、实验室0；分刊登记musicCount并提供bandcamp-selection.json，构建核对数量。视觉参考见OPERATIONS.md，Canvas动画为原创实现。

首页动画现按屏幕刷新节奏推进，字符预渲染为图集；分刊、归档和暂停控制移入左上角展开菜单。默认画面只留动画与刊名，支持键盘、减少动态效果和后台暂停。

当前首页为汇编字符星云。分刊返回首页链接已按GitHub Pages项目路径修正；构建校验本地链接不越出/SIGNAL-NOISE/且目标存在，`python -m unittest discover -s tests` 覆盖返回路径回归。

首页当前为全屏黑白绿PCB视觉：中央MCU、扇出走线与绿色沿线流动脉冲。中央芯片可进入最新分刊，保留菜单与暂停。为原创视觉示意而非可制造电路。

首页器件交互：晶振打开归档，三个LDO分别为晨/午/晚刊，显示模块和MCU进入最新分刊，拨动开关暂停或播放。未发布分刊保留禁用待刊态，发布清单更新后自动启用。原悬浮菜单已移除，手机端支持触控与减少动态效果。

首页最新视觉约束（覆盖此前样式）：黑色背景，走线、铜区、丝印与器件仅白色/灰阶，绿色仅用于流动脉冲。主视觉借鉴用户给出的电路艺术线束节奏与留白，不复制人物、羽毛素材。采用低对比度斜线网格铺铜、局部实铜、过孔孔环、安装孔与LDO散热孔阵；去掉铜区避让框轮廓及渐变金属装饰。ALL/L1 SIGNAL/L2 GND/L3 POWER/L4 B.Cu五个按钮切换示意图层，背层采用虚线。保留晶振归档、三个LDO分刊、显示器/MCU最新刊与SW1动画控制。图层、铜区、走线与绿色脉冲均为交互视觉示意，未经过原理图、电气规则、制造规则或电流仿真验证，不宣称可制造的四层PCB。不要恢复已删除的口号文案。

首页功能优先更新：所有白色器件框与板框采用直角；保留走线45度转折和圆形孔。最新刊展示真实标题、日期、内容摘要和中文阅读入口；三个LDO明确显示刊别、已发布的期号/日期或尚未发布状态。板层功能收进默认折叠的“板层视图”，不要让实验控件压过阅读入口。手机标题不与电源接口丝印重叠；短横屏允许纵向滚动，保证模块间距。

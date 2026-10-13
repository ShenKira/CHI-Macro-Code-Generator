# CHI660E 试验目录与宏映射

来源为本项目的 `chi660e.chm`。各定义的 `source` 指向该 CHM 参数页面。
参数范围优先使用 `Setup / Parameters` 对应页面；宏表说明大部分范围属于较旧的 600A，不能直接代替 600E 参数页。

## 31 类试验

CV、LSV、SCV、TAFEL、CA、CC、DPV、NPV、DNPV、SWV、ACV、SHACV、FTACV、IT、DPA、DDPA、TPA、IPAD、BE、HMV、SSF、STEP、EIS、IMPT、IMPE、CP、CPCR、ISTEP、PSA、ECN、OCPT。

IMP 在应用中沿用原来的 EIS 名称；Multi-Current Steps 的参数页为 `cpcs9c`，宏技术名是 `istep`。
LSV、SCV、DPV、NPV、DNPV、SWV、ACV、SHACV 还包含宏表明确列出的极谱／溶出变体。

## 文档未给出的命令

FTACV、DPA、DDPA、TPA、IPAD 的参数页存在，但 CHM 的 Macro Command 页面没有给出这些方法的技术名与专用参数命令。应用允许配置、编辑、保存和读取这些试验，但缺失映射时不会生成可运行宏。

显示量程数量、部分开路清洗选项、EIS 平均因子与频段周期数等也没有可靠映射。它们在表单中以可选参数呈现：

- 不勾选“设置”：不输出该参数，沿用 CHI 软件已有设置；参数预览中可以检查实际输出。
- 勾选“设置”：必须存在已确认映射，否则导出给出错误；不会悄悄忽略设置。
- 界面中的直流偏置 `off / range / on` 与旧宏表 `ibias = 0–4` 未说明一一对应，不能凭枚举顺序推断。
- EIS 的旧宏 `cl1–cl5` 所标注的频段与新版参数页面不完全对应，因此相关页面参数保留为需要确认映射的选项。

PSA 和 OCPT 的宏列表虽未重复列出 `si`，其参数页面均明确描述采样间隔，`si` 的命令含义在其他时间曲线的宏表中有明确说明。因此这两种方法输出 `si`；仍应在实际 CHI 软件中使用 Test 检查版本兼容性。

## 添加已确认的映射

打开“试验设置 → 宏命令映射”，或编辑 `config/experiments.json` 中的 `macro_overrides`。
结构如下（尖括号内容是格式占位符，不是 CHI 命令；不要直接运行）：

```json
{
  "FTACV": {
    "tech": "<经确认的技术名称>",
    "parameters": {
      "total_points": "<经确认的总点数命令>",
      "points_per_sine": "<经确认的每周期点数命令>"
    }
  }
}
```

普通数值参数使用字符串命令名，生成 `命令=参数值`；开关或枚举可使用独立命令表，例如 `{"true": "<开启命令>", "false": "<关闭命令>"}`。映射必须覆盖该字段的每个选项。
所有未映射且已启用的字段都必须补充；具体字段键见 `core/techniques/` 或保存的试验 JSON。
参数命令只能是单个字母数字命令名，不接受换行、整段脚本或 `run / save / folder` 等控制命令。

## CP 细节

- `priority=potential` 输出 `prioe`，`priority=time` 输出 `priot`。
- `cl` 是半周期段数。时间优先按首段极性分配阴、阳极段数，不再每段都加一次完整充放电周期。
- 时间优先时触及电位边界仍会切换；显示的时间包含保持时间的上限估算，实际可能缩短。
- 电位优先耗时取决于样品，返回未知。零电流＋电位优先可能一直达不到边界，应按测量目标改用时间优先或 OCPT。
- 旧 CP JSON 缺少 `priority` 时保留原行为：电位优先。
- 电流使用宏表的幅值形式，支持零。600E 无外接放大器时限制为 0–0.25 A；ISTEP 为 ±0.25 A。其它型号／电流放大器的 ±2 A 扩展不在当前配置中自动启用。
- 大于 400 段时仪器只保存前 400 段；表单说明保留该限制。

## 模块化与 Nuitka

`schema.py` 声明参数；四个分类模块声明试验；`registry.py` 显式导入目录；`ConfiguredExperiment` 负责验证、序列化、宏生成及耗时；`ExperimentDialog` 自动生成参数表单。
添加有明确宏文档的新方法只需增加定义并加入分类模块的 `TECHNIQUES`，不需修改主窗口、JSON 分发或添加函数。
没有按文件名扫描插件、动态 `importlib` 加载或运行时 CHM 解析。

源代码运行时，设置位于项目的 `config/experiments.json`；Nuitka standalone／onefile 时，位于实际启动 exe 旁的 `config/experiments.json`，不依赖工作目录，也不写入 onefile 解包目录。
`build.bat` 为两个构建显式包含 `core`、`gui`、`utils`；onefile 使用 `--include-onefile-external-data=config/*` 把可编辑配置保留在 exe 外。
分发时须把生成的 `config` 目录一起交付。若没有配置文件，应用使用内置默认值；保存设置时再创建外部文件。
路径与外部数据选项参考 [Nuitka 官方常见问题](https://nuitka.net/user-documentation/common-issue-solutions.html) 和 [外部 onefile 数据说明](https://nuitka.net/posts/nuitka-release-20.html)。

旧四类项目 JSON 可读取，IT 的 `cycles` 自动转换为重复测试次数。数据文件统一按类别编号，如 `项目_CP_1`、`项目_CP_2`，避免多个 CP 或不同参数产生相同名称。新项目包含 `schema_version=2`，旧版应用不具备读取新增类型的能力。

运行验证：`python -m unittest discover -s tests -v`。测试包括全部 31 类的 JSON 往返、文档命令清单比对、CP 零电流和时间计算、可选参数导出保护、快捷设置、参数记忆与 GUI 流程。测试中的自定义宏名称仅为虚构测试数据，不能用于仪器。

# CHI Macro Generator

用于 CHI660E 电化学工作站的 PySide6 图形化宏代码生成工具。试验定义、参数窗口、宏生成与 JSON 保存共用同一套元数据，支持按任意顺序组合试验。

## 功能

- 31 类试验的参数配置、编辑、JSON 保存与读取，参数说明依据 CHI660E 帮助文档整理。
- 默认快捷添加 CV、EIS、CP、I-T、PSA；“添加其他试验”可按中文名称或缩写搜索全部方法。
- “试验设置”可勾选、调整快捷按钮顺序，保存后立即生效，也可直接编辑配置文件。
- 通用参数表单支持科学计数法、中文名称、范围和相关参数校验、宏命令预览。
- CP 支持电位／时间优先、零电流、首段极性、保持时间、辅助信号和零电流观察预设。
- 支持拖拽排序、双击／右键编辑、删除和 Ctrl+Z 撤销。
- 参数记忆保存到配置文件，重启后恢复；旧四类项目 JSON 继续可读。
- 各类试验统一编号保存文件，重复 CP 不再使用相同文件名。
- 耗时依赖样品响应的方法显示“无法确定总耗时”，避免把未确定的耗时算作 0。

## 试验目录及文档限制

CV、LSV、SCV、TAFEL、CA、CC、DPV、NPV、DNPV、SWV、ACV、SHACV、FTACV、IT、DPA、DDPA、TPA、IPAD、BE、HMV、SSF、STEP、EIS、IMPT、IMPE、CP、CPCR、ISTEP、PSA、ECN、OCPT。

**文档给出了 31 类参数页，但没有给出 FTACV、DPA、DDPA、TPA、IPAD 的专用宏命令。**这五类可配置和保存；导出前需在“试验设置 → 宏命令映射”补充经 CHI 软件确认的命令。缺少映射时会明确报错，不会猜测命令或忽略参数。

部分显示、开路清洗、阻抗平均参数也存在同样限制。“设置”未勾选表示沿用仪器已有设置；勾选后若缺少映射则禁止导出。详见 [试验与命令映射说明](docs/TECHNIQUE_MAPPING.md)。

## 使用

1. 用项目所需的 Python 和 PySide6 环境运行 `python main.py`。
2. 设置项目名和 CHI 软件保存数据的目录。
3. 用快捷按钮或“添加其他试验”配置试验；在参数窗口的“宏命令预览”核对设置。
4. 按需排序、编辑、删除或保存项目 JSON。
5. 点击“生成代码”预览并保存 TXT，在 CHI 软件的宏编辑器中 Test 后运行。

当前开发验证环境：Python 3.13.9、PySide6 6.9.2。

## 快捷配置

配置文件为 `config/experiments.json`：

```json
{
  "version": 1,
  "quick_experiments": ["CV", "EIS", "CP", "IT", "PSA"],
  "macro_overrides": {},
  "last_parameters": {}
}
```

`quick_experiments` 的顺序即按钮顺序；可使用目录中任意类型，也允许空列表，此时仍保留“添加其他试验”。`last_parameters` 由参数窗口自动维护。读取错误时使用默认配置并保留原文件，不自动覆盖损坏的设置。

## 模块结构

- `core/techniques/schema.py`：字段、范围、中文标签和验证规则。
- `core/techniques/voltammetry.py`、`amperometry.py`、`impedance.py`、`potentiometry.py`：按方法类别组织定义。
- `core/techniques/registry.py`：静态注册与兼容旧类型的工厂。
- `core/configured_experiment.py`：公共宏生成、序列化、摘要和耗时计算。
- `gui/experiment_dialog.py`：自动生成所有试验的参数窗口。
- `gui/settings_dialog.py`：快捷列表及宏映射配置。
- `utils/app_config.py`：路径解析、配置校验、原子保存和参数记忆。

新增方法时增加试验定义并加入相应分类的 `TECHNIQUES` 即可；主窗口和 JSON 分发无需增加一组分支。

## Nuitka 打包

在已安装 Nuitka 和 PySide6 的 Python 环境中，从项目目录运行 `build.bat 1.7.0 both`。可将 `both` 换成 `standalone` 或 `onefile`；不传版本号时脚本会询问。脚本先使用当前 Python；若缺少依赖，会自动查找用户目录或 Anaconda 目录中的 `nuitka_pack` 环境。也可设置 `NUITKA_PYTHON` 为指定 `python.exe` 的完整路径。脚本先运行项目测试，再由 Nuitka 自动定位最新 MSVC；缺少依赖时会报错并停止。

产物保存在 `release/v1.7.0/standalone/main.dist/` 与 `release/v1.7.0/onefile/`，Nuitka 编译缓存位于 `release/.nuitka-cache/`。同版本的对应构建已存在时脚本会停止，避免覆盖旧产物及用户改过的配置；也可以先构建 standalone，再用相同版本号构建 onefile。版本号请按实际发布号填写。

- standalone：配置保存在 exe 旁的 `config/experiments.json`。
- onefile：配置作为外部数据交付，保存在原始 exe 旁，不写入临时解包目录。
- 分发时把产物目录内的 `config` 目录一起复制；没有配置文件时使用内置默认值。

导入使用明确的 Python 模块引用，不按文件名扫描插件，不在运行时解析 CHM。

## 验证

```text
python -m unittest discover -s tests -v
```

测试覆盖全部类型的序列化、文档命令清单、CP 模式与半周期时间、旧项目、重复文件名、配置保护和 GUI 交互。实际仪器行为仍须在对应版本的 CHI 软件与工作站上验证。

## License

Internal research tool.
Free to modify and adapt for academic and laboratory use.

## Author

Powered by **ShenKira**

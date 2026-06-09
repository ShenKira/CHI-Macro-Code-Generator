# CHI Macro Generator

一个用于 **CHI660E 电化学工作站** 的图形化 **Macro Command 代码生成工具**。  
通过模块化方式配置 **CV / EIS / CP** 实验，自动生成规范、可重复的测试脚本。

A graphical macro code generator for **CHI660E electrochemical workstations**,  
designed to build **CV / EIS / CP** experiments in a modular and reproducible way.

---

## ✨ Features | 功能特点

- 图形界面配置 **CV / EIS / CP** 测试参数
- 模块化添加实验，支持任意顺序组合
- 自动生成 CHI 宏命令（Macro Command）脚本
- 自动估算总测试耗时
- 所有参数在软件重启后自动记忆上一次使用值
- 明确的参数校验，避免生成非法代码
- 适用于 Windows（CHI 官方软件环境）

---

## 🧪 Supported Experiments | 支持的实验类型

本软件支持 CHI660E 常用的三类基础电化学测试，所有测试均以模块形式组合，并最终生成 Macro Command 脚本。

### CV – Cyclic Voltammetry
- 起始电位 / 高低电位
- 扫描速率
- 扫描圈数
- 静息时间等

### EIS – Electrochemical Impedance Spectroscopy
- 最高频率 `fh`
- 最低频率 `fl`
- 交流扰动幅度 `amp`
- 静息时间 `qt`
- 重复测试次数

### CP – Chronopotentiometry（恒流充放电）
- 阴极电流 `ic`（支持科学计数法输入，如 `1e-4`）
- 阳极电流 `ia`（支持科学计数法输入）
- 高 / 低电位限制 `eh` / `el`
- 高 / 低电位保持时间 `heht` / `leht`
- 起始电流极性 `pn`（`p` / `n`）
- 数据存储间隔 `si`
- 段数 `cl`（segments）

> 注：
> - CP 模式下程序固定采用 **电势优先（prioe）** 模式。
> - CP 的测试耗时为估算值，仅用于流程规划参考。

---

## 🚀 Usage | 使用流程

### 中文说明

1. 启动软件
2. **在生成代码之前，务必先完整设置所有参数**
3. 点击 **“添加 CV”**、**“添加 EIS”** 或 **“添加 CP”**，将实验加入测试序列
4. 根据需要重复添加多个实验模块
5. 在下方查看 **预计总测试耗时**
6. 点击 **生成代码**，导出 CHI Macro Command 脚本
7. 将生成的脚本导入 CHI 官方软件并运行

⚠️ **重要提示**：
- 生成代码时，程序将直接使用当前界面中的参数值
- 若参数未设置或设置错误，将直接影响生成的 Macro Command

---

### English Instructions

1. Launch the software
2. **Make sure all parameters are fully configured before generating code**
3. Click **Add CV**, **Add EIS**, or **Add CP** to append an experiment module
4. Add multiple modules in any desired order
5. Check the **estimated total experiment time**
6. Click **Generate Code** to export the CHI Macro Command script
7. Import the script into the official CHI software and run it

⚠️ **Important**:
- Code generation uses the current GUI parameter values directly
- Incorrect or incomplete parameters will result in invalid macro scripts

---

## 📦 Release | 发布说明

- Windows 可执行文件通过 **Nuitka** 编译生成
- 可在 GitHub **Releases** 页面下载对应版本的 `.exe`
- Release 中通常包含：
  - 编译后的可执行文件
  - 对应版本说明（Changelog）

---

## 📄 License | 许可

Internal research tool.  
Free to modify and adapt for academic and laboratory use.

---

## 👤 Author

Powered by **ShenKira**


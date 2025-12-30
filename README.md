# CHI Macro Generator

一个用于 **CHI660E 电化学工作站** 的图形化 **Macro Command 代码生成工具**。  
通过模块化方式配置 CV / EIS 实验，自动生成规范、可重复的测试脚本。

A graphical macro code generator for **CHI660E electrochemical workstations**,  
designed to build CV / EIS experiments in a modular and reproducible way.

---

## ✨ Features | 功能特点

- 图形界面配置 CV / EIS 测试参数
- 模块化添加实验，支持任意顺序组合
- 自动生成 CHI 宏命令（Macro Command）脚本
- 自动估算总测试耗时
- 自动管理文件命名，避免参数冲突
- 支持右键删除实验模块

---

## 🧪 Supported Experiments | 支持的实验类型

### CV – Cyclic Voltammetry
- 起始 / 结束电位
- 高电位上限
- 扫速（V/s）
- 轮次（cycles）
- 电容值输入（µF，自动计算推荐灵敏度）
- 手动灵敏度选择（覆盖自动结果）

### EIS – Electrochemical Impedance Spectroscopy
- 最高频率 `fh`
- 最低频率 `fl`
- 交流扰动幅度 `amp`
- 静息时间 `qt`
- 重复测试次数

---

## 🚀 Usage Workflow | 使用流程（非常重要）

### **请严格按照以下顺序操作**

### 1️⃣ 设置项目信息（必须）
- 输入 **项目名称**
- 选择 **输出路径（文件夹）**

> ⚠️ 项目名将用于 **所有生成文件的命名**，请在添加实验前确认无误。

---

### 2️⃣ 添加实验模块
- 点击 **“添加 CV”** 或 **“添加 EIS”**
- 在弹出窗口中 **完整填写所有参数**
- 确认后实验将显示在右侧表格中

📌 所有参数在软件运行期间会自动记忆，方便连续添加类似实验。

---

### 3️⃣ 检查实验列表
- 右侧表格显示：
  - 实验顺序
  - 实验类型
  - 关键参数摘要
- 支持 **右键删除实验**
- 下方显示 **预计总测试耗时**

---

### 4️⃣ 生成 Macro Code（最后一步）
- **确认所有实验模块均已添加完成**
- 点击 **“生成代码”**
- 在弹出的窗口中：
  - 复制生成的宏代码  
  - 或保存为 `.txt` 文件

> ❗ **生成代码后不会自动更新**
>  
> 如果修改了任何参数，请重新生成代码。

---

## ⚠️ Important Notes | 注意事项

- 本软件 **不会自动检查实验逻辑冲突**
- 请确保：
  - 电压范围符合样品与设备限制
  - 灵敏度与预期电流范围匹配
- 所有实验参数 **在生成代码前必须全部设置完成**

---

## 🛠 Environment | 运行环境

- Python ≥ 3.9
- PySide6
- 适用于 Windows（CHI 官方软件环境）

---

## 📄 License | 许可

Internal research tool.  
Free to modify and adapt for academic and laboratory use.

---

## 👤 Author

Powered by **shenz**

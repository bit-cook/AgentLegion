# AgentLegion

[English Documentation](README_EN.md)

**自我克隆的 AI 智能体，通过竞争寻求最优解。一生万物 (One becomes many)。**

## 📖 项目简介
AgentLegion 是一个自治 AI 智能体框架，具备递归自我复制（克隆）的能力，旨在探索巨大的解空间。智能体之间为了资源和生存进行竞争，从而推动最优策略的进化。

## 💡 核心概念
- **自我克隆 (Self-Cloning)**: 智能体可以生成子智能体来委派子任务或探索替代路径。
- **优胜劣汰 (Competition)**: 基于表现对智能体进行评估。低绩效的智能体将被淘汰。
- **进化演变 (Evolution)**: 成功的特征和策略将传播给新一代智能体。

## 🛠️ 安装指南

1. **克隆仓库**
   ```bash
   git clone <repository_url>
   cd AgentLegion_Workspace
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
   > 注意：如果因网络问题导致 `openai` 安装失败，系统将自动回退到内置的 `MockLLM` 提供程序。

3. **配置环境**
   - 创建 `.env` 文件并配置您的 API 密钥（如果使用真实 LLM）。
   - 修改 `config.py` 可调整种群大小、变异率等参数。

## 🚀 快速开始

### 运行基础演示
启动主程序，观察智能体种群的进化过程：
```bash
python main.py
```

### 运行实验
运行多次试验并记录性能指标，生成实验报告数据：
```bash
python experiment.py
```

### 运行测试
执行单元测试确保核心功能正常：
```bash
python -m unittest discover tests
```

## 📂 项目结构
- `agent_legion/`: 核心代码库
  - `agent.py`: 智能体定义
  - `environment.py`: 环境与进化逻辑
  - `llm.py`: LLM 接口与 Mock 实现
- `tests/`: 单元测试
- `config.py`: 配置文件
- `main.py`: 主程序入口
- `experiment.py`: 实验脚本

## 📄 许可证
MIT License

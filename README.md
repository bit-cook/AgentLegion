# AgentLegion

**自我克隆的 AI 智能体，通过竞争寻求最优解。一生万物 (One becomes many)。**

[![CI](https://github.com/bit-cook/AgentLegion/actions/workflows/ci.yml/badge.svg)](https://github.com/bit-cook/AgentLegion/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](pyproject.toml)
[![官网](https://img.shields.io/badge/website-live-8b5cf6.svg)](https://bit-cook.github.io/AgentLegion/)

[English Documentation](README_EN.md) · [官方网站](https://bit-cook.github.io/AgentLegion/) · [实验报告](REPORT.md)

## 📖 项目简介

AgentLegion 是一个自治 AI 智能体框架：智能体种群在**真实的基准优化问题**上提出解、相互竞争、优胜劣汰，并通过**自我克隆与基因杂交**把成功策略传播给下一代。它用可复现的实验取代了"随机数假装是智能"——每一次进化都有记录、有种子、有数据。

框架的核心主张很简单：**让智能体进化"如何搜索"，而不是手动编写搜索算法**。

## ✨ 核心特性

- **🧬 真实进化引擎** — 精英保留 + 锦标赛选择 + 克隆/杂交 + 逐基因高斯变异，种群在真实目标函数上可度量地变优（见 [REPORT.md](REPORT.md)）。
- **🔒 完全可复现** — 一切随机性来自可注入的种子 RNG；同一 seed 必然重现同一结果，实验可审计。
- **🤖 双 LLM 后端** — 默认零依赖确定性 Mock（离线可跑）；设置 `OPENAI_API_KEY` 即切换为真实的 OpenAI 兼容 API（同样零第三方依赖，纯标准库实现）。**绝不静默造假**：缺少密钥时会明确告警并回退，`--backend openai` 缺密钥则直接报错。
- **📐 类型化基因** — `focus / iteration / risk_taking` 三个基因有明确边界与语义，变异、杂交、多样性度量全部有测试覆盖。
- **📊 真实指标** — 每代记录 best/mean/median/stdev、种群多样性（策略空间平均距离）、总评估次数、收敛代际。
- **🧪 121 个测试** — 不变量、确定性、CLI 冒烟、报告数字与运行数据一致性，全部通过。
- **📦 零运行时依赖** — `pip install .` 即用，Python ≥ 3.10。

## 🚀 快速开始

```bash
git clone https://github.com/bit-cook/AgentLegion.git
cd AgentLegion
pip install .

# 运行进化演示（约 0.1 秒）
agentlegion run --seed 42

# 或使用历史入口
python main.py --seed 42
```

三十行代码看核心：

```python
from agent_legion import Environment, load_config

config = load_config(SEED=42, GENERATIONS=20, PROBLEM="rastrigin")
env = Environment(config)
result = env.run_simulation()

print(result.summary()["final_best"])   # 从约 -10.47 进化到约 -0.0001
```

运行多次试验并生成实验报告（REPORT.md 由真实运行数据生成，非手写）：

```bash
agentlegion experiment --trials 5 --generations 20 --seed 42
```

运行测试：

```bash
python -m unittest discover tests -v
```

## 🧠 工作原理

每一代分四个阶段：

```
   ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌────────────┐
   │  行动 Act │ → │ 评估 Rank │ → │ 选择 Select│ → │ 繁殖 Reproduce│
   └──────────┘   └───────────┘   └──────────┘   └────────────┘
   每个智能体        按 incumbent     精英保留 +      克隆 / 杂交
   提出 N 个候选解    得分排序          锦标赛选父代     + 基因变异
```

智能体的"基因"决定了它**如何搜索**——这正是被进化的对象：

| 基因 | 范围 | 语义 |
|---|---|---|
| `iteration` | 1 – 20 | 每次行动采样多少个候选解（best-of-N，直接提升期望得分） |
| `focus` | 0.0 – 1.0 | 采样围绕当前最优解的集中程度（1.0 = 局部精炼） |
| `risk_taking` | 0.0 – 1.0 | 探索步长倍数（高 = 大胆跳跃，利于逃离局部最优） |

**基准问题**（全部为最大化问题，最优值 0.0）：

| 问题 | 地形 | 考验 |
|---|---|---|
| `sphere` | 单峰碗 | 纯利用能力 |
| `rastrigin` | 密集多峰 | 探索/利用平衡 |
| `rosenbrock` | 弯曲香蕉谷 | 精细收敛 |

## 🤖 使用真实 LLM

AgentLegion 的默认后端是确定性的 Mock（保证离线可复现）。要接入真实的 OpenAI 兼容模型：

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1   # 任何兼容端点均可
export OPENAI_MODEL=gpt-4o-mini
agentlegion run --backend openai
```

后端选择规则（`LLM_BACKEND` / `--backend`）：

- `auto`（默认）：检测到密钥 → 真实 API；否则 Mock 并打印明确告警。
- `mock`：始终使用确定性 Mock。
- `openai`：强制真实 API；**缺少密钥直接报错退出**（绝不静默降级）。

## ⚙️ 配置

所有配置项都真实生效，可通过环境变量 `AGENTLEGION_*` 或 CLI 参数覆盖：

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `AGENTLEGION_INITIAL_AGENTS` | 5 | 初始种群 |
| `AGENTLEGION_MAX_AGENTS` | 50 | 种群上限 |
| `AGENTLEGION_GENERATIONS` | 20 | 进化代际 |
| `AGENTLEGION_MUTATION_RATE` | 0.25 | 逐基因变异概率 |
| `AGENTLEGION_ELITE_RATE` | 0.1 | 精英保留比例 |
| `AGENTLEGION_CROSSOVER_RATE` | 0.5 | 杂交概率 |
| `AGENTLEGION_TOURNAMENT_SIZE` | 3 | 锦标赛规模 |
| `AGENTLEGION_PROBLEM` | rastrigin | 基准问题 |
| `AGENTLEGION_PROBLEM_DIMENSION` | 2 | 问题维度 |
| `AGENTLEGION_SEED` | 随机 | 随机种子 |
| `AGENTLEGION_LLM_BACKEND` | auto | `auto` / `mock` / `openai` |

## 📂 项目结构

```
AgentLegion/
├── agent_legion/           # 核心包（零依赖）
│   ├── agent.py            #   智能体：行动 / 克隆 / 杂交
│   ├── strategy.py         #   类型化基因：边界、变异、杂交、距离
│   ├── environment.py      #   进化循环：选择与繁殖
│   ├── problems.py         #   基准目标函数（sphere / rastrigin / rosenbrock）
│   ├── llm.py              #   LLM 后端：Mock（确定性）+ OpenAI 兼容（urllib）
│   ├── metrics.py          #   每代统计与收敛检测
│   ├── report.py           #   由真实数据渲染报告
│   ├── config.py           #   配置加载与校验
│   └── cli.py              #   agentlegion 命令行
├── tests/                  # 121 个单元测试
├── scripts/generate_benchmarks.py  # 重新生成官网基准数据
├── docs/                   # 官方网站（GitHub Pages）
├── main.py / experiment.py # 历史入口（向后兼容）
├── pyproject.toml          # 打包与入口点
└── REPORT.md               # 由真实运行生成的实验报告
```

## 🌐 官方网站

**https://bit-cook.github.io/AgentLegion/** — 包含实时进化演示（浏览器内运行完整算法）、真实基准曲线与架构图解。

## 📄 许可证

[MIT License](LICENSE)

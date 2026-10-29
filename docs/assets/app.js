/* ============================================================
   AgentLegion website — engine port, live demo, charts, i18n
   The GA below mirrors agent_legion/ (Python) line for line.
   ============================================================ */
"use strict";

/* ---------------- i18n ---------------- */
const I18N = {
  zh: {
    "nav.demo": "实时演示",
    "nav.how": "工作原理",
    "nav.bench": "基准数据",
    "nav.quick": "快速开始",
    "nav.arch": "架构",
    "hero.kicker": "自治智能体框架 · 开源",
    "hero.title": "一生万物",
    "hero.sub":
      "自我克隆的 AI 智能体在<strong>真实目标函数</strong>上竞争、进化、寻求最优解。每一次运行都有种子、有记录、有数据 —— 可复现，可审计。",
    "hero.cta.demo": "▶ 运行实时演示",
    "hero.cta.github": "GitHub 仓库",
    "hero.stat1": "运行时依赖",
    "hero.stat2": "单元测试",
    "hero.stat3": "基准问题",
    "hero.stat4": "跑完 20 代耗时",
    "demo.kicker": "LIVE DEMO",
    "demo.title": "在浏览器里观看进化",
    "demo.sub":
      "下面运行的正是仓库中的完整算法（JavaScript 忠实移植）：智能体在解空间中采样、竞争、克隆、杂交。调整参数，观察策略如何演化。",
    "demo.problem": "基准问题",
    "demo.population": "种群上限",
    "demo.generations": "进化代际",
    "demo.mutation": "变异率",
    "demo.elite": "精英比例",
    "demo.seed": "随机种子",
    "demo.speed": "速度",
    "demo.start": "▶ 开始",
    "demo.pause": "⏸ 暂停",
    "demo.reset": "↺ 重置",
    "demo.gen": "第 N 代",
    "demo.best": "最优得分",
    "demo.mean": "平均得分",
    "demo.diversity": "种群多样性",
    "demo.evals": "总评估次数",
    "demo.legend.agent": "智能体（按代际着色）",
    "demo.legend.best": "当代最优 + 轨迹",
    "demo.legend.optimum": "全局最优点",
    "demo.chart.title": "适应度曲线（越高越好）",
    "demo.chart.best": "最优",
    "demo.chart.mean": "平均",
    "demo.world": "解空间（智能体当前位置）",
    "demo.done": "进化完成",
    "how.kicker": "HOW IT WORKS",
    "how.title": "四阶段进化循环",
    "how.sub": "智能体进化的不是分数，而是「如何搜索」本身。",
    "how.phase1": "行动",
    "how.phase1.d": "每个智能体按其策略采样 N 个候选解，保留历史最优（incumbent）。",
    "how.phase2": "评估",
    "how.phase2.d": "按 incumbent 得分排序，记录 best / mean / 多样性等指标。",
    "how.phase3": "选择",
    "how.phase3.d": "精英原样保留；其余父代由锦标赛（每次随机抽 k 个取最优）产生。",
    "how.phase4": "繁殖",
    "how.phase4.d": "父代克隆或基因杂交，子代继承 incumbent 与变异后的策略。",
    "how.genes.title": "被进化的基因",
    "how.genes.sub": "三个基因决定智能体如何搜索 —— 进化就是在搜索这个超参数空间。",
    "how.gene": "基因",
    "how.range": "范围",
    "how.meaning": "语义",
    "how.gene1": "每次行动采样的候选解数量（best-of-N，直接提升期望得分）",
    "how.gene2": "采样围绕当前最优解的集中程度（1.0 = 局部精炼）",
    "how.gene3": "探索步长倍数（高 = 大胆跳跃，利于逃离局部最优）",
    "how.problems.title": "基准问题",
    "how.problems.sub": "全部为最大化问题，最优值 0.0，其余点严格为负。",
    "bench.kicker": "BENCHMARKS",
    "bench.title": "真实运行的数据",
    "bench.sub":
      "以下曲线由 scripts/generate_benchmarks.py 实际运行生成（10 次试验 × 40 代，种群 5→50，确定性 Mock 后端），不是示意图。",
    "bench.tab.sphere": "sphere · 单峰",
    "bench.tab.rastrigin": "rastrigin · 多峰",
    "bench.tab.rosenbrock": "rosenbrock · 香蕉谷",
    "bench.chart1": "最优得分收敛（均值 ± 极值带）",
    "bench.chart2": "策略演化（种群均值）",
    "bench.card.final": "最终最优得分（10 次试验）",
    "bench.card.range": "范围",
    "bench.card.converged": "收敛试验数",
    "bench.card.convgen": "平均收敛代际",
    "bench.card.diversity": "末期多样性",
    "quick.kicker": "QUICKSTART",
    "quick.title": "三十秒开始",
    "quick.sub": "零依赖安装，Python ≥ 3.10。核心 API 只有两行。",
    "arch.kicker": "ARCHITECTURE",
    "arch.title": "代码结构",
    "arch.sub": "纯标准库实现，每个模块职责单一、可独立测试。",
    "footer.tag": "自我克隆的 AI 智能体，通过竞争寻求最优解。",
    "footer.mit": "MIT License",
    "footer.built": "官方网站由 AgentLegion 项目组维护",
    "copied": "已复制",
  },
  en: {
    "nav.demo": "Live demo",
    "nav.how": "How it works",
    "nav.bench": "Benchmarks",
    "nav.quick": "Quickstart",
    "nav.arch": "Architecture",
    "hero.kicker": "AUTONOMOUS AGENT FRAMEWORK · OPEN SOURCE",
    "hero.title": "One Becomes Many",
    "hero.sub":
      "Self-cloning AI agents compete, evolve and optimize on <strong>real objective functions</strong>. Every run is seeded, recorded and auditable — reproducible by design.",
    "hero.cta.demo": "▶ Run the live demo",
    "hero.cta.github": "GitHub repository",
    "hero.stat1": "runtime dependencies",
    "hero.stat2": "unit tests",
    "hero.stat3": "benchmark problems",
    "hero.stat4": "for 20 generations",
    "demo.kicker": "LIVE DEMO",
    "demo.title": "Watch evolution happen",
    "demo.sub":
      "The exact algorithm from the repository runs below (a faithful JavaScript port): agents sample, compete, clone and crossover in the solution space. Tune the parameters and watch strategies evolve.",
    "demo.problem": "Problem",
    "demo.population": "Population cap",
    "demo.generations": "Generations",
    "demo.mutation": "Mutation rate",
    "demo.elite": "Elite rate",
    "demo.seed": "Seed",
    "demo.speed": "Speed",
    "demo.start": "▶ Start",
    "demo.pause": "⏸ Pause",
    "demo.reset": "↺ Reset",
    "demo.gen": "Generation",
    "demo.best": "Best score",
    "demo.mean": "Mean score",
    "demo.diversity": "Diversity",
    "demo.evals": "Evaluations",
    "demo.legend.agent": "agents (colored by generation)",
    "demo.legend.best": "current best + trail",
    "demo.legend.optimum": "global optimum",
    "demo.chart.title": "Fitness curves (higher is better)",
    "demo.chart.best": "best",
    "demo.chart.mean": "mean",
    "demo.world": "Solution space (current positions)",
    "demo.done": "Evolution complete",
    "how.kicker": "HOW IT WORKS",
    "how.title": "The four-phase loop",
    "how.sub": "Agents do not evolve scores — they evolve how they search.",
    "how.phase1": "Act",
    "how.phase1.d": "Each agent samples N candidates per its strategy and keeps its incumbent (best-so-far).",
    "how.phase2": "Evaluate",
    "how.phase2.d": "Rank by incumbent score; record best / mean / diversity metrics.",
    "how.phase3": "Select",
    "how.phase3.d": "Elites survive untouched; remaining parents come from tournaments (draw k, keep the best).",
    "how.phase4": "Reproduce",
    "how.phase4.d": "Parents clone or crossover; children inherit the incumbent and a mutated strategy.",
    "how.genes.title": "The genes that evolve",
    "how.genes.sub": "Three genes decide how an agent searches — evolution searches that hyperparameter space.",
    "how.gene": "Gene",
    "how.range": "Range",
    "how.meaning": "Meaning",
    "how.gene1": "candidates sampled per act (best-of-N effort, pays off directly)",
    "how.gene2": "how tightly samples cluster around the incumbent (1.0 = local refinement)",
    "how.gene3": "exploration spread multiplier (high = bold jumps, escapes local optima)",
    "how.problems.title": "Benchmark problems",
    "how.problems.sub": "All maximization; optimum 0.0, everything else strictly negative.",
    "bench.kicker": "BENCHMARKS",
    "bench.title": "Numbers from real runs",
    "bench.sub":
      "Generated by scripts/generate_benchmarks.py from actual runs (10 trials × 40 generations, population 5→50, deterministic mock backend) — not illustrations.",
    "bench.tab.sphere": "sphere · unimodal",
    "bench.tab.rastrigin": "rastrigin · multimodal",
    "bench.tab.rosenbrock": "rosenbrock · banana valley",
    "bench.chart1": "Best-score convergence (mean ± extremes)",
    "bench.chart2": "Strategy evolution (population mean)",
    "bench.card.final": "Final best score (10 trials)",
    "bench.card.range": "range",
    "bench.card.converged": "converged trials",
    "bench.card.convgen": "mean convergence gen",
    "bench.card.diversity": "final diversity",
    "quick.kicker": "QUICKSTART",
    "quick.title": "Thirty seconds to start",
    "quick.sub": "Zero-dependency install, Python ≥ 3.10. The core API is two lines.",
    "arch.kicker": "ARCHITECTURE",
    "arch.title": "Code structure",
    "arch.sub": "Pure standard library, single-responsibility modules, independently tested.",
    "footer.tag": "Self-cloning AI agents competing for optimal solutions.",
    "footer.mit": "MIT License",
    "footer.built": "Official site maintained by the AgentLegion project",
    "copied": "Copied",
  },
};

let currentLang = "zh";

function t(key) {
  return (I18N[currentLang] && I18N[currentLang][key]) ?? I18N.en[key] ?? key;
}

function applyLang(lang) {
  currentLang = lang;
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.innerHTML = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.title = t(el.getAttribute("data-i18n-title"));
  });
  document.querySelectorAll(".lang-toggle button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });
  renderBenchmarks();
}

/* ---------------- RNG (mirrors random.Random semantics closely enough) ---------------- */
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeGauss(rng) {
  let spare = null;
  return function gauss(mean, std) {
    if (spare !== null) {
      const v = spare;
      spare = null;
      return mean + std * v;
    }
    let u, v, s;
    do {
      u = rng() * 2 - 1;
      v = rng() * 2 - 1;
      s = u * u + v * v;
    } while (s === 0 || s >= 1);
    const mul = Math.sqrt((-2 * Math.log(s)) / s);
    spare = v * mul;
    return mean + std * u * mul;
  };
}

/* ---------------- problems (mirror of agent_legion/problems.py) ---------------- */
const PROBLEMS = {
  sphere: {
    name: "sphere",
    bounds: [-5.12, 5.12],
    optimum: [0, 0],
    evaluate: (x) => -(x[0] * x[0] + x[1] * x[1]),
  },
  rastrigin: {
    name: "rastrigin",
    bounds: [-5.12, 5.12],
    optimum: [0, 0],
    evaluate: (x) => {
      const a = x[0] * x[0] - 10 * Math.cos(2 * Math.PI * x[0]);
      const b = x[1] * x[1] - 10 * Math.cos(2 * Math.PI * x[1]);
      return -(20 + a + b);
    },
  },
  rosenbrock: {
    name: "rosenbrock",
    bounds: [-2.048, 2.048],
    optimum: [1, 1],
    evaluate: (x) => {
      const a = x[1] - x[0] * x[0];
      const b = 1 - x[0];
      return -(100 * a * a + b * b);
    },
  },
};

/* ---------------- strategy (mirror of agent_legion/strategy.py) ---------------- */
const GENE_SPECS = {
  focus: { min: 0, max: 1, kind: "float" },
  iteration: { min: 1, max: 20, kind: "int" },
  risk_taking: { min: 0, max: 1, kind: "float" },
};

function clampGene(name, value) {
  const spec = GENE_SPECS[name];
  if (!isFinite(value)) return spec.min;
  value = Math.max(spec.min, Math.min(spec.max, value));
  return spec.kind === "int" ? Math.round(value) : value;
}

function randomStrategy(rng) {
  return {
    focus: rng(),
    iteration: 1 + Math.floor(rng() * 20),
    risk_taking: rng(),
  };
}

function mutateStrategy(s, rng, gauss, rate, scale = 0.15) {
  const out = { ...s };
  for (const name of Object.keys(GENE_SPECS)) {
    if (rng() < rate) {
      const spec = GENE_SPECS[name];
      const delta = gauss(0, scale * (spec.max - spec.min));
      out[name] = clampGene(name, s[name] + delta);
    }
  }
  return out;
}

function crossoverStrategies(a, b, rng) {
  const out = {};
  for (const name of Object.keys(GENE_SPECS)) {
    out[name] = rng() < 0.5 ? a[name] : b[name];
  }
  return out;
}

function strategyDistance(a, b) {
  let total = 0;
  for (const name of Object.keys(GENE_SPECS)) {
    const spec = GENE_SPECS[name];
    total += Math.abs(a[name] - b[name]) / (spec.max - spec.min);
  }
  return total / 3;
}

/* ---------------- agent + environment (mirror of agent_legion) ---------------- */
class Agent {
  constructor(rng, gauss, opts = {}) {
    this.id = Math.floor(rng() * 0xffffffff).toString(16).slice(0, 8);
    this.generation = opts.generation || 0;
    this.parentIds = opts.parentIds || [];
    this.strategy = opts.strategy || randomStrategy(rng);
    this.incumbent = opts.incumbent || null;
    this.score = -Infinity;
    this.evaluations = 0;
    this._rng = rng;
    this._gauss = gauss;
    this.trail = [];
  }

  act(problem) {
    // MockLLM.propose
    const samples = Math.max(1, Math.floor(this.strategy.iteration));
    const [lo, hi] = problem.bounds;
    const span = hi - lo;
    const base = this.incumbent || [
      lo + this._rng() * span,
      lo + this._rng() * span,
    ];
    let spread =
      span * (0.02 + 0.5 * this.strategy.risk_taking) * (1 - 0.75 * this.strategy.focus);
    spread = Math.max(spread, span * 1e-4);
    let bestX = null;
    let bestScore = -Infinity;
    for (let i = 0; i < samples; i++) {
      const x = [
        Math.max(lo, Math.min(hi, base[0] + this._gauss(0, spread))),
        Math.max(lo, Math.min(hi, base[1] + this._gauss(0, spread))),
      ];
      const score = problem.evaluate(x);
      if (score > bestScore) {
        bestX = x;
        bestScore = score;
      }
    }
    this.evaluations += samples;
    if (this.incumbent === null || bestScore > this.score) {
      this.incumbent = bestX;
      this.score = bestScore;
    }
    return this.score;
  }

  clone(rate) {
    return new Agent(this._rng, this._gauss, {
      generation: this.generation + 1,
      parentIds: [this.id],
      strategy: mutateStrategy(this.strategy, this._rng, this._gauss, rate),
      incumbent: this.incumbent ? [...this.incumbent] : null,
    });
  }

  breed(other, rate) {
    const better = this.score >= other.score ? this : other;
    return new Agent(this._rng, this._gauss, {
      generation: Math.max(this.generation, other.generation) + 1,
      parentIds: [this.id, other.id],
      strategy: mutateStrategy(
        crossoverStrategies(this.strategy, other.strategy, this._rng),
        this._rng,
        this._gauss,
        rate
      ),
      incumbent: better.incumbent ? [...better.incumbent] : null,
    });
  }
}

class Evolution {
  constructor(opts) {
    this.problem = PROBLEMS[opts.problem] || PROBLEMS.rastrigin;
    this.maxAgents = opts.population;
    this.generations = opts.generations;
    this.mutationRate = opts.mutationRate;
    this.eliteRate = opts.eliteRate;
    this.crossoverRate = 0.5;
    this.tournamentSize = 3;
    this.seed = opts.seed;
    this.rng = mulberry32(opts.seed);
    this.gauss = makeGauss(this.rng);
    this.generation = 0;
    this.agents = [];
    this.history = { best: [], mean: [], diversity: [] };
    for (let i = 0; i < Math.min(5, this.maxAgents); i++) {
      this.agents.push(new Agent(this.rng, this.gauss));
    }
  }

  step() {
    const problem = this.problem;
    for (const agent of this.agents) agent.act(problem);
    this.agents.sort((a, b) => b.score - a.score);

    const best = this.agents[0];
    if (best.trail.length === 0 || best.trail[best.trail.length - 1] !== best.incumbent) {
      best.trail.push(best.incumbent ? [...best.incumbent] : null);
      if (best.trail.length > 40) best.trail.shift();
    }

    const scores = this.agents.map((a) => a.score);
    const mean = scores.reduce((s, v) => s + v, 0) / scores.length;
    // diversity: sampled pairwise strategy distance
    let divSum = 0;
    let divCount = 0;
    for (let i = 0; i < this.agents.length; i++) {
      for (let j = i + 1; j < this.agents.length; j += 3) {
        divSum += strategyDistance(this.agents[i].strategy, this.agents[j].strategy);
        divCount++;
      }
    }
    this.history.best.push(best.score);
    this.history.mean.push(mean);
    this.history.diversity.push(divCount ? divSum / divCount : 0);

    const n = this.agents.length;
    const eliteCount = Math.max(1, Math.floor(n * this.eliteRate));
    const elites = this.agents.slice(0, eliteCount);
    const parents = [...elites];
    for (let i = 0; i < n - eliteCount; i++) {
      let bestK = null;
      for (let k = 0; k < this.tournamentSize; k++) {
        const cand = this.agents[Math.floor(this.rng() * n)];
        if (bestK === null || cand.score > bestK.score) bestK = cand;
      }
      parents.push(bestK);
    }
    const children = [];
    const slots = this.maxAgents - eliteCount;
    while (children.length < slots) {
      const parent = parents[children.length % parents.length];
      if (this.rng() < this.crossoverRate && parents.length > 1) {
        const partner = parents[Math.floor(this.rng() * parents.length)];
        children.push(parent.breed(partner, this.mutationRate));
      } else {
        children.push(parent.clone(this.mutationRate));
      }
    }
    this.agents = [...elites, ...children];
    this.generation++;
    return best;
  }
}

/* ---------------- canvas helpers ---------------- */
function fitCanvas(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const w = Math.max(1, Math.round(rect.width * dpr));
  const h = Math.max(1, Math.round(rect.height * dpr));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, w: rect.width, h: rect.height };
}

const VIVID = { violet: [139, 92, 246], cyan: [34, 211, 238], green: [52, 211, 153] };

function lerpColor(a, b, t) {
  return a.map((v, i) => Math.round(v + (b[i] - v) * t));
}

function rgba(c, alpha) {
  return `rgba(${c[0]},${c[1]},${c[2]},${alpha})`;
}

/* ---------------- live demo ---------------- */
const demo = {
  evolution: null,
  running: false,
  raf: null,
  lastStep: 0,
  speedMs: 90,
};

function demoConfig() {
  const val = (id) => document.getElementById(id).value;
  return {
    problem: val("ctl-problem"),
    population: parseInt(val("ctl-population"), 10),
    generations: parseInt(val("ctl-generations"), 10),
    mutationRate: parseFloat(val("ctl-mutation")),
    eliteRate: parseFloat(val("ctl-elite")),
    seed: parseInt(val("ctl-seed"), 10) || 42,
  };
}

function syncControlLabels() {
  const set = (id, out, text) => (document.getElementById(out).textContent = text);
  set("ctl-population", "out-population", document.getElementById("ctl-population").value);
  set("ctl-generations", "out-generations", document.getElementById("ctl-generations").value);
  set(
    "ctl-mutation",
    "out-mutation",
    parseFloat(document.getElementById("ctl-mutation").value).toFixed(2)
  );
  set(
    "ctl-elite",
    "out-elite",
    parseFloat(document.getElementById("ctl-elite").value).toFixed(2)
  );
}

function resetDemo() {
  demo.running = false;
  demo.evolution = new Evolution(demoConfig());
  updateDemoButton();
  renderDemo();
}

function updateDemoButton() {
  const btn = document.getElementById("demo-toggle");
  const done = demo.evolution && demo.evolution.generation >= demo.evolution.generations;
  btn.textContent = demo.running ? t("demo.pause") : done ? t("demo.done") : t("demo.start");
}

function toggleDemo() {
  if (!demo.evolution) resetDemo();
  if (demo.evolution.generation >= demo.evolution.generations) resetDemo();
  demo.running = !demo.running;
  updateDemoButton();
  if (demo.running) {
    demo.lastStep = performance.now();
    demoTick();
  }
}

// setTimeout-based stepping (requestAnimationFrame pauses in background tabs,
// which would freeze the simulation while the user reads another section).
function demoTick() {
  if (!demo.running) return;
  const now = performance.now();
  if (now - demo.lastStep >= demo.speedMs) {
    demo.lastStep = now;
    if (demo.evolution.generation < demo.evolution.generations) {
      demo.evolution.step();
      renderDemo();
    } else {
      demo.running = false;
      updateDemoButton();
      return;
    }
  }
  setTimeout(demoTick, 16);
}

function renderDemo() {
  const evo = demo.evolution;
  if (!evo) return;
  const canvas = document.getElementById("demo-canvas");
  const { ctx, w, h } = fitCanvas(canvas);
  const [lo, hi] = evo.problem.bounds;
  const pad = 26;
  const sx = (x) => pad + ((x - lo) / (hi - lo)) * (w - 2 * pad);
  const sy = (y) => h - pad - ((y - lo) / (hi - lo)) * (h - 2 * pad);

  ctx.clearRect(0, 0, w, h);

  // grid
  ctx.strokeStyle = "rgba(255,255,255,0.05)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const gx = pad + (i / 4) * (w - 2 * pad);
    const gy = pad + (i / 4) * (h - 2 * pad);
    ctx.beginPath();
    ctx.moveTo(gx, pad);
    ctx.lineTo(gx, h - pad);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pad, gy);
    ctx.lineTo(w - pad, gy);
    ctx.stroke();
  }

  // optimum marker
  const [ox, oy] = evo.problem.optimum;
  ctx.strokeStyle = "rgba(251,191,36,0.7)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(sx(ox), sy(oy), 7, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(sx(ox) - 11, sy(oy));
  ctx.lineTo(sx(ox) + 11, sy(oy));
  ctx.moveTo(sx(ox), sy(oy) - 11);
  ctx.lineTo(sx(ox), sy(oy) + 11);
  ctx.stroke();

  // best-agent trail
  const best = evo.agents[0];
  if (best && best.trail.length > 1) {
    ctx.strokeStyle = "rgba(52,211,153,0.55)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    best.trail.forEach((p, i) => {
      if (!p) return;
      i === 0 ? ctx.moveTo(sx(p[0]), sy(p[1])) : ctx.lineTo(sx(p[0]), sy(p[1]));
    });
    ctx.stroke();
  }

  // agents
  const maxGen = Math.max(1, ...evo.agents.map((a) => a.generation));
  for (const agent of evo.agents) {
    if (!agent.incumbent) continue;
    const genT = Math.min(1, agent.generation / Math.max(6, maxGen));
    const color = lerpColor(VIVID.violet, VIVID.cyan, genT);
    const isBest = agent === best;
    ctx.fillStyle = rgba(color, isBest ? 1 : 0.75);
    ctx.beginPath();
    ctx.arc(sx(agent.incumbent[0]), sy(agent.incumbent[1]), isBest ? 6 : 3.4, 0, Math.PI * 2);
    ctx.fill();
    if (isBest) {
      ctx.strokeStyle = "rgba(52,211,153,0.9)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(sx(agent.incumbent[0]), sy(agent.incumbent[1]), 11, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  // readouts
  const scores = evo.agents.map((a) => a.score).filter(Number.isFinite);
  const mean = scores.length ? scores.reduce((s, v) => s + v, 0) / scores.length : NaN;
  document.getElementById("ro-gen").textContent =
    `${evo.generation} / ${evo.generations}`;
  document.getElementById("ro-best").textContent = best ? best.score.toFixed(4) : "—";
  document.getElementById("ro-mean").textContent = Number.isFinite(mean)
    ? mean.toFixed(4)
    : "—";
  document.getElementById("ro-div").textContent =
    (evo.history.diversity[evo.history.diversity.length - 1] || 0).toFixed(3);
  document.getElementById("ro-evals").textContent = evo.agents.reduce(
    (s, a) => s + a.evaluations,
    0
  );

  renderDemoChart();
}

function renderDemoChart() {
  const canvas = document.getElementById("demo-chart");
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.clearRect(0, 0, w, h);
  const best = demo.evolution.history.best;
  const mean = demo.evolution.history.mean;
  if (best.length < 2) return;

  const padL = 46;
  const padR = 10;
  const padT = 12;
  const padB = 20;
  const all = [...best, ...mean];
  let min = Math.min(...all);
  let max = Math.max(...all);
  if (max - min < 1e-9) {
    max += 1;
    min -= 1;
  }
  const span = max - min;
  min -= span * 0.06;
  max += span * 0.06;
  const X = (i) => padL + (i / (demo.evolution.generations - 1)) * (w - padL - padR);
  const Y = (v) => padT + (1 - (v - min) / (max - min)) * (h - padT - padB);

  // gridlines + labels
  ctx.font = "10px " + getComputedStyle(document.body).fontFamily;
  ctx.fillStyle = "rgba(255,255,255,0.35)";
  ctx.strokeStyle = "rgba(255,255,255,0.07)";
  for (let i = 0; i <= 4; i++) {
    const v = min + (i / 4) * (max - min);
    const y = Y(v);
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(w - padR, y);
    ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(v.toFixed(1), padL - 6, y + 3);
  }

  const drawSeries = (data, color, fill) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((v, i) => (i === 0 ? ctx.moveTo(X(i), Y(v)) : ctx.lineTo(X(i), Y(v))));
    ctx.stroke();
    if (fill) {
      const grad = ctx.createLinearGradient(0, padT, 0, h - padB);
      grad.addColorStop(0, "rgba(139,92,246,0.22)");
      grad.addColorStop(1, "rgba(139,92,246,0)");
      ctx.fillStyle = grad;
      ctx.lineTo(X(data.length - 1), h - padB);
      ctx.lineTo(X(0), h - padB);
      ctx.closePath();
      ctx.fill();
    }
  };
  drawSeries(mean, "rgba(34,211,238,0.85)", false);
  drawSeries(best, "rgba(139,92,246,1)", true);
}

/* ---------------- benchmarks ---------------- */
let benchData = null;
let benchProblem = "rastrigin";

async function loadBenchmarks() {
  try {
    const response = await fetch("assets/benchmark-data.json");
    benchData = await response.json();
  } catch (err) {
    console.warn("benchmark data unavailable:", err);
    return;
  }
  renderBenchmarks();
}

function renderBenchmarks() {
  if (!benchData) return;
  const data = benchData.problems[benchProblem];
  if (!data) return;

  document.querySelectorAll(".bench-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.problem === benchProblem);
    tab.textContent = t(`bench.tab.${tab.dataset.problem}`);
  });

  drawBenchConvergence(data);
  drawBenchStrategy(data);

  const final = data.final_best;
  document.getElementById("bench-final").textContent = final.mean.toFixed(4);
  document.getElementById(
    "bench-range"
  ).textContent = `${final.min.toFixed(3)} … ${final.max.toFixed(3)}`;
  document.getElementById("bench-converged").textContent =
    `${data.convergence.converged_trials} / ${data.trials}`;
  document.getElementById("bench-convgen").textContent =
    data.convergence.mean_generation === null
      ? "—"
      : data.convergence.mean_generation.toFixed(1);
  document.getElementById("bench-diversity").textContent =
    data.mean_diversity[data.mean_diversity.length - 1].toFixed(3);
}

function drawLineChart(canvas, series, opts = {}) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.clearRect(0, 0, w, h);
  const padL = 46;
  const padR = 12;
  const padT = 12;
  const padB = 24;
  const n = Math.max(...series.map((s) => s.data.length));
  let min = Infinity;
  let max = -Infinity;
  for (const s of series) {
    for (const v of s.data) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
  }
  if (opts.minZero) min = Math.min(0, min);
  if (max - min < 1e-9) {
    max += 1;
    min -= 1;
  }
  const span = max - min;
  if (!opts.minZero) {
    min -= span * 0.05;
    max += span * 0.08;
  }
  const X = (i) => padL + (i / (n - 1)) * (w - padL - padR);
  const Y = (v) => padT + (1 - (v - min) / (max - min)) * (h - padT - padB);

  ctx.font = "10px " + getComputedStyle(document.body).fontFamily;
  ctx.strokeStyle = "rgba(255,255,255,0.07)";
  ctx.fillStyle = "rgba(255,255,255,0.35)";
  ctx.textAlign = "right";
  for (let i = 0; i <= 4; i++) {
    const v = min + (i / 4) * (max - min);
    const y = Y(v);
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(w - padR, y);
    ctx.stroke();
    ctx.fillText(v.toFixed(opts.decimals ?? 2), padL - 6, y + 3);
  }
  ctx.textAlign = "center";
  for (let i = 0; i <= 4; i++) {
    const gen = Math.round((i / 4) * (n - 1));
    ctx.fillText(gen, X(gen), h - 8);
  }

  // extremes band
  if (opts.band) {
    const lo = opts.band.lo;
    const hi = opts.band.hi;
    ctx.fillStyle = "rgba(139,92,246,0.12)";
    ctx.beginPath();
    for (let i = 0; i < hi.length; i++) ctx.lineTo(X(i), Y(hi[i]));
    for (let i = lo.length - 1; i >= 0; i--) ctx.lineTo(X(i), Y(lo[i]));
    ctx.closePath();
    ctx.fill();
  }

  for (const s of series) {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = s.width || 2;
    if (s.dash) ctx.setLineDash(s.dash);
    ctx.beginPath();
    s.data.forEach((v, i) => (i === 0 ? ctx.moveTo(X(i), Y(v)) : ctx.lineTo(X(i), Y(v))));
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // legend
  let lx = padL + 4;
  ctx.textAlign = "left";
  for (const s of series.filter((s) => !s.hideLegend)) {
    ctx.fillStyle = s.color;
    ctx.fillRect(lx, 6, 14, 3);
    ctx.fillStyle = "rgba(255,255,255,0.55)";
    ctx.fillText(s.label, lx + 19, 11);
    lx += 19 + ctx.measureText(s.label).width + 16;
  }
}

function drawBenchConvergence(data) {
  const hi = [];
  const lo = [];
  for (let i = 0; i < data.generations; i++) {
    const values = data.runs.map((r) => r.best[i]);
    hi.push(Math.max(...values));
    lo.push(Math.min(...values));
  }
  drawLineChart(document.getElementById("bench-chart-1"), [
    { data: data.mean_best, color: "rgba(139,92,246,1)", label: t("demo.chart.best") },
  ], { band: { lo, hi }, decimals: 3 });
}

function drawBenchStrategy(data) {
  drawLineChart(
    document.getElementById("bench-chart-2"),
    [
      { data: data.mean_focus, color: "rgba(139,92,246,1)", label: "focus" },
      { data: data.mean_risk_taking, color: "rgba(251,191,36,1)", label: "risk_taking" },
      {
        data: data.mean_iteration.map((v) => v / 20),
        color: "rgba(34,211,238,1)",
        label: "iteration / 20",
      },
    ],
    { minZero: true, decimals: 2 }
  );
}

/* ---------------- hero constellation ---------------- */
function startHeroCanvas() {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;
  const { ctx, w, h } = fitCanvas(canvas);
  const points = [];
  const count = Math.min(80, Math.floor((w * h) / 16000));
  for (let i = 0; i < count; i++) {
    points.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      r: 1 + Math.random() * 1.8,
    });
  }
  function frame() {
    ctx.clearRect(0, 0, w, h);
    for (const p of points) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;
    }
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 15000) {
          const alpha = (1 - d2 / 15000) * 0.16;
          ctx.strokeStyle = `rgba(139,92,246,${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(points[i].x, points[i].y);
          ctx.lineTo(points[j].x, points[j].y);
          ctx.stroke();
        }
      }
    }
    for (const p of points) {
      ctx.fillStyle = "rgba(34,211,238,0.5)";
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  frame();
}

/* ---------------- misc UI ---------------- */
function setupReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.12 }
  );
  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
}

function setupCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = document.querySelector(btn.dataset.copy);
      if (!target) return;
      const text = target.innerText.trim();
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      const original = btn.textContent;
      btn.textContent = t("copied");
      setTimeout(() => (btn.textContent = original), 1400);
    });
  });
}

function setupLangToggle() {
  document.querySelectorAll(".lang-toggle button").forEach((btn) => {
    btn.addEventListener("click", () => applyLang(btn.dataset.lang));
  });
}

function setupDemoControls() {
  document.getElementById("demo-toggle").addEventListener("click", toggleDemo);
  document.getElementById("demo-reset").addEventListener("click", resetDemo);
  ["ctl-problem", "ctl-population", "ctl-generations", "ctl-mutation", "ctl-elite", "ctl-seed"].forEach(
    (id) => document.getElementById(id).addEventListener("change", resetDemo)
  );
  document.getElementById("ctl-speed").addEventListener("input", (e) => {
    demo.speedMs = 220 - parseInt(e.target.value, 10);
    document.getElementById("out-speed").textContent = e.target.value;
  });
  document.querySelectorAll(".bench-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      benchProblem = tab.dataset.problem;
      renderBenchmarks();
    });
  });
  window.addEventListener("resize", () => {
    renderDemo();
    renderBenchmarks();
  });
}

/* ---------------- boot ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  applyLang("zh");
  setupLangToggle();
  setupCopyButtons();
  setupReveal();
  setupDemoControls();
  syncControlLabels();
  resetDemo();
  startHeroCanvas();
  loadBenchmarks();
});

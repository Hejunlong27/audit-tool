# 审计日常工作协助工具 - 完整开发技术文档

> **版本**: v1.0 | **日期**: 2026-06-23 | **语言**: Python 3.10+
>
> 本文档包含完整的项目架构、技术选型、模块设计、代码实现和部署指南，可直接用于 Trae Code 进行开发。

---

## 目录

- [一、项目概述](#一项目概述)
- [二、技术栈与依赖](#二技术栈与依赖)
- [三、项目目录结构](#三项目目录结构)
- [四、环境搭建](#四环境搭建)
- [五、配置文件](#五配置文件)
- [六、数据库设计](#六数据库设计)
- [七、核心处理层（core/）](#七核心处理层core)
  - [7.1 PDF 表格提取器](#71-pdf-表格提取器)
  - [7.2 PDF 转 Word 转换器](#72-pdf-转-word-转换器)
  - [7.3 OCR 识别引擎](#73-ocr-识别引擎)
  - [7.4 数据分析引擎](#74-数据分析引擎)
  - [7.5 发票识别器](#75-发票识别器)
  - [7.6 合同解析器](#76-合同解析器)
  - [7.7 报告生成器](#77-报告生成器)
- [八、业务逻辑层（biz/）](#八业务逻辑层biz)
  - [8.1 格式转换服务](#81-格式转换服务)
  - [8.2 数据分析服务](#82-数据分析服务)
  - [8.3 发票处理服务](#83-发票处理服务)
  - [8.4 合同审查服务](#84-合同审查服务)
  - [8.5 底稿管理](#85-底稿管理)
  - [8.6 文件管理器](#86-文件管理器)
- [九、用户界面层（ui/）](#九用户界面层ui)
  - [9.1 NiceGUI 主应用](#91-nicegui-主应用)
  - [9.2 格式转换页面](#92-格式转换页面)
  - [9.3 数据分析页面](#93-数据分析页面)
  - [9.4 发票处理页面](#94-发票处理页面)
  - [9.5 合同审查页面](#95-合同审查页面)
  - [9.6 底稿管理页面](#96-底稿管理页面)
  - [9.7 效率工具页面](#97-效率工具页面)
  - [9.8 可复用 UI 组件](#98-可复用-ui-组件)
- [十、程序入口](#十程序入口)
- [十一、测试指南](#十一测试指南)
- [十二、打包与分发](#十二打包与分发)
- [十三、开发路线图](#十三开发路线图)

---

## 一、项目概述

### 1.1 项目目标

开发一个基于 Python 的**本地运行**审计日常工作协助工具，核心定位：

1. **WPS 格式转换平替** — 提供更精准的 PDF 转 Excel、PDF 转 Word 能力
2. **数据分析增强** — 银行流水分析、异常检测、多源对账
3. **文档效率提升** — 审计底稿模板管理、报告自动生成
4. **本地安全运行** — 零网络依赖，数据不离开本机
5. **开箱即用** — 打包为独立可执行文件

### 1.2 功能模块总览

| 模块 | 功能 | 优先级 |
|------|------|--------|
| 智能格式转换 | PDF转Excel、PDF转Word、扫描件OCR、批量处理、PDF合并拆分 | P1 |
| 数据分析引擎 | 银行流水分析、Benford法则、多源对账、趋势分析 | P2 |
| 发票智能处理 | 批量OCR识别、字段提取、查重检测、汇总导出 | P2 |
| 合同审查辅助 | 条款提取、风险评分、交叉检索、到期提醒 | P3 |
| 底稿与报告管理 | 模板库、自动编号、报告生成、档案归档 | P3 |
| 效率工具集 | 文件整理、全文检索、数据清洗、任务管理 | P3 |

### 1.3 设计原则

- **AI 不替代判断，只替代重复劳动** — 所有自动输出必须经过规则校验，最终留人审核确认
- **零网络依赖** — 核心功能全部本地运行，OCR 使用本地 PaddleOCR 模型
- **模块松耦合** — 各模块独立开发、独立测试，通过统一接口通信
- **配置驱动** — 分析规则、识别模板等通过 YAML 配置，无需改代码

---

## 二、技术栈与依赖

### 2.1 核心技术栈

| 技术领域 | 选型 | 版本 | 选型理由 |
|----------|------|------|----------|
| 开发语言 | Python | 3.10+ | 生态丰富，审计人员学习门槛低 |
| PDF 表格提取 | pdfplumber | 0.11+ | 中文有线表格提取效果最佳（坐标推理） |
| PDF 无线表格 | camelot | 2.0+ | stream 模式无线框表格准确率 95.8% |
| PDF 高速处理 | PyMuPDF (fitz) | 1.27+ | C++ 引擎，速度为纯 Python 方案 7 倍 |
| PDF 转 Word | pdf2docx | 最新 | 布局还原率 92%，表格识别率 98% |
| OCR 引擎 | PaddleOCR | PP-OCRv5 | 中文印刷体检测准确率 94.5%，模型约 17MB |
| 数据分析 | pandas + numpy | 最新 | 行业标准，DataFrame 操作强大 |
| 统计检验 | scipy | 最新 | Benford 法则卡方检验、Z-Score、IQR |
| Excel 读写 | openpyxl + pandas | 最新 | openpyxl 处理样式，pandas 处理分析 |
| Word 生成 | python-docx + docxtpl | 最新 | docxtpl 支持 Jinja2 模板语法 |
| 可视化 | pyecharts | 最新 | 交互式图表，支持导出 HTML |
| 全文检索 | Whoosh | 最新 | 纯 Python 倒排索引，轻量无依赖 |
| 本地数据库 | SQLite | 内置 | 零配置，适合指纹库和任务管理 |
| GUI 框架 | NiceGUI | 3.13+ | 纯 Python，UI 现代，Web/桌面双模式 |
| 打包分发 | PyInstaller | 最新 | 编译快约 30 秒，生态最成熟 |

### 2.2 requirements.txt

```txt
# === PDF 处理 ===
pdfplumber>=0.11.0
PyMuPDF>=1.27.0
pdf2docx>=0.5.8
pypdf>=4.0.0

# === OCR ===
paddleocr>=2.9.0
paddlepaddle>=2.6.0

# === 数据分析 ===
pandas>=2.2.0
numpy>=1.26.0
scipy>=1.14.0
networkx>=3.3.0

# === Excel/Word ===
openpyxl>=3.1.0
python-docx>=1.1.0
docxtpl>=0.18.0
Jinja2>=3.1.0

# === 可视化 ===
pyecharts>=2.0.0

# === 全文检索 ===
Whoosh>=2.7.4

# === GUI ===
nicegui>=3.13.0

# === 工具 ===
thefuzz[speedup]>=0.22.0
python-Levenshtein>=0.25.0
PyYAML>=6.0
loguru>=0.7.0
```

---

## 三、项目目录结构

```
audit-assist-tool/
├── main.py                          # 程序入口
├── requirements.txt                 # 依赖清单
├── README.md                        # 项目说明
│
├── config/                          # 配置文件
│   ├── settings.yaml                # 全局配置
│   └── rules/                       # 分析规则
│       ├── benford.yaml             # Benford 法则参数
│       ├── anomaly.yaml             # 异常检测规则
│       └── invoice.yaml             # 发票识别模板
│
├── core/                            # 核心处理层
│   ├── __init__.py
│   ├── base.py                      # 处理器基类
│   ├── pdf_extractor.py             # PDF 表格提取
│   ├── pdf_converter.py             # PDF 转 Word
│   ├── pdf_merger.py                # PDF 合并拆分
│   ├── ocr_engine.py               # OCR 识别引擎
│   ├── data_analyzer.py            # 数据分析引擎
│   ├── invoice_recognizer.py       # 发票识别
│   ├── contract_parser.py          # 合同解析
│   └── report_generator.py          # 报告生成
│
├── biz/                             # 业务逻辑层
│   ├── __init__.py
│   ├── convert_service.py          # 格式转换调度
│   ├── analysis_service.py         # 数据分析调度
│   ├── invoice_service.py          # 发票处理调度
│   ├── contract_service.py         # 合同审查调度
│   ├── working_paper.py            # 底稿管理
│   └── file_manager.py             # 文件管理
│
├── ui/                              # 用户界面层
│   ├── __init__.py
│   ├── app.py                       # NiceGUI 主应用
│   ├── pages/                       # 各功能页面
│   │   ├── __init__.py
│   │   ├── convert.py               # 格式转换页
│   │   ├── analysis.py              # 数据分析页
│   │   ├── invoice.py               # 发票处理页
│   │   ├── contract.py              # 合同审查页
│   │   ├── working_paper.py         # 底稿管理页
│   │   └── utils.py                 # 效率工具页
│   └── components/                  # 可复用 UI 组件
│       ├── __init__.py
│       ├── file_uploader.py         # 文件上传组件
│       ├── data_table.py            # 数据表格组件
│       └── chart_viewer.py         # 图表展示组件
│
├── templates/                       # 模板文件
│   ├── audit_reports/               # 审计报告模板 (.docx)
│   │   └── standard_report.docx
│   └── working_papers/              # 底稿模板 (.docx / .xlsx)
│       ├── cash_count.xlsx
│       ├── bank_confirmation.docx
│       └── aging_analysis.xlsx
│
├── db/                              # 数据库
│   ├── schema.sql                   # SQLite 表结构
│   └── init_db.py                   # 数据库初始化脚本
│
├── tests/                           # 测试
│   ├── __init__.py
│   ├── test_pdf_extractor.py
│   ├── test_ocr_engine.py
│   ├── test_data_analyzer.py
│   └── test_invoice_recognizer.py
│
├── output/                          # 默认输出目录
└── logs/                            # 日志目录
```

---

## 四、环境搭建

### 4.1 创建虚拟环境

```bash
# 创建项目目录
mkdir audit-assist-tool && cd audit-assist-tool

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 升级 pip
pip install --upgrade pip
```

### 4.2 安装依赖

```bash
# 安装核心依赖（不含 OCR，体积较小）
pip install pdfplumber PyMuPDF pdf2docx pypdf pandas numpy scipy openpyxl python-docx docxtpl pyecharts Whoosh nicegui PyYAML loguru thefuzz[speedup]

# 安装 OCR 依赖（可选，体积较大）
pip install paddlepaddle paddleocr

# 安装开发依赖
pip install pytest pytest-cov
```

### 4.3 验证安装

```bash
python -c "
import pdfplumber, fitz, pdf2docx
import pandas, numpy, scipy
import openpyxl, docxtpl
print('核心依赖安装成功')
"

# 验证 OCR（如已安装）
python -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
print('PaddleOCR 安装成功')
"
```

---

## 五、配置文件

### 5.1 config/settings.yaml

```yaml
# 全局配置文件
app:
  name: "审计日常工作协助工具"
  version: "1.0.0"
  debug: false

paths:
  output_dir: "./output"
  template_dir: "./templates"
  log_dir: "./logs"
  db_path: "./data/audit_tool.db"

# PDF 提取配置
pdf_extract:
  # 表格检测策略: auto / lines / text / ocr
  default_strategy: "auto"
  # 跨页表格拼接: 是否启用
  cross_page_merge: true
  # 合并单元格还原: 是否启用
  merge_cells: true
  # 数字格式智能识别
  smart_number_format: true
  # OCR 降级阈值: 当有线/无线提取结果为空时，是否降级到 OCR
  ocr_fallback: true

# OCR 配置
ocr:
  engine: "paddleocr"  # paddleocr / tesseract
  lang: "ch"           # ch / en / ch_en
  use_gpu: false
  # PaddleOCR 模型选择: mobile(轻量) / server(高精度)
  model_type: "server"

# 数据分析配置
analysis:
  # 银行流水分析
  bank_statement:
    # 大额交易阈值（元）
    large_amount_threshold: 500000
    # 拆分交易检测时间窗口（小时）
    split_transaction_window: 24
    # 拆分交易累计阈值（元）
    split_transaction_threshold: 500000
    # 非工作时间定义
    off_hours:
      start: "22:00"
      end: "06:00"
    # 频繁对手方阈值
    frequent_counterparty_threshold: 10
    # 余额异常波动倍数（标准差）
    balance_anomaly_std_multiple: 3

  # Benford 法则
  benford:
    # 显著性水平
    alpha: 0.05
    # 最小样本量
    min_sample_size: 30

  # 对账配置
  reconciliation:
    # 日期容差（天）
    date_tolerance: 3
    # 金额容差（元）
    amount_tolerance: 1.0

# 发票识别配置
invoice:
  # 支持的发票类型
  supported_types:
    - "增值税专用发票"
    - "增值税普通发票"
    - "电子发票"
    - "机动车销售统一发票"
    - "火车票"
  # 查重字段
  dedup_fields:
    - "invoice_code"
    - "invoice_number"
    - "amount"

# 合同审查配置
contract:
  # 需要提取的条款类型
  clause_types:
    - "合同主体"
    - "合同金额"
    - "付款条件"
    - "违约责任"
    - "保密条款"
    - "争议解决方式"
    - "合同期限"
    - "不可抗力"
  # 高风险关键词
  risk_keywords:
    - "不可撤销"
    - "无条件承担"
    - "无限连带责任"
    - "单方面解约"
    - "自动续期"
  # 到期提醒天数
  expiry_warning_days: 30

# 底稿管理配置
working_paper:
  # 编号规则
  numbering:
    prefix_map:
      "资产类": "A"
      "负债类": "L"
      "所有者权益类": "E"
      "收入类": "I"
      "费用类": "F"
      "现金流量类": "C"
    separator: "-"

# GUI 配置
gui:
  title: "审计日常工作协助工具"
  port: 8080
  host: "127.0.0.1"
  reload: false
  # native mode: 打包为桌面窗口
  native: false
  window_size: "1400x900"
```

### 5.2 config/rules/benford.yaml

```yaml
# Benford 法则参数配置
# 理论首位数字概率分布
theoretical_distribution:
  1: 0.301
  2: 0.176
  3: 0.125
  4: 0.097
  5: 0.079
  6: 0.067
  7: 0.058
  8: 0.051
  9: 0.046

# 检验配置
test:
  method: "chi_square"  # chi_square / ks_test
  alpha: 0.05           # 显著性水平
  min_sample: 30        # 最小样本量
```

### 5.3 config/rules/anomaly.yaml

```yaml
# 异常检测规则配置
rules:
  - name: "大额交易"
    type: "threshold"
    field: "amount"
    operator: ">"
    value: 500000
    severity: "high"

  - name: "整额交易"
    type: "pattern"
    field: "amount"
    pattern: "^\\d+0000$"
    severity: "medium"

  - name: "非工作时间交易"
    type: "time_range"
    field: "date"
    exclude_ranges:
      - start: "08:00"
        end: "18:00"
      - weekday_only: true
    severity: "medium"

  - name: "重复交易"
    type: "duplicate"
    fields: ["amount", "counterparty", "date"]
    tolerance_days: 1
    severity: "high"

  - name: "序列断号"
    type: "gap_detection"
    field: "serial_number"
    severity: "low"
```

### 5.4 config/rules/invoice.yaml

```yaml
# 发票识别模板配置
templates:
 增值税专用发票:
    field_patterns:
      invoice_code:
        regex: "发票代码[：:]\\s*(\\d{10,12})"
        group: 1
      invoice_number:
        regex: "发票号码[：:]\\s*(\\d{8})"
        group: 1
      invoice_date:
        regex: "(\\d{4})\\s*年\\s*(\\d{1,2})\\s*月\\s*(\\d{1,2})\\s*日"
        group: "all"
        format: "{1}-{2:0>2}-{3:0>2}"
      amount:
        regex: "(?:合计|金额)[：:]\\s*[¥￥]?([\\d,]+\\.?\\d*)"
        group: 1
      tax:
        regex: "税额[：:]\\s*[¥￥]?([\\d,]+\\.?\\d*)"
        group: 1
      total:
        regex: "价税合计[：:]\\s*[¥￥]?([\\d,]+\\.?\\d*)"
        group: 1
      seller:
        regex: "销方[名称：:]\\s*(.+)"
        group: 1
      buyer:
        regex: "购方[名称：:]\\s*(.+)"
        group: 1

  增值税普通发票:
    field_patterns:
      invoice_code:
        regex: "发票代码[：:]\\s*(\\d{10,12})"
        group: 1
      invoice_number:
        regex: "发票号码[：:]\\s*(\\d{8})"
        group: 1
      invoice_date:
        regex: "(\\d{4})\\s*年\\s*(\\d{1,2})\\s*月\\s*(\\d{1,2})\\s*日"
        group: "all"
        format: "{1}-{2:0>2}-{3:0>2}"
      amount:
        regex: "[¥￥]\\s*([\\d,]+\\.?\\d*)"
        group: 1
      seller:
        regex: "销售方[名称：:]\\s*(.+)"
        group: 1
      buyer:
        regex: "购买方[名称：:]\\s*(.+)"
        group: 1

  电子发票:
    field_patterns:
      invoice_number:
        regex: "发票号码[：:]\\s*(\\d{8,20})"
        group: 1
      invoice_date:
        regex: "(\\d{4})[年-](\\d{1,2})[月-](\\d{1,2})[日号]"
        group: "all"
        format: "{1}-{2:0>2}-{3:0>2}"
      amount:
        regex: "[¥￥]\\s*([\\d,]+\\.?\\d*)"
        group: 1
      total:
        regex: "合\\s*计[：:]\\s*[¥￥]?([\\d,]+\\.?\\d*)"
        group: 1
      seller:
        regex: "销售方名称[：:]\\s*(.+)"
        group: 1
      buyer:
        regex: "购买方名称[：:]\\s*(.+)"
        group: 1
```

---

## 六、数据库设计

### 6.1 db/schema.sql

```sql
-- 发票指纹表：用于查重检测
CREATE TABLE IF NOT EXISTS invoice_fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT NOT NULL UNIQUE,       -- 发票代码_号码_金额
    invoice_code TEXT,                       -- 发票代码
    invoice_number TEXT,                     -- 发票号码
    amount REAL,                            -- 金额
    file_path TEXT,                         -- 来源文件路径
    recognized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_name TEXT DEFAULT '',           -- 所属项目
    notes TEXT DEFAULT ''                    -- 备注
);

-- 发票识别记录表
CREATE TABLE IF NOT EXISTS invoice_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint_id INTEGER,
    invoice_type TEXT,                       -- 发票类型
    invoice_code TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    amount REAL,
    tax REAL,
    total REAL,
    seller TEXT,
    buyer TEXT,
    file_path TEXT,
    recognized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_name TEXT DEFAULT '',
    is_duplicate INTEGER DEFAULT 0,
    FOREIGN KEY (fingerprint_id) REFERENCES invoice_fingerprints(id)
);

-- 审计项目表
CREATE TABLE IF NOT EXISTS audit_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    client_name TEXT,
    audit_period TEXT,
    status TEXT DEFAULT 'active',            -- active / completed / archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 工作底稿表
CREATE TABLE IF NOT EXISTS working_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    paper_number TEXT NOT NULL,              -- 如 A-1-1
    title TEXT NOT NULL,
    category TEXT,                          -- 科目类别
    template_path TEXT,
    output_path TEXT,
    status TEXT DEFAULT 'draft',            -- draft / review / approved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES audit_projects(id)
);

-- 任务管理表
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    assignee TEXT,
    status TEXT DEFAULT 'pending',           -- pending / in_progress / completed
    priority TEXT DEFAULT 'medium',          -- low / medium / high
    due_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES audit_projects(id)
);

-- 文件索引表（全文检索用）
CREATE TABLE IF NOT EXISTS file_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    content_text TEXT,
    project_name TEXT DEFAULT '',
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_invoice_fp ON invoice_fingerprints(fingerprint);
CREATE INDEX IF NOT EXISTS idx_invoice_records_number ON invoice_records(invoice_number);
CREATE INDEX IF NOT EXISTS idx_wp_project ON working_papers(project_id);
CREATE INDEX IF NOT EXISTS idx_wp_number ON working_papers(paper_number);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_file_index_path ON file_index(file_path);
```

### 6.2 db/init_db.py

```python
"""
数据库初始化脚本
"""
import sqlite3
import os
from loguru import logger


def get_db_path() -> str:
    """获取数据库文件路径"""
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'audit_tool.db')


def init_database(db_path: str = None) -> sqlite3.Connection:
    """初始化数据库，创建表结构"""
    if db_path is None:
        db_path = get_db_path()

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    conn.commit()
    logger.info(f"数据库初始化完成: {db_path}")
    return conn


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """获取数据库连接"""
    if db_path is None:
        db_path = get_db_path()

    if not os.path.exists(db_path):
        return init_database(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    init_database()
    print("数据库初始化完成")
```

---

## 七、核心处理层（core/）

### 7.1 处理器基类

```python
# core/__init__.py
```

```python
# core/base.py
"""
处理器基类
所有核心处理器继承此基类，统一输入输出规范
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from loguru import logger


@dataclass
class ProcessResult:
    """处理结果基类"""
    success: bool = True
    data: Any = None
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        logger.warning(msg)

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.success = False
        logger.error(msg)


class BaseProcessor(ABC):
    """处理器基类"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def process(self, *args, **kwargs) -> ProcessResult:
        """处理方法，子类必须实现"""
        pass

    def _validate_input(self, file_path: str) -> bool:
        """验证输入文件是否存在"""
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return False
        return True
```

### 7.2 PDF 表格提取器

```python
# core/pdf_extractor.py
"""
PDF 表格提取器
支持三种策略：有线框表格(pdfplumber)、无线框表格(camelot stream)、扫描件(OCR)
自动检测页面类型并选择最优策略
"""
import os
import re
from typing import Optional
import pandas as pd
from dataclasses import dataclass
from loguru import logger

from core.base import BaseProcessor, ProcessResult


@dataclass
class TableExtractionResult:
    """表格提取结果"""
    tables: list[pd.DataFrame]
    page_numbers: list[int]
    strategy_used: str
    total_tables: int


class PDFTableExtractor(BaseProcessor):
    """PDF 表格提取器"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.ocr_engine = None  # 延迟加载，避免启动时加载 PaddleOCR

    def _detect_page_type(self, pdf_path: str, page_num: int = 0) -> str:
        """
        检测 PDF 页面类型
        返回: 'lined' (有线框) / 'unlined' (无线框) / 'scanned' (扫描件)
        """
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        page = doc[page_num]

        # 检测是否有图片覆盖（扫描件特征）
        images = page.get_images(full=True)
        text_length = len(page.get_text().strip())

        if len(images) > 0 and text_length < 50:
            doc.close()
            return 'scanned'

        # 检测线条/矩形数量（有线框特征）
        drawings = page.get_drawings()
        line_count = sum(1 for d in drawings if d['items'] and len(d['items']) > 0)

        doc.close()

        if line_count > 10:
            return 'lined'
        else:
            return 'unlined'

    def _extract_with_pdfplumber(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 pdfplumber 提取有线框表格"""
        import pdfplumber

        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df = df.dropna(how='all')
                        df = df.dropna(axis=1, how='all')
                        if not df.empty:
                            tables.append(df)
                            logger.info(f"pdfplumber 提取到表格: 第{i+1}页, {len(df)}行x{len(df.columns)}列")
        return tables

    def _extract_with_camelot(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 camelot stream 模式提取无线框表格"""
        try:
            import camelot
        except ImportError:
            logger.warning("camelot 未安装，跳过无线框表格提取")
            return []

        tables = []
        try:
            result = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
            for i, table in enumerate(result._tables):
                df = table.df
                df = df.dropna(how='all')
                df = df.dropna(axis=1, how='all')
                if not df.empty:
                    # 清理列名中的空白
                    df.columns = [str(c).strip() for c in df.columns]
                    tables.append(df)
                    logger.info(f"camelot stream 提取到表格: 第{table.page}页, {len(df)}行x{len(df.columns)}列")
        except Exception as e:
            logger.error(f"camelot 提取失败: {e}")

        return tables

    def _extract_with_ocr(self, pdf_path: str) -> list[pd.DataFrame]:
        """使用 OCR 提取扫描件中的表格"""
        if self.ocr_engine is None:
            try:
                from core.ocr_engine import OCREngine
                self.ocr_engine = OCREngine(self.config.get('ocr', {}))
            except ImportError:
                logger.error("OCR 引擎不可用")
                return []

        # 将 PDF 转为图片后 OCR
        import fitz
        doc = fitz.open(pdf_path)
        tables = []

        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_path = f"/tmp/page_{i}.png"
            pix.save(img_path)

            result = self.ocr_engine.process(img_path)
            if result.success and result.data:
                # 将 OCR 文本尝试解析为表格
                text_lines = result.data.get('text_lines', [])
                # 简单的文本行转 DataFrame
                if text_lines:
                    df = pd.DataFrame([line.split('\t') for line in text_lines if line.strip()])
                    tables.append(df)
                    logger.info(f"OCR 提取到内容: 第{i+1}页")

            os.remove(img_path)

        doc.close()
        return tables

    def _merge_cross_page_tables(self, tables: list[pd.DataFrame]) -> list[pd.DataFrame]:
        """合并跨页表格（检测表头重复出现）"""
        if len(tables) < 2:
            return tables

        merged = [tables[0]]
        for i in range(1, len(tables)):
            current = tables[i]
            prev = merged[-1]

            # 检查当前表头是否与前一表相同
            if list(current.columns) == list(prev.columns):
                # 表头相同，尝试合并
                try:
                    merged_df = pd.concat([prev, current], ignore_index=True)
                    merged[-1] = merged_df
                    logger.info(f"合并跨页表格: 第{len(merged)}组")
                except Exception:
                    merged.append(current)
            else:
                merged.append(current)

        return merged

    def process(
        self,
        pdf_path: str,
        strategy: str = 'auto',
        merge_cross_page: bool = True,
        output_excel: str = None
    ) -> ProcessResult:
        """
        提取 PDF 中的表格

        Args:
            pdf_path: PDF 文件路径
            strategy: 提取策略 (auto/lined/unlined/scanned/pdfplumber/camelot/ocr)
            merge_cross_page: 是否合并跨页表格
            output_excel: 输出 Excel 路径（可选）

        Returns:
            ProcessResult 包含 TableExtractionResult
        """
        result = ProcessResult()

        if not self._validate_input(pdf_path):
            result.add_error(f"PDF 文件不存在: {pdf_path}")
            return result

        try:
            # 确定策略
            if strategy == 'auto':
                page_type = self._detect_page_type(pdf_path)
                logger.info(f"页面类型检测结果: {page_type}")

                if page_type == 'scanned':
                    tables = self._extract_with_ocr(pdf_path)
                    strategy_used = 'ocr'
                elif page_type == 'lined':
                    tables = self._extract_with_pdfplumber(pdf_path)
                    if not tables:
                        tables = self._extract_with_camelot(pdf_path)
                        strategy_used = 'camelot_stream'
                    else:
                        strategy_used = 'pdfplumber'
                else:
                    tables = self._extract_with_camelot(pdf_path)
                    if not tables:
                        tables = self._extract_with_pdfplumber(pdf_path)
                        strategy_used = 'pdfplumber'
                    else:
                        strategy_used = 'camelot_stream'
            elif strategy in ('pdfplumber', 'lined'):
                tables = self._extract_with_pdfplumber(pdf_path)
                strategy_used = 'pdfplumber'
            elif strategy in ('camelot', 'unlined'):
                tables = self._extract_with_camelot(pdf_path)
                strategy_used = 'camelot_stream'
            elif strategy == 'ocr':
                tables = self._extract_with_ocr(pdf_path)
                strategy_used = 'ocr'
            else:
                tables = self._extract_with_pdfplumber(pdf_path)
                strategy_used = 'pdfplumber'

            # OCR 降级
            if not tables and self.config.get('ocr_fallback', True) and strategy != 'ocr':
                result.add_warning("常规提取无结果，降级到 OCR 模式")
                tables = self._extract_with_ocr(pdf_path)
                if tables:
                    strategy_used = 'ocr_fallback'

            # 合并跨页表格
            if merge_cross_page and tables:
                tables = self._merge_cross_page_tables(tables)

            # 输出 Excel
            if output_excel and tables:
                os.makedirs(os.path.dirname(output_excel) or '.', exist_ok=True)
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    for i, table in enumerate(tables):
                        sheet_name = f"Table_{i+1}"[:31]
                        table.to_excel(writer, sheet_name=sheet_name, index=False)
                logger.info(f"表格已导出到: {output_excel}")

            extraction_result = TableExtractionResult(
                tables=tables,
                page_numbers=list(range(len(tables))),
                strategy_used=strategy_used,
                total_tables=len(tables)
            )
            result.data = extraction_result
            result.message = f"成功提取 {len(tables)} 个表格，策略: {strategy_used}"

        except Exception as e:
            result.add_error(f"PDF 表格提取失败: {str(e)}")
            logger.exception(e)

        return result
```

### 7.3 PDF 转 Word 转换器

```python
# core/pdf_converter.py
"""
PDF 转 Word 转换器
基于 pdf2docx 实现，支持批量处理
"""
import os
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class PDFToWordConverter(BaseProcessor):
    """PDF 转 Word 转换器"""

    def process(
        self,
        pdf_path: str,
        output_path: str = None,
        start_page: int = 0,
        end_page: int = None
    ) -> ProcessResult:
        """
        将 PDF 转换为 Word 文档

        Args:
            pdf_path: PDF 文件路径
            output_path: 输出 Word 路径（默认与 PDF 同名 .docx）
            start_page: 起始页（0-indexed）
            end_page: 结束页（None 表示到最后一页）
        """
        result = ProcessResult()

        if not self._validate_input(pdf_path):
            result.add_error(f"PDF 文件不存在: {pdf_path}")
            return result

        try:
            from pdf2docx import Converter

            if output_path is None:
                output_path = os.path.splitext(pdf_path)[0] + '.docx'

            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            cv = Converter(pdf_path)
            cv.convert(output_path, start=start_page, end=end_page)
            cv.close()

            file_size = os.path.getsize(output_path)
            result.data = {'output_path': output_path, 'file_size': file_size}
            result.message = f"PDF 转 Word 完成: {output_path} ({file_size/1024:.1f} KB)"
            logger.info(result.message)

        except ImportError:
            result.add_error("pdf2docx 未安装，请运行: pip install pdf2docx")
        except Exception as e:
            result.add_error(f"PDF 转 Word 失败: {str(e)}")
            logger.exception(e)

        return result

    def batch_convert(
        self,
        pdf_dir: str,
        output_dir: str = None,
        recursive: bool = False
    ) -> ProcessResult:
        """
        批量转换目录下的 PDF 文件

        Args:
            pdf_dir: PDF 文件所在目录
            output_dir: 输出目录（默认与 PDF 同目录）
            recursive: 是否递归子目录
        """
        result = ProcessResult()
        results = []

        if output_dir is None:
            output_dir = pdf_dir

        os.makedirs(output_dir, exist_ok=True)

        pattern = os.path.join(pdf_dir, '**/*.pdf') if recursive else os.path.join(pdf_dir, '*.pdf')
        pdf_files = [f for f in os.popen(f'find {pdf_dir} -name "*.pdf"').read().strip().split('\n') if f]

        if not pdf_files:
            result.message = "未找到 PDF 文件"
            return result

        for pdf_path in pdf_files:
            pdf_path = pdf_path.strip()
            if not pdf_path or not os.path.exists(pdf_path):
                continue

            rel_path = os.path.relpath(pdf_path, pdf_dir)
            out_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.docx')

            sub_result = self.process(pdf_path, out_path)
            results.append({
                'input': pdf_path,
                'output': out_path,
                'success': sub_result.success,
                'message': sub_result.message
            })

        success_count = sum(1 for r in results if r['success'])
        result.data = results
        result.message = f"批量转换完成: {success_count}/{len(results)} 成功"
        logger.info(result.message)

        return result
```

### 7.4 PDF 合并拆分

```python
# core/pdf_merger.py
"""
PDF 合并与拆分
基于 PyMuPDF (fitz) 实现
"""
import os
from typing import List
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class PDFMerger(BaseProcessor):
    """PDF 合并与拆分工具"""

    def merge(self, pdf_paths: List[str], output_path: str) -> ProcessResult:
        """合并多个 PDF 文件"""
        result = ProcessResult()

        import fitz

        merged_doc = fitz.open()
        for path in pdf_paths:
            if not os.path.exists(path):
                result.add_warning(f"文件不存在，已跳过: {path}")
                continue
            doc = fitz.open(path)
            merged_doc.insert_pdf(doc)
            doc.close()

        merged_doc.save(output_path)
        merged_doc.close()

        result.data = {'output_path': output_path, 'page_count': merged_doc.page_count}
        result.message = f"合并完成: {len(pdf_paths)} 个文件 -> {output_path}"
        logger.info(result.message)
        return result

    def split(self, pdf_path: str, output_dir: str, ranges: str = None) -> ProcessResult:
        """
        拆分 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            ranges: 页码范围，如 "1-3,5,7-10"（1-indexed），None 表示逐页拆分
        """
        result = ProcessResult()
        import fitz

        doc = fitz.open(pdf_path)
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_files = []

        if ranges is None:
            # 逐页拆分
            for i in range(len(doc)):
                out_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                new_doc.save(out_path)
                new_doc.close()
                output_files.append(out_path)
        else:
            # 按范围拆分
            parts = ranges.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    start, end = int(start) - 1, int(end) - 1
                else:
                    start = end = int(part) - 1

                out_path = os.path.join(output_dir, f"{base_name}_p{start+1}-{end+1}.pdf")
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end)
                new_doc.save(out_path)
                new_doc.close()
                output_files.append(out_path)

        doc.close()
        result.data = {'output_files': output_files}
        result.message = f"拆分完成: {len(output_files)} 个文件"
        return result
```

### 7.5 OCR 识别引擎

```python
# core/ocr_engine.py
"""
OCR 识别引擎
基于 PaddleOCR PP-OCRv5 实现，支持中文印刷体识别
"""
import os
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class OCREngine(BaseProcessor):
    """OCR 识别引擎"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self._ocr = None

    def _get_ocr_instance(self):
        """延迟加载 PaddleOCR（模型加载耗时较长）"""
        if self._ocr is None:
            from paddleocr import PaddleOCR

            use_gpu = self.config.get('use_gpu', False)
            lang = self.config.get('lang', 'ch')

            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=use_gpu,
                show_log=False,
                # PP-OCRv5 server 模型精度更高
                ocr_version='PP-OCRv5'
            )
            logger.info(f"PaddleOCR 初始化完成 (lang={lang}, gpu={use_gpu})")

        return self._ocr

    def process(self, image_path: str) -> ProcessResult:
        """
        对图片进行 OCR 识别

        Returns:
            ProcessResult.data 包含:
            - text_lines: list[str] 识别到的文本行
            - text_blocks: list[dict] 含位置信息的文本块
            - full_text: str 全部文本拼接
        """
        result = ProcessResult()

        if not self._validate_input(image_path):
            result.add_error(f"图片文件不存在: {image_path}")
            return result

        try:
            ocr = self._get_ocr_instance()
            ocr_result = ocr.ocr(image_path, cls=True)

            if not ocr_result or not ocr_result[0]:
                result.add_warning("OCR 未识别到任何文字")
                result.data = {'text_lines': [], 'text_blocks': [], 'full_text': ''}
                return result

            text_lines = []
            text_blocks = []

            for line in ocr_result[0]:
                bbox, (text, confidence) = line[0], line[1]
                text_lines.append(text)
                text_blocks.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                })

            full_text = '\n'.join(text_lines)

            result.data = {
                'text_lines': text_lines,
                'text_blocks': text_blocks,
                'full_text': full_text
            }
            result.message = f"OCR 识别完成: {len(text_lines)} 行文本"
            logger.info(result.message)

        except ImportError:
            result.add_error("PaddleOCR 未安装，请运行: pip install paddlepaddle paddleocr")
        except Exception as e:
            result.add_error(f"OCR 识别失败: {str(e)}")
            logger.exception(e)

        return result
```

### 7.6 数据分析引擎

```python
# core/data_analyzer.py
"""
数据分析引擎
支持银行流水分析、Benford 法则检验、异常检测、多源对账
"""
import os
from typing import Optional
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class DataAnalyzer(BaseProcessor):
    """数据分析引擎"""

    def analyze_bank_statement(
        self,
        df: pd.DataFrame,
        date_col: str = 'date',
        amount_col: str = 'amount',
        counterparty_col: str = 'counterparty',
        balance_col: str = 'balance',
        config: dict = None
    ) -> ProcessResult:
        """
        银行流水异常分析

        Args:
            df: 银行流水 DataFrame
            date_col: 日期列名
            amount_col: 金额列名
            counterparty_col: 对手方列名
            balance_col: 余额列名
            config: 分析配置
        """
        result = ProcessResult()
        config = config or self.config.get('bank_statement', {})
        anomalies = {}

        try:
            # 确保日期列为 datetime 类型
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')

            # 1. 大额交易
            threshold = config.get('large_amount_threshold', 500000)
            large_tx = df[df[amount_col].abs() >= threshold]
            anomalies['大额交易'] = large_tx.to_dict('records')
            logger.info(f"大额交易: {len(large_tx)} 笔 (阈值: {threshold})")

            # 2. 整额交易
            round_tx = df[df[amount_col].abs() % 10000 == 0]
            anomalies['整额交易'] = round_tx.to_dict('records')
            logger.info(f"整额交易: {len(round_tx)} 笔")

            # 3. 非工作时间交易
            if counterparty_col in df.columns:
                off_hours = config.get('off_hours', {'start': '22:00', 'end': '06:00'})
                start_h = int(off_hours['start'].split(':')[0])
                end_h = int(off_hours['end'].split(':')[0])

                hours = df[date_col].dt.hour
                if start_h > end_h:  # 跨午夜
                    off_time_tx = df[(hours >= start_h) | (hours < end_h)]
                else:
                    off_time_tx = df[(hours >= start_h) & (hours < end_h)]

                # 排除周末
                off_time_tx = off_time_tx[off_time_tx[date_col].dt.dayofweek < 5]
                anomalies['非工作时间交易'] = off_time_tx.to_dict('records')
                logger.info(f"非工作时间交易: {len(off_time_tx)} 笔")

            # 4. 频繁对手方
            if counterparty_col in df.columns:
                freq_threshold = config.get('frequent_counterparty_threshold', 10)
                counterparty_counts = df[counterparty_col].value_counts()
                frequent = counterparty_counts[counterparty_counts >= freq_threshold]
                anomalies['频繁对手方'] = frequent.to_dict()
                logger.info(f"频繁对手方: {len(frequent)} 个 (阈值: {freq_threshold})")

            # 5. 余额异常波动
            if balance_col in df.columns:
                df[balance_col] = pd.to_numeric(df[balance_col], errors='coerce')
                std_multiple = config.get('balance_anomaly_std_multiple', 3)
                daily_change = df[balance_col].diff().abs()
                mean_change = daily_change.mean()
                std_change = daily_change.std()
                threshold_val = mean_change + std_multiple * std_change
                balance_anomaly = df[daily_change > threshold_val]
                anomalies['余额异常波动'] = balance_anomaly.to_dict('records')
                logger.info(f"余额异常波动: {len(balance_anomaly)} 笔")

            # 6. 拆分交易检测
            if counterparty_col in df.columns:
                window_hours = config.get('split_transaction_window', 24)
                split_threshold = config.get('split_transaction_threshold', 500000)
                df_sorted = df.sort_values(date_col)
                df_sorted['time_group'] = df_sorted[date_col].dt.floor(f'{window_hours}H')

                grouped = df_sorted.groupby([counterparty_col, 'time_group'])[amount_col].agg(['sum', 'count'])
                split_suspects = grouped[(grouped['sum'].abs() >= split_threshold) & (grouped['count'] > 1)]
                anomalies['疑似拆分交易'] = split_suspects.reset_index().to_dict('records')
                logger.info(f"疑似拆分交易: {len(split_suspects)} 组")

            result.data = anomalies
            total_anomalies = sum(len(v) for v in anomalies.values() if isinstance(v, list))
            result.message = f"分析完成，发现 {total_anomalies} 条异常记录"

        except Exception as e:
            result.add_error(f"银行流水分析失败: {str(e)}")
            logger.exception(e)

        return result

    def benford_test(
        self,
        data: pd.Series,
        alpha: float = 0.05,
        min_sample: int = 30
    ) -> ProcessResult:
        """
        Benford 法则检验

        Args:
            data: 数值序列（如金额列）
            alpha: 显著性水平
            min_sample: 最小样本量

        Returns:
            包含首位数字分布、卡方检验结果、p 值
        """
        result = ProcessResult()

        try:
            # 过滤正数
            values = data[data > 0].dropna()
            if len(values) < min_sample:
                result.add_warning(f"样本量不足 ({len(values)} < {min_sample})，结果可能不可靠")

            # 提取首位数字
            first_digits = values.astype(str).str[0].astype(int)
            observed = first_digits.value_counts().sort_index()

            # 确保包含 1-9
            for d in range(1, 10):
                if d not in observed.index:
                    observed[d] = 0
            observed = observed.sort_index()

            # 理论分布
            theoretical = pd.Series({
                1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097,
                5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
            })

            expected_counts = theoretical * len(values)

            # 卡方检验
            chi2, p_value = stats.chisquare(observed.values, f_exp=expected_counts.values)

            is_anomaly = p_value < alpha

            result.data = {
                'observed': observed.to_dict(),
                'expected': (expected_counts).to_dict(),
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'alpha': alpha,
                'is_anomaly': is_anomaly,
                'sample_size': len(values),
                'conclusion': '偏离 Benford 分布，可能存在异常' if is_anomaly else '符合 Benford 分布'
            }
            result.message = f"Benford 检验: p={p_value:.4f}, {'异常' if is_anomaly else '正常'}"
            logger.info(result.message)

        except Exception as e:
            result.add_error(f"Benford 法则检验失败: {str(e)}")
            logger.exception(e)

        return result

    def reconcile(
        self,
        df_left: pd.DataFrame,
        df_right: pd.DataFrame,
        key_columns: list,
        amount_col: str,
        date_col: str,
        date_tolerance_days: int = 3,
        amount_tolerance: float = 1.0
    ) -> ProcessResult:
        """
        多源数据对账

        Args:
            df_left: 左表（如银行流水）
            df_right: 右表（如企业账簿）
            key_columns: 匹配关键字段列表
            amount_col: 金额列名
            date_col: 日期列名
            date_tolerance_days: 日期容差（天）
            amount_tolerance: 金额容差
        """
        result = ProcessResult()

        try:
            df_left[date_col] = pd.to_datetime(df_left[date_col], errors='coerce')
            df_right[date_col] = pd.to_datetime(df_right[date_col], errors='coerce')
            df_left[amount_col] = pd.to_numeric(df_left[amount_col], errors='coerce')
            df_right[amount_col] = pd.to_numeric(df_right[amount_col], errors='coerce')

            matched = []
            unmatched_left = []
            unmatched_right = []

            used_right_indices = set()

            for _, left_row in df_left.iterrows():
                found = False
                for j, right_row in df_right.iterrows():
                    if j in used_right_indices:
                        continue

                    # 金额匹配（容差内）
                    amount_diff = abs(left_row[amount_col] - right_row[amount_col])
                    if amount_diff > amount_tolerance:
                        continue

                    # 日期匹配（容差内）
                    date_diff = abs((left_row[date_col] - right_row[date_col]).days)
                    if date_diff > date_tolerance_days:
                        continue

                    matched.append({
                        'left': left_row.to_dict(),
                        'right': right_row.to_dict(),
                        'amount_diff': amount_diff,
                        'date_diff_days': date_diff
                    })
                    used_right_indices.add(j)
                    found = True
                    break

                if not found:
                    unmatched_left.append(left_row.to_dict())

            for j, right_row in df_right.iterrows():
                if j not in used_right_indices:
                    unmatched_right.append(right_row.to_dict())

            result.data = {
                'matched': matched,
                'unmatched_left': unmatched_left,
                'unmatched_right': unmatched_right,
                'match_rate': len(matched) / len(df_left) if len(df_left) > 0 else 0
            }
            result.message = f"对账完成: 匹配 {len(matched)}, 左表未达 {len(unmatched_left)}, 右表未达 {len(unmatched_right)}"

        except Exception as e:
            result.add_error(f"对账失败: {str(e)}")
            logger.exception(e)

        return result
```

### 7.7 发票识别器

```python
# core/invoice_recognizer.py
"""
发票识别器
OCR 识别 + 正则模板提取 + 查重检测
"""
import os
import re
import yaml
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult
from core.ocr_engine import OCREngine


class InvoiceRecognizer(BaseProcessor):
    """发票识别器"""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.ocr_engine = OCREngine(config.get('ocr', {}))
        self.templates = self._load_templates()

    def _load_templates(self) -> dict:
        """加载发票识别模板"""
        template_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'rules', 'invoice.yaml'
        )
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f).get('templates', {})
        return {}

    def _extract_fields(self, text_lines: list[str], invoice_type: str = None) -> dict:
        """从 OCR 文本中提取发票字段"""
        fields = {}

        # 确定使用哪个模板
        templates_to_try = []
        if invoice_type and invoice_type in self.templates:
            templates_to_try.append(self.templates[invoice_type])
        else:
            templates_to_try = list(self.templates.values())

        full_text = '\n'.join(text_lines)

        for template in templates_to_try:
            field_patterns = template.get('field_patterns', {})
            for field_name, pattern_config in field_patterns.items():
                if field_name in fields:
                    continue

                regex = pattern_config['regex']
                group = pattern_config.get('group', 1)
                fmt = pattern_config.get('format', None)

                match = re.search(regex, full_text)
                if match:
                    if group == 'all':
                        value = match.group(0)
                        if fmt:
                            try:
                                value = fmt.format(*match.groups())
                            except (IndexError, KeyError):
                                value = match.group(0)
                    else:
                        value = match.group(group)

                    # 金额字段清理
                    if field_name in ('amount', 'tax', 'total'):
                        try:
                            value = float(str(value).replace(',', ''))
                        except ValueError:
                            value = None

                    fields[field_name] = value

        return fields

    def process(self, image_path: str, project_name: str = '') -> ProcessResult:
        """
        识别单张发票

        Args:
            image_path: 发票图片路径
            project_name: 所属项目名称
        """
        result = ProcessResult()

        # Step 1: OCR 识别
        ocr_result = self.ocr_engine.process(image_path)
        if not ocr_result.success:
            return ocr_result

        text_lines = ocr_result.data['text_lines']

        # Step 2: 正则提取字段
        fields = self._extract_fields(text_lines)

        if not fields:
            result.add_warning("未能提取到任何发票字段")
            result.data = {'fields': {}, 'is_duplicate': False}
            return result

        # Step 3: 查重检测
        fingerprint = self._generate_fingerprint(fields)
        is_duplicate = self._check_duplicate(fingerprint)

        if is_duplicate:
            result.add_warning(f"疑似重复发票: {fingerprint}")

        result.data = {
            'fields': fields,
            'fingerprint': fingerprint,
            'is_duplicate': is_duplicate,
            'file_path': image_path,
            'project_name': project_name
        }
        result.message = f"发票识别完成: 提取 {len(fields)} 个字段" + (" [疑似重复]" if is_duplicate else "")

        return result

    def batch_process(self, image_dir: str, project_name: str = '') -> ProcessResult:
        """批量识别目录下的发票"""
        result = ProcessResult()
        results = []

        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
        files = [f for f in os.listdir(image_dir)
                 if f.lower().endswith(image_extensions)]

        for i, filename in enumerate(files):
            file_path = os.path.join(image_dir, filename)
            sub_result = self.process(file_path, project_name)
            results.append(sub_result.data)
            logger.info(f"[{i+1}/{len(files)}] {filename}: {sub_result.message}")

        success_count = sum(1 for r in results if r.get('fields'))
        result.data = results
        result.message = f"批量识别完成: {success_count}/{len(files)} 成功提取"
        return result

    def _generate_fingerprint(self, fields: dict) -> str:
        """生成发票指纹（用于查重）"""
        parts = [
            str(fields.get('invoice_code', '')),
            str(fields.get('invoice_number', '')),
            str(fields.get('amount', ''))
        ]
        return '_'.join(parts)

    def _check_duplicate(self, fingerprint: str) -> bool:
        """检查是否为重复发票"""
        try:
            from db.init_db import get_connection
            conn = get_connection()
            cursor = conn.execute(
                'SELECT id FROM invoice_fingerprints WHERE fingerprint = ?',
                (fingerprint,)
            )
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception:
            return False
```

### 7.8 合同解析器

```python
# core/contract_parser.py
"""
合同解析器
从合同 PDF/Word 中提取关键条款，进行风险评分
"""
import os
import re
from typing import Optional
import pandas as pd
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class ContractParser(BaseProcessor):
    """合同解析器"""

    # 条款模式正则
    CLAUSE_PATTERNS = {
        '合同主体': r'(甲方|乙方|委托方|受托方|买方|卖方|出租方|承租方)[：:]?\s*(.+?)(?:\n|$)',
        '合同金额': r'(?:合同总金额|合同价款|合同价格|总价)[：:]?\s*[¥￥]?\s*([\d,.]+\s*(?:万|元)?)',
        '付款条件': r'(?:付款方式|付款条件|结算方式|支付方式)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '违约责任': r'(?:违约责任|违约条款|违约金)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '保密条款': r'(?:保密[条款义务]|保密责任)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '争议解决': r'(?:争议解决|争议处理|管辖法院|仲裁)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
        '合同期限': r'(?:合同期限|合同有效期|合同期限为|有效期)[：:]?\s*(.+?)(?:\n|$)',
        '不可抗力': r'(?:不可抗力)[：:]?\s*(.+?)(?:\n\n|\n第|\n\d+\.|$)',
    }

    def _extract_text(self, file_path: str) -> str:
        """从 PDF 或 Word 文件中提取文本"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            import pdfplumber
            text = ''
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            return text

        elif ext in ('.docx', '.doc'):
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])

        elif ext in ('.txt',):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        return ''

    def _extract_clauses(self, text: str) -> dict:
        """提取合同条款"""
        clauses = {}

        for clause_type, pattern in self.CLAUSE_PATTERNS.items():
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                clauses[clause_type] = [m.strip() for m in matches if m.strip()]

        return clauses

    def _assess_risk(self, clauses: dict) -> list[dict]:
        """评估条款风险"""
        risk_keywords = self.config.get('risk_keywords', [
            '不可撤销', '无条件承担', '无限连带责任',
            '单方面解约', '自动续期'
        ])

        risks = []
        all_text = '\n'.join(
            '\n'.join(items) for items in clauses.values()
        )

        for keyword in risk_keywords:
            if keyword in all_text:
                # 找到包含关键词的条款
                for clause_type, items in clauses.items():
                    for item in items:
                        if keyword in item:
                            risks.append({
                                'clause_type': clause_type,
                                'risk_keyword': keyword,
                                'clause_text': item[:200],
                                'severity': 'high' if keyword in ('无限连带责任', '不可撤销') else 'medium'
                            })

        return risks

    def _extract_dates(self, text: str) -> dict:
        """提取合同日期信息"""
        dates = {}

        # 签订日期
        sign_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
        if sign_match:
            dates['sign_date'] = f"{sign_match.group(1)}-{sign_match.group(2):0>2}-{sign_match.group(3):0>2}"

        # 有效期
        period_match = re.search(
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(?:至|到|至-)\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            text
        )
        if period_match:
            dates['start_date'] = f"{period_match.group(1)}-{period_match.group(2):0>2}-{period_match.group(3):0>2}"
            dates['end_date'] = f"{period_match.group(4)}-{period_match.group(5):0>2}-{period_match.group(6):0>2}"

        return dates

    def process(self, file_path: str) -> ProcessResult:
        """解析合同文件"""
        result = ProcessResult()

        if not self._validate_input(file_path):
            result.add_error(f"文件不存在: {file_path}")
            return result

        try:
            text = self._extract_text(file_path)
            if not text.strip():
                result.add_error("文件内容为空")
                return result

            clauses = self._extract_clauses(text)
            risks = self._assess_risk(clauses)
            dates = self._extract_dates(text)

            result.data = {
                'file_path': file_path,
                'clauses': clauses,
                'risks': risks,
                'dates': dates,
                'total_clauses': sum(len(v) for v in clauses.values()),
                'total_risks': len(risks)
            }
            result.message = f"合同解析完成: {result.data['total_clauses']} 个条款, {len(risks)} 个风险点"

        except Exception as e:
            result.add_error(f"合同解析失败: {str(e)}")
            logger.exception(e)

        return result
```

### 7.9 报告生成器

```python
# core/report_generator.py
"""
审计报告生成器
基于 Jinja2 模板 + python-docx 生成审计报告
"""
import os
from typing import Optional
from loguru import logger

from core.base import BaseProcessor, ProcessResult


class ReportGenerator(BaseProcessor):
    """审计报告生成器"""

    def process(
        self,
        template_path: str,
        output_path: str,
        data: dict
    ) -> ProcessResult:
        """
        基于模板生成审计报告

        Args:
            template_path: Word 模板路径 (.docx)
            output_path: 输出文件路径
            data: 填充数据字典
        """
        result = ProcessResult()

        try:
            from docxtpl import DocxTemplate

            if not os.path.exists(template_path):
                result.add_error(f"模板文件不存在: {template_path}")
                return result

            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            doc = DocxTemplate(template_path)
            doc.render(data)
            doc.save(output_path)

            file_size = os.path.getsize(output_path)
            result.data = {'output_path': output_path, 'file_size': file_size}
            result.message = f"报告生成完成: {output_path} ({file_size/1024:.1f} KB)"
            logger.info(result.message)

        except ImportError:
            result.add_error("docxtpl 未安装，请运行: pip install docxtpl")
        except Exception as e:
            result.add_error(f"报告生成失败: {str(e)}")
            logger.exception(e)

        return result

    def generate_from_data(
        self,
        output_path: str,
        title: str,
        client_name: str,
        audit_period: str,
        findings: list[dict],
        conclusion: str
    ) -> ProcessResult:
        """
        快速生成审计报告（使用内置模板）

        Args:
            output_path: 输出路径
            title: 报告标题
            client_name: 被审计单位
            audit_period: 审计期间
            findings: 审计发现列表 [{"issue": "", "risk": "", "suggestion": ""}]
            conclusion: 审计结论
        """
        data = {
            'title': title,
            'client_name': client_name,
            'audit_period': audit_period,
            'findings': findings,
            'conclusion': conclusion,
            'report_date': '2026年6月23日'
        }

        # 查找内置模板
        template_dir = self.config.get('template_dir', './templates/audit_reports')
        template_path = os.path.join(template_dir, 'standard_report.docx')

        if not os.path.exists(template_path):
            # 如果没有模板，使用 python-docx 直接创建
            return self._create_simple_report(output_path, data)

        return self.process(template_path, output_path, data)

    def _create_simple_report(self, output_path: str, data: dict) -> ProcessResult:
        """无模板时直接创建简单报告"""
        result = ProcessResult()

        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()

            # 标题
            title = doc.add_heading(data['title'], level=0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # 基本信息
            doc.add_paragraph(f"被审计单位: {data['client_name']}")
            doc.add_paragraph(f"审计期间: {data['audit_period']}")
            doc.add_paragraph(f"报告日期: {data['report_date']}")

            doc.add_heading('审计发现', level=1)
            for i, finding in enumerate(data.get('findings', []), 1):
                doc.add_heading(f"发现 {i}: {finding.get('issue', '')}", level=2)
                doc.add_paragraph(f"风险等级: {finding.get('risk', '')}")
                doc.add_paragraph(f"建议: {finding.get('suggestion', '')}")

            doc.add_heading('审计结论', level=1)
            doc.add_paragraph(data.get('conclusion', ''))

            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            doc.save(output_path)

            result.data = {'output_path': output_path}
            result.message = f"报告生成完成: {output_path}"

        except Exception as e:
            result.add_error(f"报告创建失败: {str(e)}")

        return result
```

---

## 八、业务逻辑层（biz/）

### 8.1 格式转换服务

```python
# biz/__init__.py
```

```python
# biz/convert_service.py
"""
格式转换服务
调度核心处理层，提供统一的格式转换接口
"""
import os
from typing import Optional
from loguru import logger

from core.pdf_extractor import PDFTableExtractor
from core.pdf_converter import PDFToWordConverter
from core.pdf_merger import PDFMerger
from core.ocr_engine import OCREngine
from core.base import ProcessResult


class ConvertService:
    """格式转换服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.extractor = PDFTableExtractor(config.get('pdf_extract', {}))
        self.converter = PDFToWordConverter()
        self.merger = PDFMerger()
        self.ocr = OCREngine(config.get('ocr', {}))

    def pdf_to_excel(
        self,
        pdf_path: str,
        output_path: str = None,
        strategy: str = 'auto'
    ) -> ProcessResult:
        """PDF 转 Excel"""
        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + '.xlsx'
        return self.extractor.process(
            pdf_path,
            strategy=strategy,
            output_excel=output_path
        )

    def pdf_to_word(
        self,
        pdf_path: str,
        output_path: str = None
    ) -> ProcessResult:
        """PDF 转 Word"""
        return self.converter.process(pdf_path, output_path)

    def ocr_recognize(self, image_path: str) -> ProcessResult:
        """OCR 识别"""
        return self.ocr.process(image_path)

    def batch_pdf_to_excel(self, pdf_dir: str, output_dir: str = None) -> ProcessResult:
        """批量 PDF 转 Excel"""
        if output_dir is None:
            output_dir = pdf_dir

        results = []
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]

        for filename in pdf_files:
            pdf_path = os.path.join(pdf_dir, filename)
            out_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.xlsx')
            sub_result = self.pdf_to_excel(pdf_path, out_path)
            results.append({
                'file': filename,
                'success': sub_result.success,
                'message': sub_result.message
            })
            logger.info(f"[批量转换] {filename}: {sub_result.message}")

        result = ProcessResult()
        success_count = sum(1 for r in results if r['success'])
        result.data = results
        result.message = f"批量 PDF 转 Excel: {success_count}/{len(results)} 成功"
        return result
```

### 8.2 数据分析服务

```python
# biz/analysis_service.py
"""
数据分析服务
"""
import os
import pandas as pd
from loguru import logger

from core.data_analyzer import DataAnalyzer
from core.base import ProcessResult


class AnalysisService:
    """数据分析服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.analyzer = DataAnalyzer(config.get('analysis', {}))

    def load_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """加载数据文件（Excel/CSV）"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.xlsx', '.xls'):
            return pd.read_excel(file_path, **kwargs)
        elif ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8', **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def analyze_bank_statement(self, file_path: str, **kwargs) -> ProcessResult:
        """分析银行流水"""
        df = self.load_data(file_path)
        return self.analyzer.analyze_bank_statement(df, **kwargs)

    def benford_test(self, file_path: str, amount_col: str = 'amount') -> ProcessResult:
        """Benford 法则检验"""
        df = self.load_data(file_path)
        return self.analyzer.benford_test(df[amount_col])

    def reconcile(
        self,
        left_path: str,
        right_path: str,
        key_columns: list,
        amount_col: str,
        date_col: str
    ) -> ProcessResult:
        """多源对账"""
        df_left = self.load_data(left_path)
        df_right = self.load_data(right_path)
        return self.analyzer.reconcile(
            df_left, df_right, key_columns, amount_col, date_col
        )
```

### 8.3 发票处理服务

```python
# biz/invoice_service.py
"""
发票处理服务
"""
import os
import pandas as pd
from loguru import logger

from core.invoice_recognizer import InvoiceRecognizer
from core.base import ProcessResult


class InvoiceService:
    """发票处理服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.recognizer = InvoiceRecognizer(config.get('invoice', {}))

    def recognize_single(self, image_path: str, project_name: str = '') -> ProcessResult:
        """识别单张发票"""
        return self.recognizer.process(image_path, project_name)

    def recognize_batch(self, image_dir: str, project_name: str = '') -> ProcessResult:
        """批量识别发票"""
        return self.recognizer.batch_process(image_dir, project_name)

    def export_to_excel(self, results: list[dict], output_path: str) -> ProcessResult:
        """将识别结果导出为 Excel"""
        result = ProcessResult()

        try:
            rows = []
            for r in results:
                fields = r.get('fields', {})
                rows.append({
                    '文件名': os.path.basename(r.get('file_path', '')),
                    '发票类型': fields.get('invoice_type', ''),
                    '发票代码': fields.get('invoice_code', ''),
                    '发票号码': fields.get('invoice_number', ''),
                    '开票日期': fields.get('invoice_date', ''),
                    '金额': fields.get('amount', ''),
                    '税额': fields.get('tax', ''),
                    '价税合计': fields.get('total', ''),
                    '销售方': fields.get('seller', ''),
                    '购买方': fields.get('buyer', ''),
                    '是否重复': '是' if r.get('is_duplicate') else '否'
                })

            df = pd.DataFrame(rows)
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            df.to_excel(output_path, index=False)

            result.data = {'output_path': output_path, 'count': len(rows)}
            result.message = f"发票汇总导出完成: {output_path} ({len(rows)} 条)"

        except Exception as e:
            result.add_error(f"导出失败: {str(e)}")

        return result
```

### 8.4 合同审查服务

```python
# biz/contract_service.py
"""
合同审查服务
"""
import os
from loguru import logger

from core.contract_parser import ContractParser
from core.base import ProcessResult


class ContractService:
    """合同审查服务"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.parser = ContractParser(config.get('contract', {}))

    def review_contract(self, file_path: str) -> ProcessResult:
        """审查单个合同"""
        return self.parser.process(file_path)

    def batch_review(self, file_dir: str) -> ProcessResult:
        """批量审查合同"""
        result = ProcessResult()
        results = []

        extensions = ('.pdf', '.docx', '.doc', '.txt')
        files = [f for f in os.listdir(file_dir) if f.lower().endswith(extensions)]

        for filename in files:
            file_path = os.path.join(file_dir, filename)
            sub_result = self.parser.process(file_path)
            results.append(sub_result.data)
            logger.info(f"[合同审查] {filename}: {sub_result.message}")

        result.data = results
        total_risks = sum(r.get('total_risks', 0) for r in results)
        result.message = f"批量审查完成: {len(results)} 份合同, {total_risks} 个风险点"
        return result
```

### 8.5 底稿管理

```python
# biz/working_paper.py
"""
工作底稿管理
"""
import os
from loguru import logger

from db.init_db import get_connection
from core.base import ProcessResult


class WorkingPaperManager:
    """工作底稿管理"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_project(self, name: str, client_name: str, audit_period: str) -> ProcessResult:
        """创建审计项目"""
        result = ProcessResult()
        try:
            conn = get_connection()
            cursor = conn.execute(
                'INSERT INTO audit_projects (name, client_name, audit_period) VALUES (?, ?, ?)',
                (name, client_name, audit_period)
            )
            conn.commit()
            project_id = cursor.lastrowid
            conn.close()

            result.data = {'project_id': project_id, 'name': name}
            result.message = f"项目创建成功: {name} (ID: {project_id})"
        except Exception as e:
            result.add_error(f"项目创建失败: {str(e)}")
        return result

    def generate_paper_number(
        self,
        project_id: int,
        category: str,
        sequence: int,
        sub_sequence: int = 0
    ) -> str:
        """
        生成底稿编号

        Args:
            project_id: 项目 ID
            category: 科目类别（如"资产类"）
            sequence: 主序号
            sub_sequence: 子序号
        """
        prefix_map = self.config.get('numbering', {}).get('prefix_map', {
            '资产类': 'A', '负债类': 'L', '所有者权益类': 'E',
            '收入类': 'I', '费用类': 'F', '现金流量类': 'C'
        })
        separator = self.config.get('numbering', {}).get('separator', '-')

        prefix = prefix_map.get(category, 'X')
        if sub_sequence > 0:
            return f"{prefix}{separator}{sequence}{separator}{sub_sequence}"
        return f"{prefix}{separator}{sequence}"

    def list_projects(self) -> ProcessResult:
        """列出所有项目"""
        result = ProcessResult()
        try:
            conn = get_connection()
            rows = conn.execute(
                'SELECT * FROM audit_projects ORDER BY created_at DESC'
            ).fetchall()
            conn.close()

            result.data = [dict(row) for row in rows]
            result.message = f"共 {len(rows)} 个项目"
        except Exception as e:
            result.add_error(f"查询失败: {str(e)}")
        return result

    def list_papers(self, project_id: int) -> ProcessResult:
        """列出项目的所有底稿"""
        result = ProcessResult()
        try:
            conn = get_connection()
            rows = conn.execute(
                'SELECT * FROM working_papers WHERE project_id = ? ORDER BY paper_number',
                (project_id,)
            ).fetchall()
            conn.close()

            result.data = [dict(row) for row in rows]
            result.message = f"共 {len(rows)} 张底稿"
        except Exception as e:
            result.add_error(f"查询失败: {str(e)}")
        return result
```

### 8.6 文件管理器

```python
# biz/file_manager.py
"""
文件管理器
批量文件整理、重命名、全文检索
"""
import os
import re
import hashlib
from typing import Optional
from loguru import logger

from core.base import ProcessResult


class FileManager:
    """文件管理器"""

    def batch_rename(
        self,
        directory: str,
        pattern: str,
        replacement: str,
        extensions: tuple = None
    ) -> ProcessResult:
        """
        批量重命名文件

        Args:
            directory: 目标目录
            pattern: 正则匹配模式
            replacement: 替换字符串
            extensions: 文件扩展名过滤
        """
        result = ProcessResult()
        extensions = extensions or ('.pdf', '.docx', '.xlsx', '.jpg', '.png')
        renamed = []

        for filename in os.listdir(directory):
            if not filename.lower().endswith(extensions):
                continue

            new_name = re.sub(pattern, replacement, filename)
            if new_name != filename:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                os.rename(old_path, new_path)
                renamed.append({'old': filename, 'new': new_name})

        result.data = renamed
        result.message = f"重命名 {len(renamed)} 个文件"
        return result

    def find_duplicates(self, directory: str) -> ProcessResult:
        """查找重复文件（基于 MD5 哈希）"""
        result = ProcessResult()
        hash_map = {}
        duplicates = []

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    if file_hash in hash_map:
                        duplicates.append({
                            'file1': hash_map[file_hash],
                            'file2': filepath
                        })
                    else:
                        hash_map[file_hash] = filepath
                except (IOError, PermissionError):
                    continue

        result.data = duplicates
        result.message = f"发现 {len(duplicates)} 组重复文件"
        return result

    def organize_files(
        self,
        source_dir: str,
        rules: list[dict]
    ) -> ProcessResult:
        """
        按规则整理文件到子目录

        Args:
            source_dir: 源目录
            rules: 整理规则列表 [{"pattern": "regex", "folder": "target_folder"}]
        """
        result = ProcessResult()
        moved = []

        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)
            if os.path.isfile(filepath):
                for rule in rules:
                    if re.search(rule['pattern'], filename):
                        target_dir = os.path.join(source_dir, rule['folder'])
                        os.makedirs(target_dir, exist_ok=True)
                        target_path = os.path.join(target_dir, filename)
                        os.rename(filepath, target_path)
                        moved.append({'file': filename, 'to': rule['folder']})
                        break

        result.data = moved
        result.message = f"整理 {len(moved)} 个文件"
        return result
```

---

## 九、用户界面层（ui/）

### 9.1 NiceGUI 主应用

```python
# ui/__init__.py
```

```python
# ui/app.py
"""
NiceGUI 主应用
审计日常工作协助工具的 Web 界面入口
"""
from nicegui import ui, app

from ui.pages.convert import create_convert_page
from ui.pages.analysis import create_analysis_page
from ui.pages.invoice import create_invoice_page
from ui.pages.contract import create_contract_page
from ui.pages.working_paper import create_working_paper_page
from ui.pages.utils import create_utils_page


@ui.page('/')

@ui.page('/convert')
def convert_page():
    create_convert_page()


@ui.page('/analysis')
def analysis_page():
    create_analysis_page()


@ui.page('/invoice')
def invoice_page():
    create_invoice_page()


@ui.page('/contract')
def contract_page():
    create_contract_page()


@ui.page('/working-paper')
def working_paper_page():
    create_working_paper_page()


@ui.page('/utils')
def utils_page():
    create_utils_page()


def create_main_layout():
    """创建主导航布局"""
    # 侧边导航
    with ui.column().classes('w-48 h-full p-4 bg-gray-50'):
        ui.label('审计协助工具').classes('text-lg font-bold mb-4')

        ui.button('格式转换', on_click=lambda: ui.navigate.to('/convert'))
        ui.button('数据分析', on_click=lambda: ui.navigate.to('/analysis'))
        ui.button('发票处理', on_click=lambda: ui.navigate.to('/invoice'))
        ui.button('合同审查', on_click=lambda: ui.navigate.to('/contract'))
        ui.button('底稿管理', on_click=lambda: ui.navigate.to('/working-paper'))
        ui.button('效率工具', on_click=lambda: ui.navigate.to('/utils'))

    # 主内容区域（由各页面自行填充）
    ui.space()


def main():
    """启动应用"""
    app.add_static_files('/output', './output')

    ui.run(
        title='审计日常工作协助工具',
        host='127.0.0.1',
        port=8080,
        reload=False,
        show=False
    )


if __name__ == '__main__':
    main()
```

### 9.2 格式转换页面

```python
# ui/pages/__init__.py
```

```python
# ui/pages/convert.py
"""
格式转换页面
PDF 转 Excel / PDF 转 Word / OCR 识别
"""
from nicegui import ui, events
import os

from biz.convert_service import ConvertService


def create_convert_page():
    """创建格式转换页面"""
    service = ConvertService()

    ui.label('智能格式转换').classes('text-2xl font-bold')
    ui.label('支持 PDF 转 Excel、PDF 转 Word、扫描件 OCR 识别').classes('text-gray-500')

    # 功能选项卡
    with ui.tabs().classes('w-full') as tabs:
        with ui.tab('PDF 转 Excel'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传 PDF 文件，自动提取表格数据并导出为 Excel').classes('mb-4')

                upload = ui.upload(
                    label='选择 PDF 文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_pdf_to_excel(e, service)
                ).props('accept=.pdf').classes('w-full')

                result_label = ui.label('').classes('mt-4')

        with ui.tab('PDF 转 Word'):
            with ui.card().classes('w-full p-6'):
                ui.label('将 PDF 文档转换为可编辑的 Word 文件').classes('mb-4')

                upload = ui.upload(
                    label='选择 PDF 文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_pdf_to_word(e, service)
                ).props('accept=.pdf').classes('w-full')

                result_label = ui.label('').classes('mt-4')

        with ui.tab('OCR 识别'):
            with ui.card().classes('w-full p-6'):
                ui.label('对扫描件图片/PDF 进行文字识别').classes('mb-4')

                upload = ui.upload(
                    label='选择图片或 PDF',
                    auto_upload=True,
                    on_upload=lambda e: handle_ocr(e, service)
                ).props('accept=.png,.jpg,.jpeg,.bmp,.pdf').classes('w-full')

                ocr_result = ui.textarea('').classes('w-full mt-4').props('rows=10 readonly')

        with ui.tab('批量处理'):
            with ui.card().classes('w-full p-6'):
                ui.label('批量转换整个文件夹的 PDF 文件').classes('mb-4')

                dir_input = ui.input('输入文件夹路径', placeholder='/path/to/pdf/files')
                ui.button('开始批量转换', on_click=lambda: handle_batch(dir_input.value, service))

                batch_result = ui.label('').classes('mt-4')


async def handle_pdf_to_excel(e: events.UploadEventArguments, service):
    """处理 PDF 转 Excel"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    output_path = f'./output/{os.path.splitext(e.name)[0]}.xlsx'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.pdf_to_excel(input_path, output_path)
    ui.notify(result.message, type='positive' if result.success else 'negative')


async def handle_pdf_to_word(e: events.UploadEventArguments, service):
    """处理 PDF 转 Word"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    output_path = f'./output/{os.path.splitext(e.name)[0]}.docx'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.pdf_to_word(input_path, output_path)
    ui.notify(result.message, type='positive' if result.success else 'negative')


async def handle_ocr(e: events.UploadEventArguments, service):
    """处理 OCR 识别"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'

    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.ocr_recognize(input_path)
    if result.success and result.data:
        ocr_text = result.data.get('full_text', '')
        # 更新文本框内容
        ui.notify(f"OCR 识别完成: {len(result.data.get('text_lines', []))} 行文本", type='positive')


async def handle_batch(dir_path: str, service):
    """处理批量转换"""
    if not dir_path or not os.path.isdir(dir_path):
        ui.notify('请输入有效的文件夹路径', type='negative')
        return

    result = service.batch_pdf_to_excel(dir_path, './output/')
    ui.notify(result.message, type='positive' if result.success else 'negative')
```

### 9.3 数据分析页面

```python
# ui/pages/analysis.py
"""
数据分析页面
"""
from nicegui import ui
import os

from biz.analysis_service import AnalysisService


def create_analysis_page():
    """创建数据分析页面"""
    service = AnalysisService()

    ui.label('数据分析引擎').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full') as tabs:
        with ui.tab('银行流水分析'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传银行流水文件（Excel/CSV），自动执行异常检测').classes('mb-4')

                upload = ui.upload(
                    label='选择银行流水文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_bank_analysis(e, service)
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                analysis_result = ui.expansion('分析结果', value=True).classes('w-full mt-4')
                with analysis_result:
                    result_table = ui.table(
                        columns=[
                            {'name': 'type', 'label': '异常类型', 'field': 'type'},
                            {'name': 'count', 'label': '数量', 'field': 'count'},
                        ],
                        rows=[].classes('w-full')
                    )

        with ui.tab('Benford 法则'):
            with ui.card().classes('w-full p-6'):
                ui.label('对金额数据进行 Benford 法则检验，检测异常分布').classes('mb-4')

                upload = ui.upload(
                    label='选择数据文件',
                    auto_upload=True,
                    on_upload=lambda e: handle_benford(e, service)
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                benford_result = ui.label('').classes('mt-4')

        with ui.tab('多源对账'):
            with ui.card().classes('w-full p-6'):
                ui.label('上传两份文件进行自动对账').classes('mb-4')

                upload_left = ui.upload(
                    label='左表（如银行流水）',
                    auto_upload=True
                ).props('accept=.xlsx,.xls,.csv').classes('w-full mb-2')

                upload_right = ui.upload(
                    label='右表（如企业账簿）',
                    auto_upload=True
                ).props('accept=.xlsx,.xls,.csv').classes('w-full')

                ui.button('开始对账', on_click=lambda: ui.notify('请上传两份文件', 'warning'))


async def handle_bank_analysis(e, service):
    """处理银行流水分析"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.analyze_bank_statement(input_path)
    if result.success and result.data:
        rows = [
            {'type': k, 'count': len(v) if isinstance(v, list) else v}
            for k, v in result.data.items()
        ]
        ui.notify(result.message, type='positive')


async def handle_benford(e, service):
    """处理 Benford 法则检验"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.benford_test(input_path)
    if result.success and result.data:
        msg = f"p值: {result.data['p_value']:.4f} - {result.data['conclusion']}"
        ui.notify(msg, type='warning' if result.data.get('is_anomaly') else 'positive')
```

### 9.4 发票处理页面

```python
# ui/pages/invoice.py
"""
发票处理页面
"""
from nicegui import ui
import os

from biz.invoice_service import InvoiceService


def create_invoice_page():
    """创建发票处理页面"""
    service = InvoiceService()

    ui.label('发票智能处理').classes('text-2xl font-bold')

    with ui.card().classes('w-full p-6'):
        ui.label('上传发票图片或 PDF，自动识别票面信息').classes('mb-4')

        upload = ui.upload(
            label='选择发票文件（支持多选）',
            auto_upload=True,
            on_upload=lambda e: handle_invoice(e, service)
        ).props('accept=.png,.jpg,.jpeg,.pdf multiple').classes('w-full')

        invoice_table = ui.table(
            columns=[
                {'name': 'file', 'label': '文件名', 'field': 'file'},
                {'name': 'code', 'label': '发票代码', 'field': 'code'},
                {'name': 'number', 'label': '发票号码', 'field': 'number'},
                {'name': 'amount', 'label': '金额', 'field': 'amount'},
                {'name': 'seller', 'label': '销售方', 'field': 'seller'},
                {'name': 'duplicate', 'label': '是否重复', 'field': 'duplicate'},
            ],
            rows=[].classes('w-full mt-4')
        )

        ui.button('导出 Excel', on_click=lambda: ui.notify('请先上传发票', 'warning'))


async def handle_invoice(e, service):
    """处理发票识别"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.recognize_single(input_path)
    if result.success and result.data:
        fields = result.data.get('fields', {})
        ui.notify(
            f"识别完成: 发票号码 {fields.get('invoice_number', 'N/A')}",
            type='positive' if not result.data.get('is_duplicate') else 'warning'
        )
```

### 9.5 合同审查页面

```python
# ui/pages/contract.py
"""
合同审查页面
"""
from nicegui import ui

from biz.contract_service import ContractService


def create_contract_page():
    """创建合同审查页面"""
    service = ContractService()

    ui.label('合同审查辅助').classes('text-2xl font-bold')

    with ui.card().classes('w-full p-6'):
        ui.label('上传合同文件，自动提取关键条款并评估风险').classes('mb-4')

        upload = ui.upload(
            label='选择合同文件',
            auto_upload=True,
            on_upload=lambda e: handle_contract(e, service)
        ).props('accept=.pdf,.docx,.doc').classes('w-full')

        clauses_expansion = ui.expansion('提取的条款', value=True).classes('w-full mt-4')
        with clauses_expansion:
            clauses_content = ui.column().classes('w-full')

        risks_expansion = ui.expansion('风险点', value=True).classes('w-full mt-2')
        with risks_expansion:
            risks_content = ui.column().classes('w-full')


async def handle_contract(e, service):
    """处理合同审查"""
    content = e.content.read()
    input_path = f'/tmp/{e.name}'
    with open(input_path, 'wb') as f:
        f.write(content)

    result = service.review_contract(input_path)
    if result.success and result.data:
        clauses = result.data.get('clauses', {})
        risks = result.data.get('risks', [])
        ui.notify(result.message, type='positive' if not risks else 'warning')
```

### 9.6 底稿管理页面

```python
# ui/pages/working_paper.py
"""
底稿管理页面
"""
from nicegui import ui

from biz.working_paper import WorkingPaperManager


def create_working_paper_page():
    """创建底稿管理页面"""
    manager = WorkingPaperManager()

    ui.label('底稿与报告管理').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full'):
        with ui.tab('项目管理'):
            with ui.card().classes('w-full p-6'):
                ui.button('新建项目', on_click=lambda: ui.notify('功能开发中', 'info'))

                project_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': '项目名称', 'field': 'name'},
                        {'name': 'client', 'label': '客户', 'field': 'client_name'},
                        {'name': 'period', 'label': '审计期间', 'field': 'audit_period'},
                        {'name': 'status', 'label': '状态', 'field': 'status'},
                    ],
                    rows=[].classes('w-full mt-4')
                )

        with ui.tab('底稿列表'):
            with ui.card().classes('w-full p-6'):
                ui.label('选择项目后查看底稿列表').classes('text-gray-500')

        with ui.tab('报告生成'):
            with ui.card().classes('w-full p-6'):
                ui.label('基于模板生成审计报告').classes('mb-4')
                ui.button('生成报告', on_click=lambda: ui.notify('功能开发中', 'info'))
```

### 9.7 效率工具页面

```python
# ui/pages/utils.py
"""
效率工具页面
"""
from nicegui import ui

from biz.file_manager import FileManager


def create_utils_page():
    """创建效率工具页面"""
    manager = FileManager()

    ui.label('效率工具集').classes('text-2xl font-bold')

    with ui.tabs().classes('w-full'):
        with ui.tab('文件整理'):
            with ui.card().classes('w-full p-6'):
                dir_input = ui.input('文件夹路径', placeholder='/path/to/files')
                pattern_input = ui.input('重命名模式（正则）', value=r'(.*)')
                replace_input = ui.input('替换为', value=r'\1')

                ui.button('执行重命名', on_click=lambda: ui.notify('功能开发中', 'info'))
                ui.button('查找重复文件', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('全文检索'):
            with ui.card().classes('w-full p-6'):
                ui.label('对审计项目文件建立全文索引').classes('mb-4')
                ui.button('建立索引', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('数据清洗'):
            with ui.card().classes('w-full p-6'):
                ui.label('多源数据导入与标准化').classes('mb-4')
                ui.button('导入数据', on_click=lambda: ui.notify('功能开发中', 'info'))

        with ui.tab('任务管理'):
            with ui.card().classes('w-full p-6'):
                ui.label('审计项目任务跟踪').classes('mb-4')
                ui.button('新建任务', on_click=lambda: ui.notify('功能开发中', 'info'))
```

### 9.8 可复用 UI 组件

```python
# ui/components/__init__.py
```

```python
# ui/components/file_uploader.py
"""
文件上传组件
"""
from nicegui import ui, events


class FileUploader:
    """文件上传组件"""

    def __init__(self, accept: str = '.pdf,.xlsx,.csv', multiple: bool = False):
        self.accept = accept
        self.multiple = multiple
        self.uploaded_files = []

    def render(self):
        """渲染上传组件"""
        upload = ui.upload(
            label='选择文件',
            auto_upload=True,
            on_upload=self._on_upload
        ).props(f'accept={self.accept} {"multiple" if self.multiple else ""}')

        return upload

    def _on_upload(self, e: events.UploadEventArguments):
        import tempfile
        import os

        content = e.content.read()
        path = os.path.join(tempfile.gettempdir(), e.name)
        with open(path, 'wb') as f:
            f.write(content)
        self.uploaded_files.append(path)
```

```python
# ui/components/data_table.py
"""
数据表格组件
"""
from nicegui import ui


class DataTable:
    """数据表格组件"""

    def __init__(self, columns: list[dict], rows: list[dict] = None):
        self.columns = columns
        self.rows = rows or []

    def render(self):
        """渲染表格"""
        return ui.table(
            columns=self.columns,
            rows=self.rows
        ).classes('w-full')

    def add_row(self, row: dict):
        """添加行"""
        self.rows.append(row)
```

```python
# ui/components/chart_viewer.py
"""
图表展示组件
"""
from nicegui import ui


class ChartViewer:
    """图表展示组件（基于 pyecharts）"""

    def __init__(self):
        self.charts = []

    def render_bar_chart(self, title: str, x_data: list, y_data: list):
        """渲染柱状图"""
        from pyecharts import options as opts
        from pyecharts.charts import Bar

        bar = (
            Bar()
            .add_xaxis(x_data)
            .add_yaxis(title, y_data)
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )

        html_content = bar.render_embed()
        ui.html(html_content).classes('w-full')

    def render_pie_chart(self, title: str, data_pairs: list):
        """渲染饼图"""
        from pyecharts import options as opts
        from pyecharts.charts import Pie

        pie = (
            Pie()
            .add(title, data_pairs)
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )

        html_content = pie.render_embed()
        ui.html(html_content).classes('w-full')
```

---

## 十、程序入口

```python
# main.py
"""
审计日常工作协助工具 - 程序入口
"""
import os
import sys


def setup_environment():
    """初始化运行环境"""
    # 创建必要目录
    dirs = ['output', 'logs', 'data', 'templates/audit_reports', 'templates/working_papers']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 初始化数据库
    from db.init_db import init_database
    init_database()

    # 配置日志
    from loguru import logger
    logger.add(
        'logs/audit_tool_{time:YYYY-MM-DD}.log',
        rotation='1 day',
        retention='30 days',
        level='INFO',
        encoding='utf-8'
    )


def main():
    """主函数"""
    setup_environment()

    from loguru import logger
    logger.info("审计日常工作协助工具启动中...")

    # 启动 GUI
    from ui.app import main as start_gui
    start_gui()


if __name__ == '__main__':
    main()
```

---

## 十一、测试指南

### 11.1 测试文件结构

```
tests/
├── __init__.py
├── conftest.py                    # pytest fixtures
├── test_pdf_extractor.py          # PDF 提取测试
├── test_ocr_engine.py              # OCR 测试
├── test_data_analyzer.py          # 数据分析测试
└── test_invoice_recognizer.py     # 发票识别测试
```

### 11.2 conftest.py

```python
# tests/conftest.py
"""
pytest 公共 fixtures
"""
import os
import pytest
import pandas as pd


@pytest.fixture
def sample_pdf_path():
    """示例 PDF 文件路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'sample.pdf')


@pytest.fixture
def sample_invoice_path():
    """示例发票图片路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_invoice.jpg')


@pytest.fixture
def sample_bank_statement():
    """示例银行流水 DataFrame"""
    return pd.DataFrame({
        'date': pd.date_range('2026-01-01', periods=100, freq='h'),
        'amount': [100.0, -500.0, 1000000.0, 200.0, -300.0] * 20,
        'counterparty': ['公司A', '公司B', '公司C', '公司A', '公司D'] * 20,
        'balance': [50000.0 + i * 100 for i in range(100)],
        'summary': ['转账', '收款', '付款', '手续费', '存款'] * 20
    })


@pytest.fixture
def config():
    """测试配置"""
    return {
        'pdf_extract': {'ocr_fallback': False},
        'ocr': {'use_gpu': False, 'lang': 'ch'},
        'analysis': {
            'bank_statement': {
                'large_amount_threshold': 500000,
                'off_hours': {'start': '22:00', 'end': '06:00'}
            }
        }
    }
```

### 11.3 test_pdf_extractor.py

```python
# tests/test_pdf_extractor.py
"""
PDF 表格提取器测试
"""
import pytest
import pandas as pd
from core.pdf_extractor import PDFTableExtractor


class TestPDFTableExtractor:

    def test_init(self, config):
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        assert extractor is not None

    def test_detect_page_type_lined(self, config):
        """测试有线框页面检测"""
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        # 需要准备测试 PDF
        # page_type = extractor._detect_page_type('tests/fixtures/lined_table.pdf')
        # assert page_type == 'lined'
        pass

    def test_process_invalid_file(self, config):
        """测试无效文件路径"""
        extractor = PDFTableExtractor(config.get('pdf_extract'))
        result = extractor.process('/nonexistent/file.pdf')
        assert not result.success
        assert len(result.errors) > 0

    def test_benford_theoretical_distribution(self, config):
        """测试 Benford 理论分布"""
        from core.data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer(config.get('analysis', {}))

        # 生成符合 Benford 分布的数据
        import numpy as np
        np.random.seed(42)
        data = np.random.lognormal(mean=5, sigma=2, size=1000)

        result = analyzer.benford_test(pd.Series(data))
        assert result.success
        assert result.data is not None
        assert 'p_value' in result.data
```

### 11.4 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_pdf_extractor.py -v

# 运行并显示覆盖率
pytest tests/ -v --cov=core --cov=biz --cov-report=html
```

---

## 十二、打包与分发

### 12.1 PyInstaller 打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单文件可执行
pyinstaller --onefile \
    --name "审计协助工具" \
    --windowed \
    --add-data "templates:templates" \
    --add-data "config:config" \
    --hidden-import paddleocr \
    --hidden-import nicegui \
    main.py

# 打包后文件在 dist/ 目录下
# dist/审计协助工具.exe (Windows)
# dist/审计协助工具 (Linux/macOS)
```

### 12.2 打包配置文件（PyInstaller spec）

```python
# audit_tool.spec
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'paddleocr',
        'nicegui',
        'pdfplumber',
        'fitz',
        'pdf2docx',
        'docxtpl',
        'pyecharts',
        'whoosh',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='审计协助工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='审计协助工具',
)
```

### 12.3 OCR 模块可选打包

由于 PaddleOCR 依赖较大，建议将 OCR 模块作为可选插件：

```python
# 在 main.py 中添加 OCR 可用性检测
def check_ocr_available() -> bool:
    """检测 OCR 是否可用"""
    try:
        from paddleocr import PaddleOCR
        return True
    except ImportError:
        return False

# 在 UI 中根据检测结果显示/隐藏 OCR 功能
```

---

## 十三、开发路线图

| 阶段 | 时间 | 内容 | 交付物 |
|------|------|------|--------|
| P1 | 第 1-4 周 | 核心转换引擎：PDF转Excel、PDF转Word、OCR、批量处理、UI 框架 | 可独立运行的格式转换工具 |
| P2 | 第 5-8 周 | 数据分析（银行流水、Benford、对账）+ 发票处理（OCR、查重、导出） | 数据分析仪表盘 + 发票处理模块 |
| P3 | 第 9-11 周 | 合同审查 + 底稿管理 + 报告生成 + 效率工具 | 合同审查模块 + 底稿管理系统 |
| P4 | 第 12-13 周 | PyInstaller 打包、性能优化、用户手册、测试 | 可分发的安装包 + 用户手册 |

### 快速启动命令

```bash
# 1. 克隆/创建项目
mkdir audit-assist-tool && cd audit-assist-tool

# 2. 创建虚拟环境并安装依赖
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. 初始化数据库
python db/init_db.py

# 4. 启动应用
python main.py

# 5. 打开浏览器访问
# http://127.0.0.1:8080
```

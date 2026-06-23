# 审计日常工作协助工具 - 开发规范

## 一、项目概述

### 1.1 项目目标

开发一个基于 Python 的**本地运行**审计日常工作协助工具，核心定位：

1. **WPS 格式转换平替** — 提供更精准的 PDF 转 Excel、PDF 转 Word 能力
2. **数据分析增强** — 银行流水分析、异常检测、多源对账
3. **文档效率提升** — 审计底稿模板管理、报告自动生成
4. **本地安全运行** — 零网络依赖，数据不离开本机
5. **开箱即用** — 打包为独立可执行文件

### 1.2 功能模块

| 模块 | 功能 | 优先级 |
|------|------|--------|
| 智能格式转换 | PDF转Excel、PDF转Word、扫描件OCR、批量处理、PDF合并拆分 | P1 |
| 数据分析引擎 | 银行流水分析、Benford法则、多源对账、趋势分析 | P2 |
| 发票智能处理 | 批量OCR识别、字段提取、查重检测、汇总导出 | P2 |
| 合同审查辅助 | 条款提取、风险评分、交叉检索、到期提醒 | P3 |
| 底稿与报告管理 | 模板库、自动编号、报告生成、档案归档 | P3 |
| 效率工具集 | 文件整理、全文检索、数据清洗、任务管理 | P3 |

### 1.3 技术栈

| 技术领域 | 选型 | 说明 |
|----------|------|------|
| 开发语言 | Python | 3.10+ |
| PDF 表格提取 | pdfplumber + camelot | 有线/无线表格提取 |
| PDF 处理 | PyMuPDF (fitz) | 高速处理 |
| PDF 转 Word | pdf2docx | 布局还原率 92% |
| OCR 引擎 | PaddleOCR PP-OCRv5 | 中文印刷体准确率 94.5% |
| 数据分析 | pandas + numpy + scipy | 行业标准 |
| GUI 框架 | NiceGUI | 纯 Python，Web/桌面双模式 |
| 本地数据库 | SQLite | 零配置 |
| 打包分发 | PyInstaller | 编译快，生态成熟 |

### 1.4 设计原则

- **AI 不替代判断，只替代重复劳动** — 所有自动输出必须经过规则校验，最终留人审核确认
- **零网络依赖** — 核心功能全部本地运行，OCR 使用本地 PaddleOCR 模型
- **模块松耦合** — 各模块独立开发、独立测试，通过统一接口通信
- **配置驱动** — 分析规则、识别模板等通过 YAML 配置，无需改代码

---

## 二、项目结构

```
audit-assist-tool/
├── main.py                          # 程序入口
├── requirements.txt                 # 依赖清单
├── config/                          # 配置文件
│   ├── settings.yaml                # 全局配置
│   └── rules/                       # 分析规则
│       ├── benford.yaml             # Benford 法则参数
│       ├── anomaly.yaml             # 异常检测规则
│       └── invoice.yaml             # 发票识别模板
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
├── biz/                             # 业务逻辑层
│   ├── __init__.py
│   ├── convert_service.py          # 格式转换调度
│   ├── analysis_service.py         # 数据分析调度
│   ├── invoice_service.py          # 发票处理调度
│   ├── contract_service.py         # 合同审查调度
│   ├── working_paper.py            # 底稿管理
│   └── file_manager.py             # 文件管理
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
├── templates/                       # 模板文件
│   ├── audit_reports/               # 审计报告模板 (.docx)
│   └── working_papers/              # 底稿模板 (.docx / .xlsx)
├── db/                              # 数据库
│   ├── schema.sql                   # SQLite 表结构
│   └── init_db.py                   # 数据库初始化脚本
├── tests/                           # 测试
├── output/                          # 默认输出目录
└── logs/                            # 日志目录
```

---

## 三、核心模块规范

### 3.1 核心处理层 (core/)

#### 处理器基类 (base.py)
- 所有处理器继承 `BaseProcessor`
- 统一返回 `ProcessResult` 数据类
- 包含 `success`, `data`, `message`, `warnings`, `errors` 字段

#### PDF 表格提取器 (pdf_extractor.py)
- 三种策略：有线框表格(pdfplumber)、无线框表格(camelot stream)、扫描件(OCR)
- 自动检测页面类型并选择最优策略
- 支持跨页表格拼接
- 支持 OCR 降级

#### PDF 转 Word (pdf_converter.py)
- 基于 pdf2docx 实现
- 支持批量处理
- 布局还原率 92%，表格识别率 98%

#### OCR 识别引擎 (ocr_engine.py)
- 基于 PaddleOCR PP-OCRv5
- 延迟加载避免启动耗时
- 支持中文印刷体识别

#### 数据分析引擎 (data_analyzer.py)
- 银行流水异常分析：大额交易、整额交易、非工作时间交易、频繁对手方、余额异常波动、拆分交易检测
- Benford 法则检验：卡方检验、p 值计算
- 多源数据对账：支持日期容差和金额容差

#### 发票识别器 (invoice_recognizer.py)
- OCR 识别 + 正则模板提取
- 支持增值税专用发票、增值税普通发票、电子发票等
- 查重检测基于指纹库

#### 合同解析器 (contract_parser.py)
- 条款提取：合同主体、金额、付款条件、违约责任、保密条款、争议解决、合同期限、不可抗力
- 风险评分：高风险关键词检测

#### 报告生成器 (report_generator.py)
- 基于 Jinja2 模板 + python-docx
- 支持自定义模板

### 3.2 业务逻辑层 (biz/)

- `ConvertService`: 格式转换调度
- `AnalysisService`: 数据分析调度
- `InvoiceService`: 发票处理调度
- `ContractService`: 合同审查调度
- `WorkingPaperManager`: 底稿管理
- `FileManager`: 文件管理

### 3.3 用户界面层 (ui/)

基于 NiceGUI 框架，页面路由：
- `/` - 首页
- `/convert` - 格式转换
- `/analysis` - 数据分析
- `/invoice` - 发票处理
- `/contract` - 合同审查
- `/working-paper` - 底稿管理
- `/utils` - 效率工具

---

## 四、数据库设计

### 4.1 表结构

- `invoice_fingerprints`: 发票指纹表（用于查重）
- `invoice_records`: 发票识别记录表
- `audit_projects`: 审计项目表
- `working_papers`: 工作底稿表
- `tasks`: 任务管理表
- `file_index`: 文件索引表（全文检索用）

---

## 五、配置规范

### 5.1 config/settings.yaml
- 全局配置：应用信息、路径配置
- PDF 提取配置：策略、跨页合并、OCR 降级
- OCR 配置：引擎选择、语言、GPU
- 数据分析配置：银行流水阈值、Benford 参数、对账容差
- 发票识别配置：支持类型、查重字段
- 合同审查配置：条款类型、风险关键词
- GUI 配置：标题、端口、窗口大小

### 5.2 config/rules/*.yaml
- `benford.yaml`: Benford 法则理论分布和检验参数
- `anomaly.yaml`: 异常检测规则
- `invoice.yaml`: 发票识别模板和字段正则

---

## 六、验收标准

### 6.1 P1 核心功能
- [ ] PDF 转 Excel 正常工作
- [ ] PDF 转 Word 正常工作
- [ ] OCR 识别正常工作
- [ ] 批量处理功能正常
- [ ] NiceGUI 界面正常启动

### 6.2 P2 数据分析
- [ ] 银行流水分析正常
- [ ] Benford 法则检验正常
- [ ] 多源对账正常
- [ ] 发票识别和查重正常
- [ ] 发票汇总导出正常

### 6.3 P3 高级功能
- [ ] 合同审查正常
- [ ] 底稿管理正常
- [ ] 报告生成正常
- [ ] 效率工具正常

### 6.4 部署
- [ ] PyInstaller 打包成功
- [ ] 可执行文件独立运行

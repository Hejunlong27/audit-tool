# 审计日常工作协助工具 - 开发任务清单

## 第一阶段：项目初始化 (P1)

### 1.1 创建项目基础结构
- [x] 创建项目根目录 `audit-assist-tool/`
- [x] 创建 `requirements.txt` 依赖清单
- [x] 创建目录结构：core/, biz/, ui/, ui/pages/, ui/components/, config/, config/rules/, db/, tests/, templates/, templates/audit_reports/, templates/working_papers/, output/, logs/, data/
- [x] 创建 `__init__.py` 文件

### 1.2 创建配置文件
- [x] 创建 `config/settings.yaml` 全局配置
- [x] 创建 `config/rules/benford.yaml`
- [x] 创建 `config/rules/anomaly.yaml`
- [x] 创建 `config/rules/invoice.yaml`

### 1.3 创建数据库
- [x] 创建 `db/schema.sql` 表结构
- [x] 创建 `db/init_db.py` 数据库初始化脚本

---

## 第二阶段：核心处理层 (P1)

### 2.1 基础模块
- [x] 创建 `core/base.py` 处理器基类和 ProcessResult

### 2.2 PDF 处理模块
- [x] 创建 `core/pdf_extractor.py` PDF 表格提取器
- [x] 创建 `core/pdf_converter.py` PDF 转 Word
- [x] 创建 `core/pdf_merger.py` PDF 合并拆分

### 2.3 OCR 模块
- [x] 创建 `core/ocr_engine.py` OCR 识别引擎

### 2.4 数据分析模块
- [x] 创建 `core/data_analyzer.py` 数据分析引擎

### 2.5 发票与合同模块
- [x] 创建 `core/invoice_recognizer.py` 发票识别器
- [x] 创建 `core/contract_parser.py` 合同解析器
- [x] 创建 `core/report_generator.py` 报告生成器

---

## 第三阶段：业务逻辑层 (P1)

- [x] 创建 `biz/__init__.py`
- [x] 创建 `biz/convert_service.py` 格式转换服务
- [x] 创建 `biz/analysis_service.py` 数据分析服务
- [x] 创建 `biz/invoice_service.py` 发票处理服务
- [x] 创建 `biz/contract_service.py` 合同审查服务
- [x] 创建 `biz/working_paper.py` 底稿管理
- [x] 创建 `biz/file_manager.py` 文件管理器

---

## 第四阶段：用户界面层 (P1)

### 4.1 UI 组件
- [x] 创建 `ui/__init__.py`
- [x] 创建 `ui/components/__init__.py`
- [x] 创建 `ui/components/file_uploader.py` 文件上传组件
- [x] 创建 `ui/components/data_table.py` 数据表格组件
- [x] 创建 `ui/components/chart_viewer.py` 图表展示组件

### 4.2 UI 页面
- [x] 创建 `ui/pages/__init__.py`
- [x] 创建 `ui/pages/convert.py` 格式转换页面
- [x] 创建 `ui/pages/analysis.py` 数据分析页面
- [x] 创建 `ui/pages/invoice.py` 发票处理页面
- [x] 创建 `ui/pages/contract.py` 合同审查页面
- [x] 创建 `ui/pages/working_paper.py` 底稿管理页面
- [x] 创建 `ui/pages/utils.py` 效率工具页面

### 4.3 主应用
- [x] 创建 `ui/app.py` NiceGUI 主应用

---

## 第五阶段：程序入口与模板 (P1)

- [x] 创建 `main.py` 程序入口
- [x] 创建 `templates/audit_reports/standard_report.docx` 标准审计报告模板
- [x] 创建示例底稿模板

---

## 第六阶段：测试 (P2)

- [x] 创建 `tests/__init__.py`
- [x] 创建 `tests/conftest.py` pytest fixtures
- [x] 创建 `tests/test_pdf_extractor.py`
- [x] 创建 `tests/test_ocr_engine.py`
- [x] 创建 `tests/test_data_analyzer.py`
- [x] 创建 `tests/test_invoice_recognizer.py`

---

## 第七阶段：打包与部署 (P3)

- [x] 创建 `audit_tool.spec` PyInstaller 配置文件
- [ ] 执行打包测试
- [ ] 验证可执行文件运行

---

## 任务依赖关系

```
1.1 项目基础结构
    ↓
2.1 基础模块 + 1.3 数据库
    ↓
2.2 PDF处理模块 → 3.1 格式转换服务
2.3 OCR模块 → 3.1 格式转换服务, 3.2 发票服务
2.4 数据分析模块 → 3.2 数据分析服务
2.5 发票合同模块 → 3.3 发票服务, 3.4 合同服务
    ↓
4.1 UI组件 ← 4.2 UI页面 ← 4.3 主应用
    ↓
5.1 程序入口
    ↓
6.1 测试
    ↓
7.1 打包部署
```

---

## 快速验证命令

```bash
# 验证核心依赖
python -c "import pdfplumber, fitz, pdf2docx, pandas, numpy, scipy; print('核心依赖安装成功')"

# 验证 OCR
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功')"

# 初始化数据库
python db/init_db.py

# 启动应用
python main.py
```

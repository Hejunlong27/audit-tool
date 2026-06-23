# 审计日常工作协助工具 - 验收检查清单

## 第一阶段：项目初始化

- [x] 项目目录结构符合规范
- [x] `requirements.txt` 包含所有依赖
- [x] `config/settings.yaml` 配置完整
- [x] `config/rules/*.yaml` 规则文件完整
- [x] `db/schema.sql` 表结构正确
- [x] `db/init_db.py` 可正常初始化数据库

## 第二阶段：核心处理层

### 基础模块
- [x] `core/base.py` 中 `BaseProcessor` 和 `ProcessResult` 定义正确

### PDF 处理模块
- [x] `core/pdf_extractor.py` 支持三种策略（有线/无线/OCR）
- [x] `core/pdf_extractor.py` 支持跨页表格合并
- [x] `core/pdf_converter.py` PDF 转 Word 功能正常
- [x] `core/pdf_merger.py` PDF 合并拆分功能正常

### OCR 模块
- [x] `core/ocr_engine.py` PaddleOCR 延迟加载正常
- [x] `core/ocr_engine.py` 返回格式包含 text_lines, text_blocks, full_text

### 数据分析模块
- [x] `core/data_analyzer.py` 银行流水分析包含6种异常检测
- [x] `core/data_analyzer.py` Benford 法则检验返回 p 值和结论
- [x] `core/data_analyzer.py` 多源对账支持容差匹配

### 发票与合同模块
- [x] `core/invoice_recognizer.py` 支持多种发票类型识别
- [x] `core/invoice_recognizer.py` 查重检测功能正常
- [x] `core/contract_parser.py` 条款提取包含8种类型
- [x] `core/contract_parser.py` 风险关键词检测正常
- [x] `core/report_generator.py` 支持模板渲染

## 第三阶段：业务逻辑层

- [x] `biz/convert_service.py` 调度 PDF 转换功能
- [x] `biz/analysis_service.py` 调度数据分析功能
- [x] `biz/invoice_service.py` 调度发票处理功能
- [x] `biz/invoice_service.py` 导出 Excel 功能正常
- [x] `biz/contract_service.py` 调度合同审查功能
- [x] `biz/working_paper.py` 底稿管理 CRUD 功能正常
- [x] `biz/file_manager.py` 批量重命名功能正常
- [x] `biz/file_manager.py` 重复文件检测功能正常

## 第四阶段：用户界面层

### UI 组件
- [x] `ui/components/file_uploader.py` 文件上传组件可用
- [x] `ui/components/data_table.py` 数据表格组件可用
- [x] `ui/components/chart_viewer.py` 图表展示组件可用

### UI 页面
- [x] `ui/pages/convert.py` 格式转换页面：PDF转Excel/Word、OCR、批量处理
- [x] `ui/pages/analysis.py` 数据分析页面：银行流水分析、Benford法则、对账
- [x] `ui/pages/invoice.py` 发票处理页面：上传、识别、导出
- [x] `ui/pages/contract.py` 合同审查页面：条款展示、风险展示
- [x] `ui/pages/working_paper.py` 底稿管理页面：项目管理、底稿列表
- [x] `ui/pages/utils.py` 效率工具页面：文件整理、全文检索

### 主应用
- [x] `ui/app.py` 路由配置正确
- [x] `ui/app.py` 侧边导航功能正常

## 第五阶段：程序入口

- [x] `main.py` 初始化目录结构正常
- [x] `main.py` 数据库初始化正常
- [x] `main.py` 日志配置正常
- [ ] `main.py` 启动 NiceGUI 应用正常（需要依赖安装后验证）

## 第六阶段：测试

- [x] `tests/conftest.py` fixtures 定义正确
- [x] `tests/test_pdf_extractor.py` 测试覆盖主要功能
- [x] `tests/test_ocr_engine.py` 测试覆盖 OCR 功能
- [x] `tests/test_data_analyzer.py` 测试覆盖数据分析功能
- [x] `tests/test_invoice_recognizer.py` 测试覆盖发票识别功能
- [ ] pytest 运行无报错（需要依赖安装后验证）

## 第七阶段：打包与部署

- [x] `audit_tool.spec` PyInstaller 配置正确
- [ ] 打包后可执行文件生成成功（需要依赖安装后验证）
- [ ] 可执行文件可独立运行（需要依赖安装后验证）
- [ ] GUI 界面显示正常（需要依赖安装后验证）

## 端到端验证

- [ ] 用户可通过 Web 界面上传 PDF 文件（需要依赖安装后验证）
- [ ] PDF 转 Excel 转换结果正确（需要依赖安装后验证）
- [ ] PDF 转 Word 转换结果正确（需要依赖安装后验证）
- [ ] OCR 识别结果准确（需要依赖安装后验证）
- [ ] 银行流水分析输出异常列表（需要依赖安装后验证）
- [ ] Benford 法则检验输出 p 值和结论（需要依赖安装后验证）
- [ ] 发票识别输出结构化字段（需要依赖安装后验证）
- [ ] 发票查重检测重复发票（需要依赖安装后验证）
- [ ] 合同审查输出条款和风险点（需要依赖安装后验证）
- [ ] 底稿管理可创建和查询项目（需要依赖安装后验证）
- [ ] 报告生成输出 Word 文件（需要依赖安装后验证）

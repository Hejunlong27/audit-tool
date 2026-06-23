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
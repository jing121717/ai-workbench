-- AI Workbench 代码开发工作台 - 数据库迁移脚本
-- 运行前请备份数据库！

-- =============================================
-- 1. 代码项目表
-- =============================================
CREATE TABLE IF NOT EXISTS `code_projects` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL COMMENT '项目名称',
    `local_path` VARCHAR(1000) COMMENT '本地路径',
    `is_git_repo` BOOLEAN DEFAULT FALSE COMMENT '是否Git仓库',
    `git_remote_url` VARCHAR(500) COMMENT 'Git远程地址',
    `git_current_branch` VARCHAR(100) COMMENT '当前分支',
    `tech_stack` JSON COMMENT '技术栈列表',
    `summary` TEXT COMMENT '项目简介',
    `project_tree` JSON COMMENT '项目结构树',
    `languages_stats` JSON COMMENT '语言统计',
    `total_files` INT DEFAULT 0,
    `total_units` INT DEFAULT 0,
    `owner_id` INT NOT NULL,
    `kb_id` INT COMMENT '关联知识库ID',
    `is_active` BOOLEAN DEFAULT TRUE,
    `last_synced_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_owner_id` (`owner_id`),
    INDEX `idx_kb_id` (`kb_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码项目';

-- =============================================
-- 2. 代码单元索引表
-- =============================================
CREATE TABLE IF NOT EXISTS `code_units` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `project_id` INT NOT NULL,
    `unit_type` VARCHAR(50) NOT NULL COMMENT 'function/class/interface/method/constant',
    `name` VARCHAR(255) NOT NULL COMMENT '单元名称',
    `file_path` VARCHAR(1000) NOT NULL,
    `start_line` INT NOT NULL,
    `end_line` INT NOT NULL,
    `content` TEXT NOT NULL COMMENT '代码内容',
    `signature` VARCHAR(500) COMMENT '函数签名',
    `doc_comment` TEXT COMMENT '文档注释',
    `return_type` VARCHAR(100) COMMENT '返回类型',
    `parameters` JSON COMMENT '参数列表',
    `dependencies` JSON COMMENT '依赖列表',
    `vector_id` VARCHAR(255) COMMENT '向量库ID',
    `is_indexed` BOOLEAN DEFAULT FALSE COMMENT '是否已索引',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_project_type` (`project_id`, `unit_type`),
    INDEX `idx_name` (`name`),
    INDEX `idx_file_path` (`file_path`(255)),
    INDEX `idx_vector_id` (`vector_id`),
    FOREIGN KEY (`project_id`) REFERENCES `code_projects`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码单元索引';

-- =============================================
-- 3. 代码素材片段表
-- =============================================
CREATE TABLE IF NOT EXISTS `code_snippets` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL COMMENT '代码内容',
    `language` VARCHAR(50) COMMENT '语言 python/java/ts等',
    `category` VARCHAR(50) COMMENT '分类: utility/business/sql/frontend/config',
    `tags` JSON COMMENT '标签列表',
    `description` TEXT COMMENT '描述说明',
    `is_favorite` BOOLEAN DEFAULT FALSE,
    `use_count` INT DEFAULT 0 COMMENT '使用次数',
    `vector_id` VARCHAR(255) COMMENT '向量库ID',
    `is_public` BOOLEAN DEFAULT FALSE COMMENT '是否公开',
    `user_id` INT NOT NULL,
    `project_id` INT COMMENT '关联项目',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_category` (`category`),
    INDEX `idx_user_favorite` (`user_id`, `is_favorite`),
    INDEX `idx_user_language` (`user_id`, `language`),
    UNIQUE KEY `uix_user_snippet_title` (`user_id`, `title`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码素材片段';

-- =============================================
-- 4. 片段模板表
-- =============================================
CREATE TABLE IF NOT EXISTS `snippet_templates` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `category` VARCHAR(50) COMMENT '模板分类',
    `content` TEXT NOT NULL,
    `variables` JSON COMMENT '变量定义',
    `description` TEXT,
    `use_count` INT DEFAULT 0,
    `is_global` BOOLEAN DEFAULT FALSE,
    `user_id` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_category` (`category`),
    INDEX `idx_user` (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='片段模板';

-- =============================================
-- 5. 项目成员表
-- =============================================
CREATE TABLE IF NOT EXISTS `project_members` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `project_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `role` VARCHAR(20) DEFAULT 'viewer' COMMENT 'owner/editor/viewer',
    `can_read` BOOLEAN DEFAULT TRUE,
    `can_write` BOOLEAN DEFAULT FALSE,
    `can_delete` BOOLEAN DEFAULT FALSE,
    `can_share` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uix_project_user` (`project_id`, `user_id`),
    INDEX `idx_project_member` (`project_id`, `user_id`),
    FOREIGN KEY (`project_id`) REFERENCES `code_projects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目成员';

-- =============================================
-- 6. 代码分析任务表
-- =============================================
CREATE TABLE IF NOT EXISTS `code_analysis_tasks` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `task_type` VARCHAR(50) NOT NULL COMMENT 'defect/test/refactor/doc/convert',
    `status` VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/completed/failed',
    `input_data` JSON COMMENT '输入数据',
    `output_data` JSON COMMENT '输出结果',
    `code_content` TEXT,
    `language` VARCHAR(50),
    `user_id` INT NOT NULL,
    `project_id` INT COMMENT '关联项目',
    `error_message` TEXT,
    `started_at` TIMESTAMP NULL,
    `completed_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_status` (`user_id`, `status`),
    INDEX `idx_task_type` (`task_type`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码分析任务';

-- =============================================
-- 7. IDE集成表
-- =============================================
CREATE TABLE IF NOT EXISTS `ide_integrations` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `ide_type` VARCHAR(50) COMMENT 'vscode/vim/emacs/jetbrains',
    `api_token` VARCHAR(255) COMMENT 'API令牌',
    `settings` JSON COMMENT 'IDE设置',
    `is_active` BOOLEAN DEFAULT TRUE,
    `last_connected_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_ide` (`user_id`, `ide_type`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='IDE集成';

-- =============================================
-- 8. 代码评审评论表
-- =============================================
CREATE TABLE IF NOT EXISTS `code_review_comments` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `project_id` INT NOT NULL,
    `file_path` VARCHAR(1000),
    `line_number` INT,
    `content` TEXT NOT NULL,
    `severity` VARCHAR(20) COMMENT 'info/warning/error',
    `resolved` BOOLEAN DEFAULT FALSE,
    `parent_id` INT COMMENT '回复父ID',
    `user_id` INT NOT NULL,
    `ai_summary` TEXT COMMENT 'AI评审意见摘要',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_project_file` (`project_id`, `file_path`),
    FOREIGN KEY (`project_id`) REFERENCES `code_projects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码评审评论';

-- =============================================
-- 9. 知识库表（扩展）
-- =============================================
ALTER TABLE `knowledge_bases`
ADD COLUMN IF NOT EXISTS `kb_type` ENUM('document', 'code') DEFAULT 'document' COMMENT '知识库类型',
ADD COLUMN IF NOT EXISTS `project_id` INT COMMENT '关联代码项目',
ADD COLUMN IF NOT EXISTS `is_indexed` BOOLEAN DEFAULT FALSE COMMENT '是否已索引';

-- =============================================
-- 10. 用户表（扩展）
-- =============================================
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `default_model` VARCHAR(100) COMMENT '默认模型',
ADD COLUMN IF NOT EXISTS `offline_mode` BOOLEAN DEFAULT FALSE COMMENT '离线模式';

-- =============================================
-- 11. 插入默认片段模板
-- =============================================
INSERT INTO `snippet_templates` (`name`, `category`, `content`, `variables`, `is_global`) VALUES
('Python工具函数模板', 'utility', '# {{description}}\ndef {{function_name}}({{params}}):\n    """\n    {{docstring}}\n    """\n    {{body}}', '[{"name": "description", "type": "string"}, {"name": "function_name", "type": "string"}, {"name": "params", "type": "string"}, {"name": "docstring", "type": "string"}, {"name": "body", "type": "string"}]', TRUE),
('REST API模板', 'business', '@app.route("{{endpoint}}", methods=["{{method}}"])\ndef {{function_name}}():\n    """\n    {{description}}\n    """\n    {{body}}', '[{"name": "endpoint", "type": "string"}, {"name": "method", "type": "string"}, {"name": "function_name", "type": "string"}, {"name": "description", "type": "string"}, {"name": "body", "type": "string"}]', TRUE),
('React组件模板', 'frontend', 'import React from "react";\n\ninterface Props {\n  {{props}}\n}\n\nexport const {{component_name}}: React.FC<Props> = ({{props}}) => {\n  return (\n    {{jsx}}\n  );\n};', '[{"name": "props", "type": "string"}, {"name": "component_name", "type": "string"}, {"name": "jsx", "type": "string"}]', TRUE);

-- =============================================
-- 12. 创建必要索引
-- =============================================
CREATE INDEX IF NOT EXISTS `idx_snippet_user_id` ON `code_snippets`(`user_id`);
CREATE INDEX IF NOT EXISTS `idx_snippet_language` ON `code_snippets`(`language`);
CREATE INDEX IF NOT EXISTS `idx_code_project_id` ON `code_units`(`project_id`);
CREATE INDEX IF NOT EXISTS `idx_project_owner` ON `code_projects`(`owner_id`);

-- =============================================
-- 完成
-- =============================================
SELECT 'Migration completed successfully!' AS message;

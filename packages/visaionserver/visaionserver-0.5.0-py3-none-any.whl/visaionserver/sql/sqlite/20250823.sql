-- 为用户表添加项目视图模式字段
-- 日期: 2025-08-23
-- 描述: 添加 project_view_mode 字段到 users 表，用于存储前端的项目展示方式
--       1: 卡牌式, 2: 列表式, 默认为 1

-- 重要提示：
-- 如果此脚本因为 "duplicate column name: project_view_mode" 错误而失败，
-- 说明列已经存在，这是正常情况，可以忽略该错误。

-- 清理可能存在的遗留临时表
DROP TABLE IF EXISTS users_backup;

-- 尝试添加列
-- 注意：如果列已存在，以下命令会失败，但这是预期的安全行为
ALTER TABLE users ADD COLUMN project_view_mode INTEGER DEFAULT 1 CHECK (project_view_mode IN (1, 2));

-- 确保所有现有用户都有默认值（如果列刚刚被添加）
UPDATE users SET project_view_mode = 1 WHERE project_view_mode IS NULL;
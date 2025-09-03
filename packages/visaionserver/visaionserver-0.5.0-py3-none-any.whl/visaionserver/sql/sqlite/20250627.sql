-- 修复缺少AUTOINCREMENT属性的表
-- 日期: 2025-06-22

-- 1. 修复 users 表
CREATE TABLE users_backup AS SELECT * FROM users;
DROP TABLE users;
CREATE TABLE "users" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "username" VARCHAR(50) NOT NULL UNIQUE,
  "email" VARCHAR(100) UNIQUE,
  "hashed_password" VARCHAR(255) NOT NULL,
  "is_active" BOOLEAN DEFAULT 1,
  "is_superuser" BOOLEAN DEFAULT 0,
  "role" VARCHAR(20) DEFAULT 'user',
  "project_view_mode" INTEGER DEFAULT 1 CHECK (project_view_mode IN (1, 2)),
  "reset_token" VARCHAR(100),
  "reset_token_expires_at" DATETIME,
  "mfa_enabled" BOOLEAN DEFAULT 0,
  "mfa_secret" VARCHAR(100),
  "created_at" DATETIME,
  "updated_at" DATETIME,
  "last_login" DATETIME
);
CREATE INDEX "ix_users_id" ON "users" ("id" ASC);
CREATE INDEX "ix_users_username" ON "users" ("username" ASC);
CREATE INDEX "ix_users_email" ON "users" ("email" ASC);
-- 尝试恢复数据，如果失败则忽略（让后续创建admin用户）
INSERT INTO users (
    id, username, email, hashed_password, is_active, is_superuser, role,
    reset_token, reset_token_expires_at, mfa_enabled, mfa_secret,
    created_at, updated_at, last_login, project_view_mode
)
SELECT 
    id, username, email, hashed_password, is_active, is_superuser, role,
    reset_token, reset_token_expires_at, mfa_enabled, mfa_secret,
    created_at, updated_at, last_login, 1 as project_view_mode
FROM users_backup;
DROP TABLE users_backup;

-- 2. 修复 projects 表
CREATE TABLE projects_backup AS SELECT * FROM projects;
DROP TABLE projects;
CREATE TABLE "projects" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" VARCHAR(100) NOT NULL,
  "type" INTEGER NOT NULL,
  "image_type" INTEGER,
  "is_del" BOOLEAN DEFAULT 0,
  "user_id" INTEGER NOT NULL,
  "created_at" DATETIME,
  "updated_at" DATETIME
);
CREATE INDEX "ix_projects_id" ON "projects" ("id" ASC);
INSERT INTO projects SELECT * FROM projects_backup;
DROP TABLE projects_backup;

-- 3. 修复 project_users 表
CREATE TABLE project_users_backup AS SELECT * FROM project_users;
DROP TABLE project_users;
CREATE TABLE "project_users" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "permission" INTEGER NOT NULL DEFAULT 3,
  "last_accessed_at" DATETIME
);
CREATE INDEX "ix_project_users_id" ON "project_users" ("id" ASC);
INSERT INTO project_users SELECT * FROM project_users_backup;
DROP TABLE project_users_backup;

-- 4. 修复 datasets 表
CREATE TABLE datasets_backup AS SELECT * FROM datasets;
DROP TABLE datasets;
CREATE TABLE "datasets" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" VARCHAR(100) NOT NULL,
  "project_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "status" VARCHAR(20) DEFAULT 'CREATING',
  "package_path" VARCHAR(255),
  "last_package_time" DATETIME,
  "is_del" BOOLEAN DEFAULT 0,
  "created_at" DATETIME,
  "updated_at" DATETIME
);
CREATE INDEX "ix_datasets_id" ON "datasets" ("id" ASC);
INSERT INTO datasets SELECT * FROM datasets_backup;
DROP TABLE datasets_backup;

-- 5. 修复 samples 表
CREATE TABLE samples_backup AS SELECT * FROM samples;
DROP TABLE samples;
CREATE TABLE "samples" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "name" VARCHAR(255) NOT NULL,
  "path" VARCHAR(500) NOT NULL,
  "status" INTEGER DEFAULT 1,
  "md5" VARCHAR(32) NOT NULL,
  "size" INTEGER NOT NULL,
  "width" INTEGER NOT NULL,
  "height" INTEGER NOT NULL,
  "thumbnail_path" VARCHAR(500),
  "annotation_path" VARCHAR(500),
  "annotation_original_name" VARCHAR(255),
  "is_del" BOOLEAN DEFAULT 0,
  "created_at" DATETIME,
  "updated_at" DATETIME,
  CHECK (status IN (1, 2, 3))
);
CREATE INDEX "ix_samples_id" ON "samples" ("id" ASC);
INSERT INTO samples SELECT * FROM samples_backup;
DROP TABLE samples_backup;

-- 6. 修复 labels 表
CREATE TABLE labels_backup AS SELECT * FROM labels;
DROP TABLE labels;
CREATE TABLE "labels" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" VARCHAR(100) NOT NULL,
  "color" JSON NOT NULL DEFAULT '[]',
  "project_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "is_del" BOOLEAN DEFAULT 0,
  "created_at" DATETIME,
  "updated_at" DATETIME
);
CREATE INDEX "ix_labels_id" ON "labels" ("id" ASC);
INSERT INTO labels SELECT * FROM labels_backup;
DROP TABLE labels_backup;

-- 7. 修复 sample_labels 表
CREATE TABLE sample_labels_backup AS SELECT * FROM sample_labels;
DROP TABLE sample_labels;
CREATE TABLE "sample_labels" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "sample_id" INTEGER NOT NULL,
  "label_id" INTEGER NOT NULL,
  "created_at" DATETIME,
  "updated_at" DATETIME
);
CREATE INDEX "ix_sample_labels_id" ON "sample_labels" ("id" ASC);
INSERT INTO sample_labels SELECT * FROM sample_labels_backup;
DROP TABLE sample_labels_backup;

-- 8. 修复 annotation_logs 表
CREATE TABLE annotation_logs_backup AS SELECT * FROM annotation_logs;
DROP TABLE annotation_logs;
CREATE TABLE "annotation_logs" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "sample_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "action" VARCHAR(50) NOT NULL,
  "content" TEXT NOT NULL,
  "created_at" DATETIME,
  FOREIGN KEY ("sample_id") REFERENCES "samples" ("id"),
  FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);
CREATE INDEX "ix_annotation_logs_id" ON "annotation_logs" ("id" ASC);
INSERT INTO annotation_logs SELECT * FROM annotation_logs_backup;
DROP TABLE annotation_logs_backup;

-- 9. 修复 dataset_samples 表
CREATE TABLE dataset_samples_backup AS SELECT * FROM dataset_samples;
DROP TABLE dataset_samples;
CREATE TABLE "dataset_samples" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "dataset_id" INTEGER NOT NULL,
  "sample_id" INTEGER NOT NULL,
  "created_at" DATETIME,
  "updated_at" DATETIME
);
CREATE INDEX "ix_dataset_samples_id" ON "dataset_samples" ("id" ASC);
INSERT INTO dataset_samples SELECT * FROM dataset_samples_backup;
DROP TABLE dataset_samples_backup;

-- 10. 修复 onnx_exports 表
CREATE TABLE onnx_exports_backup AS SELECT * FROM onnx_exports;
DROP TABLE onnx_exports;
CREATE TABLE "onnx_exports" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL,
  "model_id" INTEGER NOT NULL,
  "param" JSON,
  "status" VARCHAR(20) DEFAULT 'PENDING',
  "creator_id" INTEGER NOT NULL,
  "download_url" VARCHAR(500),
  "job_id" INTEGER,
  "create_time" DATETIME,
  "update_time" DATETIME,
  FOREIGN KEY ("model_id") REFERENCES "models" ("id"),
  FOREIGN KEY ("creator_id") REFERENCES "users" ("id")
);
CREATE INDEX "ix_onnx_exports_id" ON "onnx_exports" ("id" ASC);
INSERT INTO onnx_exports SELECT * FROM onnx_exports_backup;
DROP TABLE onnx_exports_backup; 
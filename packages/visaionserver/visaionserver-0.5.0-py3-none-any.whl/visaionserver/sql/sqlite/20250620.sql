-- 步骤1：创建临时表备份原数据
CREATE TABLE models_backup AS SELECT * FROM models;

-- 步骤2：删除原表
DROP TABLE models;

-- 步骤3：重建带自增主键的新表
CREATE TABLE "models" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" VARCHAR(100) NOT NULL,
  "project_id" INTEGER,
  "param" JSON,
  "user_id" INTEGER,
  "training_sets" JSON,
  "validation_sets" JSON,
  "mapping_label_json" JSON,
  "status" SMALLINT,
  "create_time" DATETIME,
  "update_time" DATETIME,
  "pid" INTEGER,
  "log_url" VARCHAR(500),
  "predict_url" VARCHAR(500),
  "metrics_log_url" VARCHAR(500),
  "metrics_json" JSON,
  "model_file_url_json" JSON,
  "start_time" DATETIME,
  "finish_time" DATETIME,
  "is_del" SMALLINT,
  "template" VARCHAR(200) NOT NULL,
  FOREIGN KEY ("project_id") REFERENCES "projects" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX "ix_models_id"
ON "models" (
  "id" ASC
);

-- 步骤4：恢复数据（id 会重新自增分配）
INSERT INTO models  SELECT * FROM models_backup;

-- 步骤5：删除临时表
DROP TABLE models_backup;

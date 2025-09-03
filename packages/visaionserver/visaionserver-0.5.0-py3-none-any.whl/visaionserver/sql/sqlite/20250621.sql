
    -- 步骤1：创建临时表备份原数据
  CREATE TABLE evaluate_backup AS SELECT * FROM evaluate;

    -- 步骤2：删除原表
    DROP TABLE evaluate;
    
    -- 步骤3：重建带自增主键的新表
    CREATE TABLE "evaluate" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "model_id" INTEGER,
  "pth" VARCHAR(100) NOT NULL,
  "status" SMALLINT,
  "user_id" INTEGER,
  "create_time" DATETIME,
  "params" JSON NOT NULL,
  "metrics_json" JSON,
  "log_url" VARCHAR(200),
  "predict_url" VARCHAR(200),
  "metrics_log_url" VARCHAR(200),
  FOREIGN KEY ("model_id") REFERENCES "models" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX "ix_evaluate_id"
ON "evaluate" (
  "id" ASC
);
    
    -- 步骤4：恢复数据（id 会重新自增分配）
    INSERT INTO evaluate  SELECT * FROM evaluate_backup;
-- 步骤5：删除临时表
DROP TABLE evaluate_backup;
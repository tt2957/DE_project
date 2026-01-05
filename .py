import duckdb

DB_PATH = "db/steam.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

# 테이블 목록 확인
tables = con.execute("SHOW TABLES").fetchall()
print("Tables:", tables)

# 특정 테이블 구조 확인
schema = con.execute("DESCRIBE raw_concurrency").fetchall()
print("Schema:", schema)

# 샘플 데이터 확인
sample = con.execute("SELECT * FROM raw_concurrency LIMIT 5").fetchdf()
print(sample)

con.close()
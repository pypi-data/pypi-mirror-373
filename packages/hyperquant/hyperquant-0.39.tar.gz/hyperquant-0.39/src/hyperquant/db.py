from dataclasses import dataclass
import duckdb
import pandas as pd
from typing import Dict, Optional, Union
import os


# 实现retry装饰器
def restry(max_retries=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise e
        return wrapper
    return decorator

@dataclass
class DuckDBType():
    INTEGER = 'INTEGER'
    DOUBLE = 'DOUBLE'
    DECIMAL = 'DECIMAL'
    DECIMAL_10_2 = 'DECIMAL(10,2)'
    DECIMAL_10_4 = 'DECIMAL(10,4)'
    DECIMAL_10_6 = 'DECIMAL(10,6)'
    TIMESTAMP = 'TIMESTAMP'
    BOOLEAN = 'BOOLEAN'
    VARCHAR = 'VARCHAR'
    # 根据需要添加更多类型

@restry()
def save_to_duck(
    path: str,
    df: pd.DataFrame,
    tbl_name: str,
    dtype_overrides: Optional[Dict[str, str]] = None,
    update_for: Optional[Union[str, list]] = None,
    con: Optional[duckdb.DuckDBPyConnection] = None
):
    after_close = False
    if con is None:
        if os.path.dirname(path) != '':
            os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            duckdb.connect(path).close()  # 仅创建空库
        con = duckdb.connect(path)
        after_close = True

    # 如果提供了 update_for, 确保它是一个列表
    if update_for:
        update_for = [update_for] if isinstance(update_for, str) else update_for
        missing = [col for col in update_for if col not in df.columns]
        if missing:
            raise ValueError(f"Missing update_for columns: {missing}")

    # 类型推断
    def infer_type(series):
        if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
            return 'DOUBLE'
        elif pd.api.types.is_bool_dtype(series):
            return 'BOOLEAN'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'TIMESTAMP'
        else:
            return 'VARCHAR'

    dtype_mapping = {col: infer_type(df[col]) for col in df.columns}
    if dtype_overrides:
        dtype_mapping.update({k: v.upper() for k, v in dtype_overrides.items()})

    try:
        # 检查表是否存在
        table_exists = con.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'main' AND table_name = ?;
        """, (tbl_name.lower(),)).fetchone()[0] > 0

        # 创建表或添加列
        if not table_exists:
            cols = [f'"{col}" {dtype}' for col, dtype in dtype_mapping.items()]
            con.execute(f'CREATE TABLE "{tbl_name}" ({", ".join(cols)});')
        else:
            # 查询现有列
            existing_columns = con.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'main' AND table_name = ?;
            """, (tbl_name.lower(),)).fetchall()
            existing_columns = {row[0].lower(): row[1].upper() for row in existing_columns}

            # 合并添加列
            new_columns = {col: dtype for col, dtype in dtype_mapping.items() 
                          if col.lower() not in existing_columns}
            if new_columns:
                add_clauses = [f'ADD COLUMN "{col}" {dtype}' 
                              for col, dtype in new_columns.items()]
                con.execute(f'ALTER TABLE "{tbl_name}" {", ".join(add_clauses)};')

        # 注册临时表
        con.register('df_temp', df)

        # 如果 update_for 存在，进行更新操作
        if update_for:
            join_cond = " AND ".join([f'target."{col}" = src."{col}"' 
                                     for col in update_for])
            update_cols = [col for col in df.columns if col not in update_for]
            if not update_cols:
                raise ValueError("No columns to update with given update_for.")
            
            # 更新 SQL
            set_clause = ", ".join([f'"{col}" = src."{col}"' 
                                   for col in update_cols])
            con.execute(f"""
                UPDATE "{tbl_name}" AS target
                SET {set_clause}
                FROM df_temp AS src
                WHERE {join_cond};
            """)

            # 插入不存在的记录
            insert_cols = ", ".join([f'"{col}"' for col in df.columns])
            insert_vals = ", ".join([f'src."{col}"' for col in df.columns])

            con.execute(f"""
                INSERT INTO "{tbl_name}" ({insert_cols})
                SELECT {insert_vals}
                FROM df_temp AS src
                LEFT JOIN "{tbl_name}" AS target
                ON {join_cond}
                WHERE target."{update_for[0]}" IS NULL;
            """)
        else:
            # 没有 update_for 时直接插入数据
            cols = ", ".join([f'"{col}"' for col in df.columns])
            con.execute(f'INSERT INTO "{tbl_name}" ({cols}) SELECT {cols} FROM df_temp;')

        if after_close:
            con.close()
    except Exception as e:
        if after_close:
            con.rollback()
            con.close()
        raise RuntimeError(f"Failed to save data: {e}") from e

clear_table_duck = lambda path, tbl_name: duckdb.connect(path).execute(f"TRUNCATE TABLE {tbl_name};")

# 使用示例
if __name__ == "__main__":
    # 初始数据
    data_initial = {
        'symbol': ['BTCUSDT'],
        'exchange': ['binance'],
        'orderid': ['123'],
        'win': [301110],
        'time': [pd.to_datetime('2025-01-05 05:10:00')]
    }
    
    df_initial = pd.DataFrame(data_initial)
    
    # 更新数据
    data_update = {
        'symbol': ['BTCUSDT'],
        'exchange': ['eee'],
        'orderid': ['123'],
        'win': [1010],
        'time': [pd.to_datetime('2025-01-05 04:20:00', utc=True)]
    }
    
    df_update = pd.DataFrame(data_update)
    
    # 自定义数据类型覆盖
    dtype_overrides = {
        'orderid': DuckDBType.VARCHAR,  # 根据您的数据类型调整
        'win': DuckDBType.INTEGER
    }
    
    # 保存初始数据到 DuckDB
    # save_to_duck('./333.db', df_initial, 'trades', dtype_overrides=dtype_overrides, update_for='orderid')
    
    # # 覆盖 orderid 为 '123' 的数据
    save_to_duck('./333.db', df_update, 'trades', dtype_overrides=dtype_overrides, update_for=['orderid', 'time'])
    
    # 验证结果
    with duckdb.connect('./333.db') as con:
        df = con.execute("SELECT * FROM trades;").fetchdf()
        print(df)
from antlr4 import InputStream, CommonTokenStream

from const import OP_EQ, OP_LT, OP_LE, OP_GT, OP_GE
from database import Database
from executor import Executor, new_values_executor, new_seq_scan_executor, new_index_scan_executor, \
    new_filter_executor, new_projection_executor, new_insert_executor, new_update_executor, new_delete_executor
from row import Row, new_row
from sql.SqlLexer import SqlLexer
from sql.SqlParser import SqlParser
from sql.sql_visitor import StmtVisitor, Condition, CreateTableStmt, CreateIndexStmt, InsertStmt, \
    SelectStmt, UpdateStmt, DeleteStmt
from table import Table
from value.const import VALUE_TYPE_INT, VALUE_TYPE_STRING, VALUE_TYPE_BOOL
from value.value import Value
from value.value_bool import new_value_bool
from value.value_int import new_value_int
from value.value_string import new_value_string

OP_STR_TO_CONST = {
    '=': OP_EQ,
    '<': OP_LT,
    '<=': OP_LE,
    '>': OP_GT,
    '>=': OP_GE,
}

TYPE_NAME_TO_CONST = {
    'INT': VALUE_TYPE_INT,
    'STRING': VALUE_TYPE_STRING,
    'BOOL': VALUE_TYPE_BOOL,
}


def parse_sql(sql_text: str):
    lexer = SqlLexer(InputStream(sql_text))
    parser = SqlParser(CommonTokenStream(lexer))
    tree = parser.program()
    stmt = StmtVisitor().visit(tree)
    return stmt


def execute_sql(db: Database, sql_text: str):
    """
    执行一条 SQL。SELECT 返回 list[Row]；INSERT/UPDATE/DELETE 返回受影响行数；
    CREATE 返回 None。
    """
    stmt = parse_sql(sql_text)
    if isinstance(stmt, CreateTableStmt):
        col_types = [TYPE_NAME_TO_CONST[type_name] for type_name in stmt.col_types]
        db.create_table(stmt.table_name, stmt.col_names, col_types)
        return None
    if isinstance(stmt, CreateIndexStmt):
        db.create_index(stmt.table_name, stmt.col_names)
        return None

    table = db.get_table(stmt.table_name)
    if isinstance(stmt, InsertStmt):
        row = new_row_from_literals(table, stmt.literals)
        executor = new_insert_executor(table, new_values_executor([row]))
        return sum(1 for _ in executor)
    if isinstance(stmt, SelectStmt):
        executor = build_scan(table, stmt.conditions)
        if stmt.col_names is not None:
            col_indexes = [col_index_of(table, col_name) for col_name in stmt.col_names]
            executor = new_projection_executor(executor, col_indexes)
        return [row for _, row in executor]
    if isinstance(stmt, UpdateStmt):
        child = build_scan(table, stmt.conditions)
        assignments = [(col_index_of(table, col_name), new_value_of_type(table, col_name, literal))
                       for col_name, literal in stmt.assignments]
        executor = new_update_executor(table, child, assignments)
        return sum(1 for _ in executor)
    if isinstance(stmt, DeleteStmt):
        child = build_scan(table, stmt.conditions)
        executor = new_delete_executor(table, child)
        return sum(1 for _ in executor)
    raise ValueError(f"不支持的语句 {type(stmt)}")


def build_scan(table: Table, conditions: list[Condition]) -> Executor:
    """
    WHERE 条件（AND 连接）→ 扫描执行器。
    优化规则（对齐 BusTub 的 seqscan_as_indexscan）：若某索引的全部列都有等值条件，
    用 IndexScan 替代 SeqScan + 对应 Filter，其余条件保持 Filter。
    """
    remaining = list(conditions)
    executor = None
    for col_indexes, _ in table.indexes.items():
        eq_conditions = [condition_for_col(remaining, table.col_names[col_index], '=')
                         for col_index in col_indexes]
        if all(condition is not None for condition in eq_conditions):
            key_row = new_row([new_value_of_type(table, table.col_names[col_index], condition.literal)
                               for col_index, condition in zip(col_indexes, eq_conditions)])
            executor = new_index_scan_executor(table, col_indexes, key_row)
            for condition in eq_conditions:
                remaining.remove(condition)
            break
    if executor is None:
        executor = new_seq_scan_executor(table)
    for condition in remaining:
        executor = new_filter_executor(
            executor,
            col_index_of(table, condition.col_name),
            OP_STR_TO_CONST[condition.op],
            new_value_of_type(table, condition.col_name, condition.literal),
        )
    return executor


def condition_for_col(conditions: list[Condition], col_name: str, op: str) -> Condition | None:
    for condition in conditions:
        if condition.col_name == col_name and condition.op == op:
            return condition
    return None


def col_index_of(table: Table, col_name: str) -> int:
    try:
        return table.col_names.index(col_name)
    except ValueError:
        raise ValueError(f"列 {col_name} 不存在")


def new_value_of_type(table: Table, col_name: str, literal: int | str | bool) -> Value:
    col_index = col_index_of(table, col_name)
    return new_value(literal, table.col_types[col_index])


def new_row_from_literals(table: Table, literals: list[int | str | bool]) -> Row:
    if len(literals) != len(table.col_types):
        raise ValueError(f"INSERT 需要 {len(table.col_types)} 个值，实际 {len(literals)} 个")
    vals = [new_value(literal, col_type) for literal, col_type in zip(literals, table.col_types)]
    return new_row(vals)


def new_value(literal: int | str | bool, col_type: int) -> Value:
    if col_type == VALUE_TYPE_INT:
        if type(literal) is not int:
            raise ValueError(f"类型不匹配：期望 INT，实际 {literal!r}")
        return new_value_int(literal)
    if col_type == VALUE_TYPE_STRING:
        if type(literal) is not str:
            raise ValueError(f"类型不匹配：期望 STRING，实际 {literal!r}")
        return new_value_string(literal)
    if col_type == VALUE_TYPE_BOOL:
        if type(literal) is not bool:
            raise ValueError(f"类型不匹配：期望 BOOL，实际 {literal!r}")
        return new_value_bool(literal)
    raise ValueError(f"未知列类型 {col_type}")

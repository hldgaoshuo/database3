from antlr4 import InputStream, CommonTokenStream

from const import OP_EQ, OP_LT, OP_LE, OP_GT, OP_GE, AGG_COUNT, AGG_SUM, AGG_MIN, AGG_MAX
from database import Database
from executor import Executor, new_values_executor, new_seq_scan_executor, new_index_scan_executor, \
    new_filter_executor, new_projection_executor, new_insert_executor, new_update_executor, new_delete_executor, \
    new_aggregation_executor, new_value
from row import Row, new_row
from sql.SqlLexer import SqlLexer
from sql.SqlParser import SqlParser
from sql.sql_visitor import StmtVisitor, Condition, AggCall, CreateTableStmt, CreateIndexStmt, InsertStmt, \
    SelectStmt, UpdateStmt, DeleteStmt
from table import Table
from value.const import VALUE_TYPE_INT, VALUE_TYPE_STRING, VALUE_TYPE_BOOL
from value.value import Value

OP_STR_TO_CONST = {
    '=': OP_EQ,
    '<': OP_LT,
    '<=': OP_LE,
    '>': OP_GT,
    '>=': OP_GE,
}

AGG_FUNC_STR_TO_CONST = {
    'COUNT': AGG_COUNT,
    'SUM': AGG_SUM,
    'MIN': AGG_MIN,
    'MAX': AGG_MAX,
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
        if has_aggregation(stmt):
            executor = build_aggregation(table, executor, stmt)
        elif stmt.items is not None:
            col_indexes = [col_index_of(table, col_name) for col_name in stmt.items]
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


def has_aggregation(stmt: SelectStmt) -> bool:
    if stmt.group_by or stmt.having is not None:
        return True
    return any(isinstance(item, AggCall) for item in stmt.items or [])


def build_aggregation(table: Table, child: Executor, stmt: SelectStmt) -> Executor:
    """聚合查询：分组列必须在 GROUP BY 中；HAVING 映射为聚合输出上的 Filter。"""
    if stmt.items is None:
        raise ValueError("聚合查询不支持 SELECT *")
    for item in stmt.items:
        if isinstance(item, str) and item not in stmt.group_by:
            raise ValueError(f"列 {item} 必须出现在 GROUP BY 中")

    group_col_indexes = [col_index_of(table, col_name) for col_name in stmt.group_by]
    items = []
    out_col_types = []
    for item in stmt.items:
        if isinstance(item, str):
            items.append(('col', stmt.group_by.index(item)))
            out_col_types.append(table.col_types[col_index_of(table, item)])
        else:
            items.append(agg_item_of(table, item))
            out_col_types.append(agg_out_type_of(table, item))
    executor = new_aggregation_executor(child, group_col_indexes, items, out_col_types)

    if stmt.having is not None:
        col_index = having_col_index_of(stmt)
        executor = new_filter_executor(executor, col_index, OP_STR_TO_CONST[stmt.having.op],
                                       new_value(stmt.having.literal, out_col_types[col_index]))
    return executor


def agg_item_of(table: Table, call: AggCall) -> tuple:
    func_const = AGG_FUNC_STR_TO_CONST[call.func]
    if call.col_name is None:
        if call.func != 'COUNT':
            raise ValueError(f"{call.func} 需要列参数")
        return func_const, None
    return func_const, col_index_of(table, call.col_name)


def agg_out_type_of(table: Table, call: AggCall) -> int:
    if call.func == 'COUNT':
        return VALUE_TYPE_INT
    col_type = table.col_types[col_index_of(table, call.col_name)]
    if call.func == 'SUM':
        if col_type != VALUE_TYPE_INT:
            raise ValueError("SUM 仅支持 INT 列")
        return VALUE_TYPE_INT
    return col_type


def having_col_index_of(stmt: SelectStmt) -> int:
    having = stmt.having
    if having.agg is not None:
        for i, item in enumerate(stmt.items):
            if isinstance(item, AggCall) and item.func == having.agg.func \
                    and item.col_name == having.agg.col_name:
                return i
        raise ValueError("HAVING 引用的聚合必须出现在 SELECT 中")
    for i, item in enumerate(stmt.items):
        if item == having.col_name:
            return i
    raise ValueError(f"HAVING 引用的列 {having.col_name} 必须出现在 SELECT 中")


def build_scan(table: Table, conditions: list[Condition]) -> Executor:
    """
    WHERE 条件（AND 连接）→ 扫描执行器。
    优化规则（对齐 BusTub 的 seqscan_as_indexscan）：若某索引的全部列都有等值条件，
    用 IndexScan 替代 SeqScan + 对应 Filter，其余条件保持 Filter。
    """
    remaining = list(conditions)
    for condition in remaining:
        if condition.agg is not None:
            raise ValueError("WHERE 不支持聚合函数，聚合过滤请用 HAVING")
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

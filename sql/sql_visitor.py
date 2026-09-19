from sql.SqlParser import SqlParser
from sql.SqlVisitor import SqlVisitor


class Condition:
    """WHERE 条件：列名、比较运算符（'= < <= > >=' 原文）、字面量（Python 原生值）"""

    def __init__(self):
        self.col_name: str = ""
        self.op: str = ""
        self.literal: int | str | bool = 0


class CreateTableStmt:

    def __init__(self):
        self.table_name: str = ""
        self.col_names: list[str] = []
        self.col_types: list[str] = []  # 'INT' | 'STRING' | 'BOOL'


class CreateIndexStmt:

    def __init__(self):
        self.table_name: str = ""
        self.col_names: list[str] = []


class InsertStmt:

    def __init__(self):
        self.table_name: str = ""
        self.literals: list[int | str | bool] = []


class SelectStmt:

    def __init__(self):
        self.table_name: str = ""
        self.col_names: list[str] | None = None  # None 表示 *
        self.conditions: list[Condition] = []


class UpdateStmt:

    def __init__(self):
        self.table_name: str = ""
        self.assignments: list[tuple[str, int | str | bool]] = []
        self.conditions: list[Condition] = []


class DeleteStmt:

    def __init__(self):
        self.table_name: str = ""
        self.conditions: list[Condition] = []


def literal_from_ctx(ctx: SqlParser.LiteralContext) -> int | str | bool:
    if ctx.INTEGER_LITERAL() is not None:
        return int(ctx.INTEGER_LITERAL().getText())
    if ctx.STRING_LITERAL() is not None:
        text = ctx.STRING_LITERAL().getText()
        return text[1:-1].replace("\\'", "'").replace("\\\\", "\\")
    if ctx.TRUE() is not None:
        return True
    return False


def condition_from_ctx(ctx: SqlParser.ConditionContext) -> Condition:
    condition = Condition()
    condition.col_name = ctx.colName.text
    condition.op = ctx.op.getText()
    condition.literal = literal_from_ctx(ctx.literal())
    return condition


def conditions_from_ctx(ctx) -> list[Condition]:
    if ctx is None:
        return []
    return [condition_from_ctx(c) for c in ctx.condition()]


class StmtVisitor(SqlVisitor):
    """parse tree → 语句对象，不接触数据库"""

    def visitProgram(self, ctx: SqlParser.ProgramContext):
        # program 的默认 visitChildren 会把语句结果被末尾的 EOF 覆盖成 None，直接取 statement
        return self.visit(ctx.statement())

    def visitCreateTable(self, ctx: SqlParser.CreateTableContext) -> CreateTableStmt:
        stmt = CreateTableStmt()
        stmt.table_name = ctx.tableName.text
        for column_def in ctx.columnDef():
            stmt.col_names.append(column_def.colName.text)
            stmt.col_types.append(column_def.colType.getText().upper())
        return stmt

    def visitCreateIndex(self, ctx: SqlParser.CreateIndexContext) -> CreateIndexStmt:
        stmt = CreateIndexStmt()
        stmt.table_name = ctx.tableName.text
        stmt.col_names = [identifier.getText() for identifier in ctx.colList().IDENTIFIER()]
        return stmt

    def visitInsert(self, ctx: SqlParser.InsertContext) -> InsertStmt:
        stmt = InsertStmt()
        stmt.table_name = ctx.tableName.text
        stmt.literals = [literal_from_ctx(literal) for literal in ctx.literalList().literal()]
        return stmt

    def visitSelect(self, ctx: SqlParser.SelectContext) -> SelectStmt:
        stmt = SelectStmt()
        stmt.table_name = ctx.tableName.text
        if ctx.ASTERISK() is None:
            stmt.col_names = [identifier.getText() for identifier in ctx.colList().IDENTIFIER()]
        stmt.conditions = conditions_from_ctx(ctx.whereClause())
        return stmt

    def visitUpdate(self, ctx: SqlParser.UpdateContext) -> UpdateStmt:
        stmt = UpdateStmt()
        stmt.table_name = ctx.tableName.text
        stmt.assignments = [(assignment.colName.text, literal_from_ctx(assignment.literal()))
                            for assignment in ctx.assignment()]
        stmt.conditions = conditions_from_ctx(ctx.whereClause())
        return stmt

    def visitDelete(self, ctx: SqlParser.DeleteContext) -> DeleteStmt:
        stmt = DeleteStmt()
        stmt.table_name = ctx.tableName.text
        stmt.conditions = conditions_from_ctx(ctx.whereClause())
        return stmt

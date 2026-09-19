# Generated from Sql.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SqlParser import SqlParser
else:
    from SqlParser import SqlParser

# This class defines a complete generic visitor for a parse tree produced by SqlParser.

class SqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SqlParser#program.
    def visitProgram(self, ctx:SqlParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#statement.
    def visitStatement(self, ctx:SqlParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#createTable.
    def visitCreateTable(self, ctx:SqlParser.CreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#columnDef.
    def visitColumnDef(self, ctx:SqlParser.ColumnDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#typeName.
    def visitTypeName(self, ctx:SqlParser.TypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#createIndex.
    def visitCreateIndex(self, ctx:SqlParser.CreateIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#insert.
    def visitInsert(self, ctx:SqlParser.InsertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#select.
    def visitSelect(self, ctx:SqlParser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#selectList.
    def visitSelectList(self, ctx:SqlParser.SelectListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#selectItem.
    def visitSelectItem(self, ctx:SqlParser.SelectItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#aggFunc.
    def visitAggFunc(self, ctx:SqlParser.AggFuncContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#funcName.
    def visitFuncName(self, ctx:SqlParser.FuncNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#groupByClause.
    def visitGroupByClause(self, ctx:SqlParser.GroupByClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#havingClause.
    def visitHavingClause(self, ctx:SqlParser.HavingClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#update.
    def visitUpdate(self, ctx:SqlParser.UpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#assignment.
    def visitAssignment(self, ctx:SqlParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#delete.
    def visitDelete(self, ctx:SqlParser.DeleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#whereClause.
    def visitWhereClause(self, ctx:SqlParser.WhereClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#condition.
    def visitCondition(self, ctx:SqlParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#compareOp.
    def visitCompareOp(self, ctx:SqlParser.CompareOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#colList.
    def visitColList(self, ctx:SqlParser.ColListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#literalList.
    def visitLiteralList(self, ctx:SqlParser.LiteralListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SqlParser#literal.
    def visitLiteral(self, ctx:SqlParser.LiteralContext):
        return self.visitChildren(ctx)



del SqlParser
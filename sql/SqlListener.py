# Generated from Sql.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SqlParser import SqlParser
else:
    from SqlParser import SqlParser

# This class defines a complete listener for a parse tree produced by SqlParser.
class SqlListener(ParseTreeListener):

    # Enter a parse tree produced by SqlParser#program.
    def enterProgram(self, ctx:SqlParser.ProgramContext):
        pass

    # Exit a parse tree produced by SqlParser#program.
    def exitProgram(self, ctx:SqlParser.ProgramContext):
        pass


    # Enter a parse tree produced by SqlParser#statement.
    def enterStatement(self, ctx:SqlParser.StatementContext):
        pass

    # Exit a parse tree produced by SqlParser#statement.
    def exitStatement(self, ctx:SqlParser.StatementContext):
        pass


    # Enter a parse tree produced by SqlParser#createTable.
    def enterCreateTable(self, ctx:SqlParser.CreateTableContext):
        pass

    # Exit a parse tree produced by SqlParser#createTable.
    def exitCreateTable(self, ctx:SqlParser.CreateTableContext):
        pass


    # Enter a parse tree produced by SqlParser#columnDef.
    def enterColumnDef(self, ctx:SqlParser.ColumnDefContext):
        pass

    # Exit a parse tree produced by SqlParser#columnDef.
    def exitColumnDef(self, ctx:SqlParser.ColumnDefContext):
        pass


    # Enter a parse tree produced by SqlParser#typeName.
    def enterTypeName(self, ctx:SqlParser.TypeNameContext):
        pass

    # Exit a parse tree produced by SqlParser#typeName.
    def exitTypeName(self, ctx:SqlParser.TypeNameContext):
        pass


    # Enter a parse tree produced by SqlParser#createIndex.
    def enterCreateIndex(self, ctx:SqlParser.CreateIndexContext):
        pass

    # Exit a parse tree produced by SqlParser#createIndex.
    def exitCreateIndex(self, ctx:SqlParser.CreateIndexContext):
        pass


    # Enter a parse tree produced by SqlParser#insert.
    def enterInsert(self, ctx:SqlParser.InsertContext):
        pass

    # Exit a parse tree produced by SqlParser#insert.
    def exitInsert(self, ctx:SqlParser.InsertContext):
        pass


    # Enter a parse tree produced by SqlParser#select.
    def enterSelect(self, ctx:SqlParser.SelectContext):
        pass

    # Exit a parse tree produced by SqlParser#select.
    def exitSelect(self, ctx:SqlParser.SelectContext):
        pass


    # Enter a parse tree produced by SqlParser#update.
    def enterUpdate(self, ctx:SqlParser.UpdateContext):
        pass

    # Exit a parse tree produced by SqlParser#update.
    def exitUpdate(self, ctx:SqlParser.UpdateContext):
        pass


    # Enter a parse tree produced by SqlParser#assignment.
    def enterAssignment(self, ctx:SqlParser.AssignmentContext):
        pass

    # Exit a parse tree produced by SqlParser#assignment.
    def exitAssignment(self, ctx:SqlParser.AssignmentContext):
        pass


    # Enter a parse tree produced by SqlParser#delete.
    def enterDelete(self, ctx:SqlParser.DeleteContext):
        pass

    # Exit a parse tree produced by SqlParser#delete.
    def exitDelete(self, ctx:SqlParser.DeleteContext):
        pass


    # Enter a parse tree produced by SqlParser#whereClause.
    def enterWhereClause(self, ctx:SqlParser.WhereClauseContext):
        pass

    # Exit a parse tree produced by SqlParser#whereClause.
    def exitWhereClause(self, ctx:SqlParser.WhereClauseContext):
        pass


    # Enter a parse tree produced by SqlParser#condition.
    def enterCondition(self, ctx:SqlParser.ConditionContext):
        pass

    # Exit a parse tree produced by SqlParser#condition.
    def exitCondition(self, ctx:SqlParser.ConditionContext):
        pass


    # Enter a parse tree produced by SqlParser#compareOp.
    def enterCompareOp(self, ctx:SqlParser.CompareOpContext):
        pass

    # Exit a parse tree produced by SqlParser#compareOp.
    def exitCompareOp(self, ctx:SqlParser.CompareOpContext):
        pass


    # Enter a parse tree produced by SqlParser#colList.
    def enterColList(self, ctx:SqlParser.ColListContext):
        pass

    # Exit a parse tree produced by SqlParser#colList.
    def exitColList(self, ctx:SqlParser.ColListContext):
        pass


    # Enter a parse tree produced by SqlParser#literalList.
    def enterLiteralList(self, ctx:SqlParser.LiteralListContext):
        pass

    # Exit a parse tree produced by SqlParser#literalList.
    def exitLiteralList(self, ctx:SqlParser.LiteralListContext):
        pass


    # Enter a parse tree produced by SqlParser#literal.
    def enterLiteral(self, ctx:SqlParser.LiteralContext):
        pass

    # Exit a parse tree produced by SqlParser#literal.
    def exitLiteral(self, ctx:SqlParser.LiteralContext):
        pass



del SqlParser
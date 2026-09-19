grammar Sql;

// ---------- parser ----------

program
    : statement EOF
    ;

statement
    : createTable
    | createIndex
    | insert
    | select
    | update
    | delete
    ;

createTable
    : CREATE TABLE tableName=IDENTIFIER '(' columnDef (',' columnDef)* ')'
    ;

columnDef
    : colName=IDENTIFIER colType=typeName
    ;

typeName
    : INT
    | STRING
    | BOOL
    ;

createIndex
    : CREATE INDEX indexName=IDENTIFIER ON tableName=IDENTIFIER '(' colList ')'
    ;

insert
    : INSERT INTO tableName=IDENTIFIER VALUES '(' literalList ')'
    ;

select
    : SELECT selectList FROM tableName=IDENTIFIER whereClause? groupByClause? havingClause?
    ;

selectList
    : ASTERISK
    | selectItem (',' selectItem)*
    ;

selectItem
    : IDENTIFIER
    | aggFunc
    ;

aggFunc
    : funcName '(' (ASTERISK | IDENTIFIER) ')'
    ;

funcName
    : COUNT
    | SUM
    | MIN
    | MAX
    ;

groupByClause
    : GROUP BY colList
    ;

havingClause
    : HAVING condition
    ;

update
    : UPDATE tableName=IDENTIFIER SET assignment (',' assignment)* whereClause?
    ;

assignment
    : colName=IDENTIFIER '=' literal
    ;

delete
    : DELETE FROM tableName=IDENTIFIER whereClause?
    ;

whereClause
    : WHERE condition (AND condition)*
    ;

condition
    : (colName=IDENTIFIER | agg=aggFunc) op=compareOp literal
    ;

compareOp
    : '='
    | '<'
    | '<='
    | '>'
    | '>='
    ;

colList
    : IDENTIFIER (',' IDENTIFIER)*
    ;

literalList
    : literal (',' literal)*
    ;

literal
    : INTEGER_LITERAL
    | STRING_LITERAL
    | TRUE
    | FALSE
    ;

// ---------- lexer ----------

CREATE  : C R E A T E ;
TABLE   : T A B L E ;
INDEX   : I N D E X ;
ON      : O N ;
INSERT  : I N S E R T ;
INTO    : I N T O ;
VALUES  : V A L U E S ;
SELECT  : S E L E C T ;
FROM    : F R O M ;
WHERE   : W H E R E ;
AND     : A N D ;
UPDATE  : U P D A T E ;
SET     : S E T ;
DELETE  : D E L E T E ;
INT     : I N T ;
STRING  : S T R I N G ;
BOOL    : B O O L ;
TRUE    : T R U E ;
FALSE   : F A L S E ;
GROUP   : G R O U P ;
BY      : B Y ;
HAVING  : H A V I N G ;
COUNT   : C O U N T ;
SUM     : S U M ;
MIN     : M I N ;
MAX     : M A X ;

ASTERISK        : '*' ;
EQ              : '=' ;
LT              : '<' ;
LE              : '<=' ;
GT              : '>' ;
GE              : '>=' ;

INTEGER_LITERAL : '-'? [0-9]+ ;
STRING_LITERAL  : '\'' (~['\\] | '\\' .)* '\'' ;
IDENTIFIER      : [a-zA-Z_] [a-zA-Z0-9_]* ;
WS              : [ \t\r\n]+ -> skip ;

fragment A : [aA] ;
fragment B : [bB] ;
fragment C : [cC] ;
fragment D : [dD] ;
fragment E : [eE] ;
fragment F : [fF] ;
fragment G : [gG] ;
fragment H : [hH] ;
fragment I : [iI] ;
fragment J : [jJ] ;
fragment K : [kK] ;
fragment L : [lL] ;
fragment M : [mM] ;
fragment N : [nN] ;
fragment O : [oO] ;
fragment P : [pP] ;
fragment Q : [qQ] ;
fragment R : [rR] ;
fragment S : [sS] ;
fragment T : [tT] ;
fragment U : [uU] ;
fragment V : [vV] ;
fragment W : [wW] ;
fragment X : [xX] ;
fragment Y : [yY] ;
fragment Z : [zZ] ;

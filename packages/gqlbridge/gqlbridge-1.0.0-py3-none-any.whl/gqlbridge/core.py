from graphql import parse
from graphql import parse
from graphql.language.printer import print_ast
import re
import pandas as pd
import hashlib
from sqlalchemy import create_engine, text
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import os

def form_list_filter_value(args):
    arg_list = [eachValue['value'] for eachValue in args['value']['values']]
    arg_string = '('
    for eachValue in args['value']['values']:
        if eachValue['kind'] in ['int_value', 'float_value']:
            arg_string += f'{eachValue["value"]},'
        if eachValue['kind'] == 'string_value':
            arg_string += "'" + eachValue["value"] + "',"
    arg_string  = arg_string[:-1]
    arg_string += ')'
    return arg_string

def get_symbol(symbol_string):
    if symbol_string == 'le':
        return '<='
    elif symbol_string == 'ge':
        return '>='
    elif symbol_string == 'lt':
        return '<'
    elif symbol_string == 'gt':
        return '>'
    elif symbol_string == 'eq':
        return '='
    elif symbol_string == 'ne':
        return '!='

def get_args(selection, tableName):
    filterString = ' where '
    for args in selection['arguments']:
        if args['value']['kind'] in ['object_value'] and args['name']['value'] not in ['left', 'right', 'inner', 'full', 'outer', 'full outer', 'cross']:
            symbol = get_symbol(args['value']['fields'][0]['name']['value'])
            if args["value"]["fields"][0]["value"]["kind"] in ['string_value']:
                if re.match(r'.*\d{4}[\\-]\d{2}[\\-]\d{2}.*', args["value"]["fields"][0]["value"]["value"]) or re.match(r'.*\d{2}[\\-]\d{2}[\\-]\d{4}.*', args["value"]["fields"][0]["value"]["value"]):
                    filterString += f'{tableName}.{args["name"]["value"]}::TIMESTAMP {symbol} \'{args["value"]["fields"][0]["value"]["value"]}\'::TIMESTAMP'
                else:
                    filterString += f'{tableName}.{args["name"]["value"]} {symbol} \'{args["value"]["fields"][0]["value"]["value"]}\''
            else:
                filterString += f'{tableName}.{args["name"]["value"]} {symbol} {args["value"]["fields"][0]["value"]["value"]}'

        elif args['value']['kind'] in ['object_value']:
            continue
        elif args['value']['kind'] in ['string_value']:
            if re.match(r'.*\d{4}[\\-]\d{2}[\\-]\d{2}.*', args["value"]["value"]) or re.match(r'.*\d{2}[\\-]\d{2}[\\-]\d{4}.*', args["value"]["value"]):
                filterString += f'{tableName}.{args["name"]["value"]}::TIMESTAMP = \'{args["value"]["value"]}\'::TIMESTAMP'
            else:
                filterString += f'{tableName}.{args["name"]["value"]} = \'{args["value"]["value"]}\''
        elif args['value']['kind'] == 'list_value':
            filterListVal = form_list_filter_value(args)
            filterString += f'{tableName}.{args["name"]["value"]} in {filterListVal}'
        else:
            filterString += f'{tableName}.{args["name"]["value"]} = {args["value"]["value"]}'
        if filterString != ' where ':
            filterString += ' and '
    return filterString[:-5]

def extract_columns(node, path=None, results=None):
    if path is None:
        path = []
    if results is None:
        results = []

    if not isinstance(node, dict):
        return results

    if "name" in node and isinstance(node["name"], dict):
        name_val = node["name"].get("value")
        if name_val:
            path = path + [name_val]

    selection_set = node.get("selection_set", {})
    if isinstance(selection_set, dict):
        selections = selection_set.get("selections", [])
        if isinstance(selections, list):
            for item in selections:
                extract_columns(item, path, results)
            return results

    if path:
        results.append("/".join(path))
    return results

def shorten_alias(alias: str, max_len: int = 63) -> str:

    if len(alias) <= max_len:
        return alias

    prefix_len = max_len - 8
    prefix = alias[:prefix_len]
    suffix = hashlib.md5(alias.encode()).hexdigest()[:8]
    alias_map[f'{prefix}{suffix}'] = alias

    return f"{prefix}{suffix}"

def prepare_json_col(json_schema_list, col_name, tableName):
    alias_counter = {"count": 0}  # simple counter for unique elem aliases

    def next_alias():
        alias_counter["count"] += 1
        return f"elem{alias_counter['count']}"

    def build_grouped(paths, base_ref):

        grouped = {}
        for path in paths:
            head, *tail = path.split('/')
            grouped.setdefault(head, []).append(tail)

        fields = []
        for head, tails in grouped.items():
            if head == "list_items":
                # Handle array expansion → give unique alias
                alias = next_alias()
                inner = build_grouped(
                    ["/".join(t) for t in tails if t],
                    f"{alias}.value"
                )
                return f"""(
                    SELECT jsonb_agg({inner})
                    FROM jsonb_array_elements({base_ref}) {alias}
                )"""
            else:
                # Object or leaf
                if any(t for t in tails):  # deeper fields exist
                    inner = build_grouped(
                        ["/".join(t) for t in tails if t],
                        f"{base_ref}->'{head}'"
                    )
                    fields.append(f"'{head}', {inner}")
                else:  # leaf field
                    fields.append(f"'{head}', {base_ref}->>'{head}'")

        return f"jsonb_build_object({', '.join(fields)})"

    # Root expression build
    json_expr = build_grouped(json_schema_list, f"{tableName}.{col_name}::jsonb")
    return f"\'{col_name}\', {json_expr}, "





def prepare_selection_string(selection, table_or_col_flag, tableName=None): # 0 - col, 1 - table
    if selection['selection_set'] is not None and table_or_col_flag == 1:
        tableName = f"{selection['name']['value']}"
        filterString = get_args(selection, tableName)

        return f' {tableName}{filterString}'
    elif selection['selection_set'] is not None and selection['arguments'] == [] and table_or_col_flag == 0:
        json_schema_list = []
        for eachSelection in selection['selection_set']['selections']:
            json_schema_list += extract_columns(eachSelection)

        json_col = prepare_json_col(json_schema_list, selection['name']['value'], tableName)

        return f'{json_col}'
    elif selection['selection_set'] is None:
        sqlQuery = f'\'{selection["name"]["value"]}\', {tableName}.{selection["name"]["value"]}, '
        return sqlQuery


def get_join_condition_from_graphql(arguments, parent_table, join_table):
    join_type = "INNER JOIN"  # default
    join_condition = ""

    for arg in arguments:
        arg_name = arg['name']['value'].lower()

        if arg_name in ("left", "right", "full", "inner", "cross"):
            # Map GraphQL key -> SQL join type
            join_type = {
                "left": "LEFT JOIN",
                "right": "RIGHT JOIN",
                "full": "FULL JOIN",
                "inner": "INNER JOIN",
                "cross": "CROSS JOIN"
            }[arg_name]

            if arg['value']['kind'] == 'object_value':
                for field in arg['value']['fields']:
                    val = field['value']['value']
                    if val.startswith("eq-"):
                        parent_col = val.replace("eq-", "")
                        join_condition = (
                            f"{parent_table}.{field['name']['value']} = {join_table}.{parent_col}"
                        )

            else:
                raise Exception('Incorrect join condition')

            break  # stop after first valid join

    return join_type, join_condition




def traverse_selections(selectionSet, parent_table=None, table_flag=0):
    sqlQuery = "SELECT " if table_flag == 1 else "SELECT jsonb_build_object("

    if selectionSet['selection_set'] is None:
        raise Exception('Provide columns of the table that need to be fetched')

    for eachSelection in selectionSet['selection_set']['selections']:
        args = eachSelection.get('arguments', [])
        if args != []:
            join_table = eachSelection['name']['value']
            join_query, table_sql = traverse_selections(eachSelection, parent_table=selectionSet['name']['value'], table_flag=1)

            join_type, join_condition = get_join_condition_from_graphql(
                eachSelection['arguments'],
                parent_table=selectionSet['name']['value'],
                join_table=join_table
            )


            if 'where' not in table_sql:
                table_sql = table_sql[:-1] + ' where '
            else :
                table_sql += ' AND '

            join_sql = f"""\'{join_table}\', (
                SELECT jsonb_agg(
                    jsonb_build_object({join_query[6:-2]})
                ) 
             FROM (SELECT * FROM {table_sql} {join_condition}) AS {join_table}
            ), \n"""
            sqlQuery += join_sql

            join_query_list.append(f"{join_type} {join_table} ON {join_condition}")
            continue

        col_sql = prepare_selection_string(eachSelection, 0, selectionSet['name']['value'])
        sqlQuery += col_sql

    table_sql = prepare_selection_string(selectionSet, 1, selectionSet['name']['value'])
    if table_flag == 1:
        return sqlQuery, table_sql
    sqlQuery = f"{sqlQuery[:-2]}) FROM (SELECT * FROM {table_sql}) AS {selectionSet['name']['value']}"
    if join_query_list:
        sqlQuery += " " + " ".join(join_query_list)

    return sqlQuery




def run_query(query: str) -> pd.DataFrame:
    conn_params = {
        "host": os.environ['DB_HOST'],
        "port": os.environ['DB_PORT'],
        "dbname": os.environ['DB_NAME'],
        "user": os.environ['DB_USER'],
        "password": os.environ['DB_PASSWORD']
    }
    conn_url = f'postgresql+psycopg2://{conn_params["user"]}:{conn_params["password"]}@{conn_params["host"]}:{conn_params["port"]}/{conn_params["dbname"]}'

    engine = create_engine(conn_url)
    with engine.connect() as conn:
        df: pd.DataFrame = pd.read_sql(text(query), conn)
    return df

def main(queryStr):
    global join_query_list, alias_map
    alias_map = {}
    join_query_list = []

    # Parse the query into an AST (Abstract Syntax Tree)
    parsedAst = parse(queryStr)

    # Print or inspect the AST

    graphqlDict = parsedAst.to_dict()

    definations = graphqlDict['definitions']
    final_dict = {}
    queries_count = 1

    for defination in definations:
        selectionSet = defination['selection_set']

        for selection in selectionSet['selections']:
            sqlQuery = traverse_selections(selection)
            df = run_query(sqlQuery)

            df.drop_duplicates(inplace=True)
            final_dict[f'Query{queries_count}'] = df['jsonb_build_object'].to_list()
            queries_count += 1


    return json.dumps(final_dict)

if __name__:
    alias_map = {}
    join_query_list = []
    with open('graphql_query.txt', 'r') as file:
        queryStr = file.read()
    resultant_dict = main(queryStr)
    # print(resultant_dict)
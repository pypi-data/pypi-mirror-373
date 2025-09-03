"""
GQLBridge

A package to run GraphQL-style queries on PostgreSQL and return nested JSON results.

Usage:

from GQLBridge import run_graphql_query

query = '''
query {
  project(eq:"demo_project") {
    id
    name
    description
  }
}
'''

result = run_graphql_query(query)
print(result)
"""

from .core import main as run_graphql_query
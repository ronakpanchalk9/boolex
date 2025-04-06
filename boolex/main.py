import re
import pandas as pd

def interpret_query(q_grouped):
    groups_terms = []
    groups_operators = []
    
    if q_grouped[0] == "NOT":
        groups_operators = []
    else:
        groups_operators = ["AND"]
    for term in q_grouped:
        if term in operators:
            groups_operators.append(term)
        else:
            groups_terms.append(f"({simple_bool_to_regex(regex_escape(term))})")

    return {"terms": groups_terms, "operators": groups_operators}

def combine_groups(results, group, operator):
    if operator == "AND":
        results += group
    elif operator == "NOT":
        results = f"(?!{group}){results.strip()}"
    elif operator == "OR":
        results += f"|{group}"
    elif operator == "OR NOT":
        results = f"^(?!{group})|{results.strip()}"
    
    return results

def simple_bool_to_regex(query):
    q = query.strip()
    # Parse the query
    q_parsed = simple_parse_query(q)
    # Split into terms and operators
    q_split = simple_split_query(q_parsed)
    q_terms = q_split["terms"]
    q_operators = q_split["operators"]

    # Assemble the query
    regex = "^"
    for i in range(len(q_terms)):
        regex = simple_append_to_regex(regex, q_terms[i], q_operators[i])

    regex += ".*"
    return regex

def simple_parse_query(q):
    q_parsed = re.sub(r'"(.*?)"', r'\1,', q)
    q_parsed = re.sub(r' *AND *', 'AND,', q_parsed)
    q_parsed = re.sub(r' *OR NOT *', 'OR NOT,', q_parsed)
    q_parsed = re.sub(r' *NOT(?!,) *', 'NOT,', q_parsed)
    q_parsed = re.sub(r' *OR(?! NOT,) *', 'OR,', q_parsed)
    q_parsed = q_parsed.rstrip(',')
    return q_parsed.split(",")

def simple_split_query(q_parsed):
    q_terms = []
    if q_parsed[0] == "NOT":
        q_operators = []
    else:
        q_operators = ["AND"]
    
    for term in q_parsed:
        if term in operators:
            q_operators.append(term)
        else:
            q_terms.append(f".*\\b{term}\\b")
    return {"terms": q_terms, "operators": q_operators}

# Appends a term to the regex based on the operator
def simple_append_to_regex(regex, term, operator):
    if operator == "AND":
        regex += f"(?={term})"
    elif operator == "NOT":
        regex += f"(?!{term})"
    elif operator == "OR":
        regex += f".*|^(?={term})"
    elif operator == "OR NOT":
        regex += f"|^(?!{term})"
    
    return regex


# Escapes special regex characters
def regex_escape(string):
    return re.sub(r'([.?*+^$[\]\\(){}|-])', r'\\\1', string)

def group_query(q):
    q_grouped = re.sub(r' *\((.*?)\) *', r',\1,', q)
    if q_grouped[0] == ",":
        q_grouped = q_grouped[1:]
    
    if q_grouped[-1] == ",":
        q_grouped = q_grouped[:-1]
    
    return q_grouped.split(",")

operators = ["AND", "OR", "NOT", "OR NOT"]

def bool_to_regex(query):
    q = query.strip()
    q_grouped = group_query(q)
    q_interpreted = interpret_query(q_grouped)
    groups_terms = q_interpreted["terms"]
    groups_operators = q_interpreted["operators"]
    results = ""
    for i,terms in enumerate(groups_terms):
        results = combine_groups(results, terms, groups_operators[i])
    return results.strip()

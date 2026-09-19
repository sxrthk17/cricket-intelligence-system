# import spacy
from analytics.analytics_engine import (high_scorer,total_runs, economy_rate, wickets_by_bowler, boundary_count)
import pandas as pd




# ## Spacy works through a language/pipeline model

# string = input("Enter Query: ").strip().lower()

# nlp = spacy.load("en_core_web_sm")

# ## feeding one queestion into the pipeline

# doc = nlp(string)

# ## spaCy doc is iterable: let us run a for loop


import nltk
from nltk.stem import WordNetLemmatizer

string = input("Enter Query: ").strip().lower()

tokens = nltk.word_tokenize(string)
def extract_n(tokens):
    for token in tokens:
        if token.isdigit():
            N = int(token)

            if N > 0:
                return N
            raise ValueError("N must be a positive integer")

    return 1

N = extract_n(tokens)

pos_tags = nltk.pos_tag(tokens)

lemmatizer = WordNetLemmatizer()




def get_wordnet_pos(tag):
    if tag.startswith("V"):
        return "v"
    elif tag.startswith("N"):
        return "n"
    elif tag.startswith("J"):
        return "a"
    elif tag.startswith("R"):
        return "r"
    else:
        return "n"

# # print("Lemma")
# # for token in doc:
# #     print(token, "-->" ,token.lemma_, "-->" , token.pos_)
# # ---------------------------
# # OPERATION VOCABULARY
# # ---------------------------

MAX_WORDS = {
    "most": 3,
    "highest": 3,
    "top": 3,
    "leading": 3,

    # weaker / context-dependent
    "best": 1,
    "high": 1
}

MIN_WORDS = {
    "lowest": 3,
    "least": 3,

    # weaker / context-dependent
    "low": 1,
    "worst": 1,
    "lagging": 1,
    "last": 1,
    "bottom": 1
}
# ---------------------------
# METRIC VOCABULARY
# ---------------------------
RUN_WORDS = {
    "run": 3,
    "score": 2,
    "scorer": 2,
    "scoring":1
}

WICKET_WORDS = {
    "wicket": 3
}

ECONOMY_WORDS = {
    "economy": 3,
    "economical": 2
}

BOUNDARY_WORDS = {
    "boundary": 3,
    "four": 2,
    "six": 2,
    "boundaries":1
}

DISMISSAL_WORDS = {
    "dismissal": 3,
    "dismiss": 2,

    # weaker / context-dependent
    "out": 1
}

# ---------------------------
# ENTITY VOCABULARY
# ---------------------------

BATSMAN_WORDS = {
    "batsman": 3,
    "batter": 3,
    "batting": 2
}

BOWLER_WORDS = {
    "bowler": 3,
    "bowling": 2,
    "baller": 1
}

signals = {
    "max": 0,
    "min": 0,
    "runs": 0,
    "wickets": 0,
    "economy": 0,
    "boundaries": 0,
    "dismissals": 0,
    "batsman": 0,
    "bowler": 0
}



for token, tag in pos_tags:

    lemma = lemmatizer.lemmatize(
        token,
        get_wordnet_pos(tag)
    )

    if lemma in MAX_WORDS:
        print("MAX signal found", lemma)
        weight = MAX_WORDS[lemma]
        print("Weight", weight)
        signals["max"] += weight

    if lemma in MIN_WORDS:
        print("MIN signal found", lemma)
        weight = MIN_WORDS[lemma]
        print("Weight", weight)
        signals["min"] += weight

    if lemma in RUN_WORDS:
        print("RUN signal found:", lemma)
        weight = RUN_WORDS[lemma]
        print("Weight:", weight)
        signals["runs"] += weight

    if lemma in WICKET_WORDS:
        print("WICKET signal found", lemma)
        weight = WICKET_WORDS[lemma]
        print("Weight", weight)
        signals["wickets"] += weight

    if lemma in ECONOMY_WORDS:
        print("ECONOMY signal found", lemma)
        weight = ECONOMY_WORDS[lemma]
        print("Weight", weight)
        signals["economy"] += weight

    if lemma in BOUNDARY_WORDS:
        print("BOUNDARY signal found", lemma)
        weight = BOUNDARY_WORDS[lemma]
        print("Weight", weight)
        signals["boundaries"] += weight

    if lemma in DISMISSAL_WORDS:
        print("DISMISSAL signal found", lemma)
        weight = DISMISSAL_WORDS[lemma]
        print("Weight", weight)
        signals["dismissals"] += weight

    if lemma in BATSMAN_WORDS:
        print("BATSMAN signal found", lemma)
        weight = BATSMAN_WORDS[lemma]
        print("Weight", weight)
        signals["batsman"] += weight

    if lemma in BOWLER_WORDS:
        print("BOWLER signal found", lemma)
        weight = BOWLER_WORDS[lemma]
        print("Weight", weight)
        signals["bowler"] += weight


operation_signals = {
    "max": signals["max"],
    "min": signals["min"]
}

metric_signals = {
    "runs": signals['runs'],
    "wickets": signals['wickets'],
    "economy": signals['economy'],
    "boundaries": signals['boundaries'],
    "dismissals": signals['dismissals'],
}

entity_signals = {
    'batsman':signals['batsman'],
    'bowler': signals['bowler']
}



print(signals)

def choose_operation(signals):
    best_operation = max(signals, key=signals.get)

    if signals[best_operation] == 0:
        return None
    else:
        return best_operation


def choose_metric(signals):
    best_metric = max(signals, key=signals.get)

    if signals[best_metric] == 0:
        return None
    else:
        return best_metric

def choose_entity(signals):
    best_entity = max(signals, key=signals.get)
    if signals[best_entity] == 0:
        return None
    else:
        return best_entity


def infer_entity(selected_metric, entity_signals):
    best_entity = max(entity_signals, key=entity_signals.get)

    if entity_signals[best_entity] > 0:
        return best_entity

    if selected_metric == 'runs':
        return "batsman"

    if selected_metric == "wickets":
        return "bowler"

    if selected_metric =='economy':
        return "bowler"

    if selected_metric == 'dismissals':
        return 'batsman'

    if selected_metric == 'boundaries':
        return 'batsman'



selected_operation = choose_operation(operation_signals)
selected_metric = choose_metric(metric_signals)
selected_entity = infer_entity(selected_metric, entity_signals)

query_meaning = {
    "entity": selected_entity,
    "metric": selected_metric,
    "operation": selected_operation,
}
function_map = {
    ("batsman", "runs"): total_runs,
    ("batsman", "boundaries"): boundary_count,
    ("bowler", "economy"): economy_rate,
    ("bowler", "wickets"): wickets_by_bowler
}

route = (
    query_meaning['entity'],
    query_meaning['metric']
)


def select_result(result_df, metric_column, operation, N=1):

    if operation == "max":
        ascending = False
    elif operation == "min":
        ascending = True
    else: 
        return None

    return (
        result_df.sort_values(by=metric_column, ascending=ascending).head(N).reset_index(drop=True)
    )



df = pd.read_csv('datasets/real_cleaned_deliveries.csv') 

metric_column = {
    "runs":"batsman_runs",
    "boundaries":"boundary_count",
    "economy":"economy_rate",
    "wickets":"total_wickets"
}

if None in route:
    print("Sorry, I could not understand the query.")
else:
    selected_function = function_map[route]

    result = selected_function(df)

    final_result = select_result(result, metric_column[selected_metric], selected_operation, N)

    print(final_result)

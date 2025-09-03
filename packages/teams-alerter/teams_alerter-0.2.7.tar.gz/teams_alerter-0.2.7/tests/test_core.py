import pytest
import os
import json

from teams_alerter.core import TeamsAlerter


def test_error_handler():
    env = "dev"
    ERROR_UTILS = {
        "env": env,
        "app_project_id": os.environ.get("ERROR_HANDLER_APP_PROJECT_ID", "betin-horse-datastream-" + env),
        "topic_project_id": os.environ.get("ERROR_HANDLER_TOPIC_PROJECT_ID", "betin-horse-datastream-" + env),
        "topic_id": os.environ.get("ERROR_HANDLER_TOPIC_ID", "topic-datastream-errors-" + env),
        "app_name": "health_check_check_horses_stats",
        "teams_channel": "datastream-alerts-" + env,
    }
    diffs_list = [
        {
            "idCheval": 1338148,
            "champ": "formFigs",
            "postgres": '<span style="background-color:yellow; color:#000;">5a</span> 8a 8a 3a (24) 13a 12a 9a 10a Da 7a 7m 9a 10a 8m 6a 0a Da 10a 7a 7a (23) 11a 1a 2a 5a 10a 4a Aa 3a 10a Aa 3a 10a 2a 3a 3a 3a Da 4a 7a (22) 7a 3a 3a 1a 12a 6a 1a 1a 2a 7a 1a 4a 4a 1a 6a 1a 4a 10a (21) 14a 4a 5a 4a 1a 3a 2a 4a 7a 3a 5a 4a 6a 2a 2a 7a 7a 7a (20) 1a 1a 2a 4a 6a 1a 3a 5a 1a 1a 4a 1a 3a 4a 2a 2a (19) 4a 5a Da Da 4a 5Da 3a 5a 1a 4a (18) Da Da 5a 2a',
            "mongo": "8a 8a 3a (24) 13a 12a 9a 10a Da 7a 7m 9a 10a 8m 6a 0a Da 10a 7a 7a (23) 11a 1a 2a 5a 10a 4a Aa 3a 10a Aa 3a 10a 2a 3a 3a 3a Da 4a 7a (22) 7a 3a 3a 1a 12a 6a 1a 1a 2a 7a 1a 4a 4a 1a 6a 1a 4a 10a (21) 14a 4a 5a 4a 1a 3a 2a 4a 7a 3a 5a 4a 6a 2a 2a 7a 7a 7a (20) 1a 1a 2a 4a 6a 1a 3a 5a 1a 1a 4a 1a 3a 4a 2a 2a (19) 4a 5a Da Da 4a 5Da 3a 5a 1a 4a (18) Da Da 5a 2a",
            "difference": "5a  manquants dans Mongo",
        },
        {
            "idCheval": 1338148,
            "champ": "totalPrize",
            "postgres": 308670,
            "mongo": 304920,
            "difference": "3750 de moins dans Mongo",
        },
        {
            "idCheval": 1343727,
            "champ": "formFigs",
            "postgres": '<span style="background-color:yellow; color:#000;">4a</span> <span style="background-color:yellow; color:#000;">4a</span> 4m 9m 7a Da 9a 3m (24) 6a 1a 1a 5a 6a 1a Da 4a 6a 4a 3a 5a 2a 0a (23) 9a 6a Da Aa 1a 0a 3a Da 4m 7a 7a Da 3a 4Dista 5a 9a (22) 13a 11a 6a Aa 4a 8a 3a 2a 3a 4a 4a 3a 6a 8a (21) 1a Da 11a 9a 6a 3a 3a 5a 3a Da 2a 4a 1a 11a Da 6a 2a (20) 1a 11a Da 3a Aa 3a 3a 9a 1a 8a 5a (19) 4a 2a 5a 4a 1a 7a',
            "mongo": "4m 9m 7a Da 9a 3m (24) 6a 1a 1a 5a 6a 1a Da 4a 6a 4a 3a 5a 2a 0a (23) 9a 6a Da Aa 1a 0a 3a Da 4m 7a 7a Da 3a 4Dista 5a 9a (22) 13a 11a 6a Aa 4a 8a 3a 2a 3a 4a 4a 3a 6a 8a (21) 1a Da 11a 9a 6a 3a 3a 5a 3a Da 2a 4a 1a 11a Da 6a 2a (20) 1a 11a Da 3a Aa 3a 3a 9a 1a 8a 5a (19) 4a 2a 5a 4a 1a 7a",
            "difference": "4a 4a  manquants dans Mongo",
        },
        {
            "idCheval": 1343727,
            "champ": "totalPrize",
            "postgres": 163935,
            "mongo": 159775,
            "difference": "4160 de moins dans Mongo",
        },
    ]
    error = ValueError(
        ValueError(json.dumps({"data": diffs_list, "message": f"[Vérification horses_stats du 2025-08-29]"}))
    )
    TeamsAlerter.handle_error(error, ERROR_UTILS)

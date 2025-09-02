import json
import traceback

from google.cloud import pubsub_v1
from .utils import ErrorUtils, DateUtils, format_email_template, is_json


class TeamsAlerter:

    def __init__(
        self,
        utils: ErrorUtils,
        payload: None,
    ):
        self.utils = utils
        self.payload = payload

    @staticmethod
    def handle_error(error: Exception, utils: ErrorUtils) -> None:
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        utc_timestamp = DateUtils.get_str_utc_timestamp()
        utc_timestamp_minus_5min = DateUtils.get_str_utc_timestamp_minus_5min()
        utc_timestamp_plus_5min = DateUtils.get_str_utc_timestamp_plus_5min()
        url_log = f"https://console.cloud.google.com/logs/query;cursorTimestamp={utc_timestamp};startTime={utc_timestamp_minus_5min};endTime={utc_timestamp_plus_5min}?referrer=search&hl=fr&inv=1&invt=Ab5Y1Q&project={utils['app_project_id']}"
        # detail = f"Error type: {error_type}\nError message: {error_message}\nError traceback: {error_traceback}"
        detail = {"type": error_type, "message": error_message, "traceback": error_traceback}
        level = "ERROR"

        teams_alerter = TeamsAlerter(utils=utils, payload={})
        teams_alerter.format_payload(detail, level, url_log, utc_timestamp)
        teams_alerter.publish_alert()

    def publish_alert(self):
        # Création d'un éditeur
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.utils["topic_project_id"], self.utils["topic_id"])

        # Message à publier
        data = json.dumps(self.payload).encode("utf-8")

        # Publier le message
        try:
            publish_future = publisher.publish(topic_path, data)
            publish_future.result()

        except Exception as e:
            self.utils["logger"](f"🟥Une erreur s'est produite lors de la publication du message : {e}")

    def format_payload(self, detail, level, url_log, utc_timestamp):
        app_list = {
            "teams": [
                "health_check_check_pg_wal_slot",
                "health_check_check_meetings_ids",
                "health_check_check_races_ids",
                "health_check_check_partants_data",
                "health_check_check_runners_ids",
                "health_check_check_processing_queue_ids",
            ],
            "email": [
                "health_check_check_horses_stats",
            ],
        }

        # base payload
        self.payload = {
            # base info
            "app_name": self.utils["app_name"],
            "detail": detail,
            "level": level,
            "environment": self.utils["env"],
            "url_log": url_log,
            "timestamp": utc_timestamp,
            # alerting info to complete
            "alert_type": [],  # teams, email
            "teams_channel": "",
            "teams_template": "",
            "email_template_html": "",
        }

        if self.utils["app_name"] in app_list["email"]:
            self.format_email_template()

        if self.utils["app_name"] in app_list["teams"] or self.utils["app_name"] not in app_list["email"]:
            self.format_teams_template()

    def format_teams_template(self):
        self.payload["alert_type"].append("teams")
        self.payload["teams_channel"] = self.utils["teams_channel"]
        self.payload["teams_template"] = "card"

    def format_email_template(self):
        self.payload["alert_type"].append("email")
        self.payload["email_object"] = "Contrôle DATASTREAM"

        if self.utils["app_name"] == "health_check_check_horses_stats":
            if is_json(self.payload["detail"]["message"]):
                # cette ligne plante si message n'est pas json
                error_info_list = json.loads(self.payload["detail"]["message"])
                table_data = [("ID CHEVAL", "CHAMP", "POSTGRES", "MONGO", "DIFFERENCE")]
                for error_info in error_info_list["data"]:
                    table_data.append(
                        (
                            error_info["idCheval"],
                            error_info["champ"],
                            error_info["postgres"],
                            error_info["mongo"],
                            error_info["difference"],
                        )
                    )

                email_object = "Contrôle DATASTREAM - Fiche cheval"
                self.payload["email_object"] = email_object
                email_messages = [
                    """
                        Bonjour, <br>
                        Veuillez trouver ci-dessous le tableau récapitulatif du contrôle effectué sur la fiche cheval dans Datastream.
                    """,
                    f"""
                        Env: <strong>{self.utils["env"]}</strong> <br>
                        Timestamp: {DateUtils.get_str_utc_timestamp()} <br>
                        Champs: <strong>formFigs et/ou totalPrize</strong>
                    """,
                ]

                self.payload["email_template_html"] = format_email_template(email_object, email_messages, table_data)
            else:
                print("⚠ ERREUR INTERNE : error_message n'est pas un JSON valide :", self.payload["detail"]["message"])

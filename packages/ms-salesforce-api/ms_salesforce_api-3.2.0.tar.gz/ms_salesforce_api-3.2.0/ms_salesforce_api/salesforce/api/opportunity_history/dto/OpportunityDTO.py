from datetime import datetime

from ms_salesforce_api.salesforce.helpers.string import normalize_value


class OpportunityHistoryDTO(object):
    def __init__(
        self,
        opportunity_history_id,
        opportunity_id,
        stage_name,
        forecast_category,
        amount,
        prev_amount,
        expected_revenue,
        close_date,
        prev_close_date,
        probability,
        created_date,
    ):
        self.opportunity_history_id = opportunity_history_id
        self.opportunity_id = opportunity_id
        self.stage_name = stage_name
        self.forecast_category = forecast_category
        self.amount = amount
        self.prev_amount = prev_amount
        self.expected_revenue = expected_revenue
        self.close_date = close_date
        self.prev_close_date = prev_close_date
        self.probability = probability
        self.created_date = created_date

    @staticmethod
    def from_salesforce_record(record):
        def _parse_created_date(created_date):
            try:
                dt = datetime.strptime(
                    created_date,
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )

                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return ""

        return OpportunityHistoryDTO(
            opportunity_history_id=record["Id"],
            opportunity_id=record["OpportunityId"],
            stage_name=normalize_value(record.get("StageName", "")),
            forecast_category=normalize_value(
                record.get("ForecastCategory", "")
            ),
            amount=record.get("Amount", 0.0),
            prev_amount=record.get("PrevAmount", 0.0),
            expected_revenue=record.get("ExpectedRevenue", 0.0),
            close_date=record["CloseDate"],
            prev_close_date=record["PrevCloseDate"],
            probability=record.get("Probability", 0.0),
            created_date=_parse_created_date(record["CreatedDate"]),
        )

    def to_dict(self):
        return {
            "opportunity_history_id": self.opportunity_history_id,
            "opportunity_id": self.opportunity_id,
            "stage_name": self.stage_name,
            "forecast_category": self.forecast_category,
            "amount": self.amount,
            "prev_amount": self.prev_amount,
            "expected_revenue": self.expected_revenue,
            "close_date": self.close_date,
            "prev_close_date": self.prev_close_date,
            "probability": self.probability,
            "created_date": self.created_date,
        }

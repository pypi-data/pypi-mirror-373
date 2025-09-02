from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING, Any

import pandas as pd
from pandas.tseries.offsets import BMonthEnd
from wbfdm.models import InstrumentList
from wbreport.mixins import ReportMixin

if TYPE_CHECKING:
    from wbcore.contrib.authentication.models import User
    from wbreport.models import Report, ReportVersion


class ReportClass(ReportMixin):
    @classmethod
    def parse_parameters(cls, parameters: dict[str, str]) -> dict[str, Any]:
        return {
            "end": datetime.strptime(parameters["end"], "%Y-%m-%d").date(),
        }

    @classmethod
    def get_next_parameters(cls, parameters: dict[str, Any]) -> dict[str, Any]:
        parse_parameters = cls.parse_parameters(parameters)
        return {
            "end": datetime.strftime((parse_parameters["end"] + BMonthEnd(1)).date(), "%Y-%m-%d"),
        }

    @classmethod
    def get_version_date(cls, parameters) -> datetime.date:
        parameters = cls.parse_parameters(parameters)
        return parameters["end"]

    @classmethod
    def get_version_title(cls, report_title: str, parameters: dict[str, Any]) -> str:
        parameters = cls.parse_parameters(parameters)
        return f"{report_title} - {parameters['end']:%b %Y}"

    @classmethod
    def has_view_permission(cls, report: "Report", user: "User") -> bool:
        return user.has_perms(["wbreport.view_report", "wbportfolio.view_assetposition"])

    @classmethod
    def get_context(cls, version: "ReportVersion") -> dict[str, Any]:
        instrument_list: "InstrumentList" = version.report.content_object
        end_date = version.parameters.get("end")
        positions = []

        for instrument in instrument_list.instruments.all():
            if portfolio := instrument.primary_portfolio:
                for position in portfolio.assets.filter(date=end_date):
                    positions.append(
                        {
                            "portfolio": instrument.name,
                            "isin": position.underlying_instrument.isin,
                            "title": position.underlying_instrument.name_repr,
                            "instrument_type": position.underlying_instrument.instrument_type.short_name,
                            "weight": float(position.weighting),
                            "date": position.date.strftime("%Y-%m-%d"),
                        }
                    )

        return {"positions": positions}

    @classmethod
    def generate_file(cls, context: dict[str, Any]) -> BytesIO:
        stream = BytesIO()
        if positions := context.get("positions", None):
            df = pd.DataFrame(positions).sort_values(by=["weight"], ascending=False)
            writer = pd.ExcelWriter(stream, engine="xlsxwriter")
            for portfolio, dff in df.groupby("portfolio"):
                dff.to_excel(writer, sheet_name=portfolio[0:31], index=False)
            writer.save()
        return stream

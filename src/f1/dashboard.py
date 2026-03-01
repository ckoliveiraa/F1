import pandas as pd
import plotly.express as px
import streamlit as st

from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)
from f1.utils.config import DEFAULT_YEAR


@st.cache_resource
def get_service() -> F1DashboardService:
    client = HttpClient()
    return F1DashboardService(
        meeting_repo=OpenF1MeetingRepository(client),
        session_repo=OpenF1SessionRepository(client),
        lap_repo=OpenF1LapRepository(client),
        driver_repo=OpenF1DriverRepository(client),
    )


@st.cache_data(ttl=3600)
def fetch_meetings(year: int) -> list[dict]:
    service = get_service()
    meetings = service.get_meetings_for_year(year)
    return [m.model_dump() for m in meetings]


def main() -> None:
    st.set_page_config(page_title="F1 Fastest Laps", page_icon="🏎️", layout="wide")
    st.title("🏎️ F1 — 5 Voltas Mais Rápidas por Circuito")

    with st.sidebar:
        st.header("Filtros")
        year = st.selectbox(
            "Ano",
            options=[2023, 2024, 2025],
            index=[2023, 2024, 2025].index(DEFAULT_YEAR),
        )
        session_name = st.selectbox("Tipo de Sessão", options=["Race", "Qualifying"])

    meetings_data = fetch_meetings(year)

    if not meetings_data:
        st.warning(f"Nenhuma etapa encontrada para {year}.")
        return

    service = get_service()

    for meeting_dict in meetings_data:
        meeting_key = meeting_dict["meeting_key"]
        meeting_name = meeting_dict["meeting_name"]
        circuit = meeting_dict["circuit_short_name"]
        country = meeting_dict["country_name"]

        with st.expander(f"🏁 {meeting_name} — {circuit}, {country}"):
            with st.spinner("Carregando voltas..."):
                try:
                    entries = service.get_top_laps_for_meeting(
                        meeting_key, session_name
                    )
                except Exception as exc:
                    st.error(f"Erro ao carregar dados: {exc}")
                    continue

            if not entries:
                st.info("Sem dados de voltas disponíveis para esta sessão.")
                continue

            df = pd.DataFrame([e.model_dump() for e in entries])
            df["lap_duration_fmt"] = df["lap_duration"].apply(
                lambda s: f"{int(s // 60)}:{s % 60:06.3f}"
            )

            st.subheader(f"Top {len(entries)} Voltas Mais Rápidas")
            st.dataframe(
                df[
                    [
                        "rank",
                        "driver_name",
                        "driver_acronym",
                        "team_name",
                        "lap_number",
                        "lap_duration_fmt",
                    ]
                ].rename(
                    columns={
                        "rank": "Pos",
                        "driver_name": "Piloto",
                        "driver_acronym": "Acrônimo",
                        "team_name": "Equipe",
                        "lap_number": "Volta",
                        "lap_duration_fmt": "Tempo",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            colors = {
                row["driver_acronym"]: f"#{row['team_colour']}"
                for _, row in df.iterrows()
            }
            fig = px.bar(
                df,
                x="driver_acronym",
                y="lap_duration",
                color="driver_acronym",
                color_discrete_map=colors,
                labels={"driver_acronym": "Piloto", "lap_duration": "Tempo (s)"},
                title=f"Tempos de Volta — {meeting_name}",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

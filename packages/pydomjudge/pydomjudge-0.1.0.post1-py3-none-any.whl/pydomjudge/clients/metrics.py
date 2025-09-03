from pydomjudge.clients.client import _Client


class MetricsClient(_Client):
    def get_metrics(self, strict: bool = False) -> str:
        url = f"{self.base_url}/api/v4/metrics/prometheus"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.text

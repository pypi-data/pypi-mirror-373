"""HTML chart"""

from typing import Any, Dict, Self

from pydantic import BaseModel, Field


class HTMLChart(BaseModel):
  """HTML chart configuration"""

  content: str = Field(description='HTML content of the chart', default='<p>N/A</p>')
  title: str = Field(description='Title of the chart', default='Chart')

  def render(self: Self) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    return {'library': 'HTML', 'configuration': self._render_html()}

  def _render_html(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to HTML render engine.
    """
    config = {'content': self.content, 'title': self.title}

    return config

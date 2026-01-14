import BarChartView from "./BarChartView";
import LineChartView from "./LineChartView";
import KPIView from "./KPIView";
import TableView from "./TableView";
import AreaChartView from "./AreaChartView";
import HistogramView from "./HistogramView";
import { isChartRenderable } from "../utils/isChartRenderable";

function ChartRenderer({ visualization, data }) {
  if (!isChartRenderable(visualization, data)) {
    return null;
  }

  switch (visualization.type) {
    case "bar":
      return <BarChartView data={data} xKey={visualization.x} yKey={visualization.y} />;

    case "line":
      return <LineChartView data={data} xKey={visualization.x} yKey={visualization.y} />;

    case "area":
      return <AreaChartView data={data} xKey={visualization.x} yKey={visualization.y} />;

    case "histogram":
      return <HistogramView data={data} valueKey={visualization.value} />;

    case "kpi":
      return <KPIView data={data} />;

    case "table":
      return <TableView data={data} />;

    default:
      return null;
  }
}

export default ChartRenderer;

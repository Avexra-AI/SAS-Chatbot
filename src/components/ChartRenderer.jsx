import BarChartView from "./BarChartView";
import LineChartView from "./LineChartView";
import KPIView from "./KPIView";
import TableView from "./TableView";
import { isChartRenderable } from "../utils/isChartRenderable";

function ChartRenderer({ visualization, data }) {
  if (!isChartRenderable(visualization, data)) {
    return null; // ❗ nothing renders, UI stays clean
  }

  switch (visualization.type) {
    case "bar":
      return (
        <BarChartView
          data={data}
          xKey={visualization.x}
          yKey={visualization.y}
        />
      );

    case "line":
      return (
        <LineChartView
          data={data}
          xKey={visualization.x}
          yKey={visualization.y}
        />
      );

    case "kpi":
      return <KPIView data={data} />;

    default:
      return null;
  }
}

export default ChartRenderer;

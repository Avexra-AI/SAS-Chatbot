export function isChartRenderable(visualization, data) {
  if (!visualization) return false;
  if (!data || !Array.isArray(data) || data.length === 0) return false;

  // KPI
  if (visualization.type === "kpi") {
    return true;
  }

  // Bar / Line / Area
  if (["bar", "line", "area"].includes(visualization.type)) {
    const { x, y } = visualization;
    if (!x || !y) return false;

    return data.every(
      (row) =>
        row[x] !== null &&
        row[x] !== undefined &&
        row[y] !== null &&
        row[y] !== undefined
    );
  }

  // Histogram
  if (visualization.type === "histogram") {
    return !!visualization.value;
  }

  // Table
  if (visualization.type === "table") {
    return true;
  }

  return false;
}

export function isChartRenderable(visualization, data) {
  if (!visualization || !data || data.length === 0) return false;

  const { type, x, y } = visualization;

  if (!type || type === "table" || type === "empty") return false;
  if (!x || !y) return false;

  for (const row of data) {
    if (
      row[x] === null ||
      row[x] === undefined ||
      row[y] === null ||
      row[y] === undefined
    ) {
      return false;
    }
  }

  return true;
}

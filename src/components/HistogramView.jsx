import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function HistogramView({ data, valueKey, bins = 10 }) {
  // create bins manually
  const values = data.map((d) => d[valueKey]);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const step = (max - min) / bins;

  const histogram = Array.from({ length: bins }, (_, i) => ({
    range: `${Math.round(min + i * step)} - ${Math.round(
      min + (i + 1) * step
    )}`,
    count: 0,
  }));

  values.forEach((val) => {
    const index = Math.min(
      Math.floor((val - min) / step),
      bins - 1
    );
    histogram[index].count += 1;
  });

  return (
    <div style={{ height: 350, marginTop: "30px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={histogram}>
          <XAxis dataKey="range" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#4f46e5" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default HistogramView;

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function GroupedBarChartView({ data, xKey, groupKey, yKey, stacked = false }) {
  // find unique groups
  const groups = [...new Set(data.map((d) => d[groupKey]))];

  return (
    <div style={{ height: 350, marginTop: "30px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          {groups.map((group) => (
            <Bar
              key={group}
              dataKey={(d) => (d[groupKey] === group ? d[yKey] : 0)}
              name={group}
              stackId={stacked ? "stack" : undefined}
              fill="#4f46e5"
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default GroupedBarChartView;

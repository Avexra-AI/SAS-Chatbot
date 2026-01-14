import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function AreaChartView({ data, xKey, yKey }) {
  return (
    <div style={{ height: 350, marginTop: "30px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Area
            type="monotone"
            dataKey={yKey}
            stroke="#4f46e5"
            fill="#6366f1"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AreaChartView;

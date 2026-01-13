function LineChartView({ data, config }) {
  return (
    <div>
      <h3>Trend</h3>
      {data.map((row, i) => (
        <p key={i}>
          {row[config.x]} : {row[config.y]}
        </p>
      ))}
    </div>
  );
}

export default LineChartView;

function KPIView({ data, config }) {
  const row = data[0];

  return (
    <div className="kpi-card">
      <h3>{config.label || "Value"}</h3>
      <h1>{Object.values(row)[1]}</h1>
    </div>
  );
}

export default KPIView;

function AlertCard({ alert, onClick, isSelected }) {
  return (
    <div
      className={`alert-card ${alert.risk_level.toLowerCase()} ${
        isSelected ? "selected" : ""
      }`}
      onClick={() => onClick(alert)}
    >
      <div className="alert-card-header">
        <strong>{alert.alert_id}</strong>

        <span className={`risk ${alert.risk_level.toLowerCase()}`}>
          {alert.risk_level}
        </span>
      </div>

      <p>
        Risk Score: <strong>{alert.risk_score}%</strong>
      </p>

      <p>
        Status: <strong>{alert.status}</strong>
      </p>
    </div>
  );
}

export default AlertCard;
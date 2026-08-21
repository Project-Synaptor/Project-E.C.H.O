function StatusBadge({ status }) {

  let label = status;


  if (status === "UNVERIFIED") {
    label = "Unverified";
  }


  if (status === "VALIDATED_TRUE") {
    label = "Validated";
  }


  if (status === "FALSE_POSITIVE") {
    label = "False Positive";
  }


  return (
    <span className={`status-badge ${status.toLowerCase()}`}>
      {label}
    </span>
  );
}


export default StatusBadge;
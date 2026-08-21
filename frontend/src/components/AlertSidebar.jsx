import { useState } from "react";
import StatusBadge from "./StatusBadge";


function AlertSidebar({ alert, onClose, onValidate }) {
   
    const [feedback, setFeedback] = useState("");

    // If no alert is selected, don't show anything
    if (!alert) {
        return null;
    }


    return (
        <div className="sidebar">

            {/* Close button */}
            <button
                className="close-button"
                onClick={onClose}
            >
                ✕
            </button>


            {/* Alert ID */}
            <h2>{alert.alert_id}</h2>


            {/* Risk information */}
            <h3>
                Risk Score: {alert.risk_score}%
            </h3>

            <p>
                Risk Level:
                <strong> {alert.risk_level}</strong>
            </p>


            {/* Status */}
            <p>
                Status:{" "}
                <StatusBadge status={alert.status} />
            </p>


            <hr />


            {/* Evidence */}
            <h3>Evidence</h3>

            <p>
                {alert.evidence}
            </p>


            {/* Location */}
            <h3>Location</h3>

            <p>
                Latitude: {alert.latitude}
                <br />
                Longitude: {alert.longitude}
            </p>


            {/* Timestamp */}
            <h3>Time</h3>

            <p>
                {new Date(alert.timestamp).toLocaleString()}
            </p>


            <hr />


            {/* Validation buttons */}
            {/* <button
                className="validate-button"
                onClick={() => onValidate(alert.alert_id, true)}
            >
                ✓ Validate Alert
            </button>


            <button
                className="false-button"
                onClick={() => onValidate(alert.alert_id, false)}
            >
                ✕ Report False Positive
            </button> */}
            {/* User feedback */}

            <h3>Feedback</h3>

            <textarea
                className="feedback-box"
                placeholder="Enter your feedback (optional)"
                maxLength={300}
                rows={4}
                value={feedback}
                onChange={(event) => setFeedback(event.target.value)}
            />

            <p className="character-count">
                {feedback.length}/300
            </p>


            {/* Validation buttons */}

            <button
                className="validate-button"
                onClick={() => onValidate(
                    alert.alert_id,
                    true,
                    feedback.trim() === "" ? null : feedback
                )}
            >
                ✓ Validate Alert
            </button>


            <button
                className="false-button"
                onClick={() => onValidate(
                    alert.alert_id,
                    false,
                    feedback.trim() === "" ? null : feedback
                )}
            >
                ✕ Report False Positive
            </button>
        </div>
    );
}


export default AlertSidebar;
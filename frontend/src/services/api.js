const API_BASE_URL = import.meta.env.VITE_API_URL;

export async function getAlerts() {
  const response = await fetch(`${API_BASE_URL}/alerts`);

  if (!response.ok) {
    throw new Error("Failed to fetch alerts");
  }

  return response.json();
}

export async function validateAlert(
  alertId,
  isValid,
  userFeedback = null
) {
  const response = await fetch(`${API_BASE_URL}/validate`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      alert_id: alertId,
      is_valid: isValid,
      user_feedback: userFeedback,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to validate alert");
  }

  return response.json();
}
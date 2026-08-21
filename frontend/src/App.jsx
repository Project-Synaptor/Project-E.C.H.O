import { useEffect, useState } from "react";
import { getAlerts, validateAlert } from "./api";

import MapView from "./components/MapView";
import AlertCard from "./components/AlertCard";
import AlertSidebar from "./components/AlertSidebar";

import "./App.css";


function App() {

  // Alerts received from the backend
  const [alerts, setAlerts] = useState([]);

  // Loading state
  const [loading, setLoading] = useState(true);

  // Error state
  const [error, setError] = useState(null);

  // Currently selected alert
  const [selectedAlert, setSelectedAlert] = useState(null);


  // Load alerts from backend
  useEffect(() => {

    async function loadAlerts() {

      try {

        setLoading(true);

        const data = await getAlerts();


        setAlerts(data);

        setError(null);

      } catch (err) {

        console.error("Error loading alerts:", err);

        setError("Unable to load alerts.");

      } finally {

        setLoading(false);

      }

    }

    loadAlerts();

  }, []);


  // Validate / reject an alert
  const handleValidation = async (
    alertId,
    isValid,
    userFeedback
  ) => {

    try {

      // Send validation to backend
      const result = await validateAlert(
        alertId,
        isValid,
        userFeedback
      );



      // Determine the new status
      const newStatus = isValid
        ? "VALIDATED_TRUE"
        : "FALSE_POSITIVE";


      // Update the alert in the alert list
      setAlerts((currentAlerts) => {

        return currentAlerts.map((alert) => {

          if (alert.alert_id === alertId) {

            return {
              ...alert,
              status: newStatus
            };

          }

          return alert;

        });

      });


      // Update the currently selected alert
      setSelectedAlert((currentAlert) => {

        if (
          currentAlert &&
          currentAlert.alert_id === alertId
        ) {

          return {
            ...currentAlert,
            status: newStatus
          };

        }

        return currentAlert;

      });



    } catch (err) {

      console.error(
        "Validation failed:",
        err
      );

      alert(
        "Unable to validate alert. Please try again."
      );

    }

  };


  // Loading screen
  if (loading) {

    return (
      <div>
        Loading alerts...
      </div>
    );

  }


  // Error screen
  if (error) {

    return (
      <div>
        {error}
      </div>
    );

  }


  return (

    <div className="dashboard">


      {/* Header */}

      <header className="header">

        <h1>E.C.H.O.</h1>

        <span>
          Field Dashboard
        </span>

      </header>


      {/* Alert List */}

      <aside className="alerts-panel">

        <h2>Alerts</h2>

        {alerts.map((alert) => (

          <AlertCard
            key={alert.alert_id}
            alert={alert}
            onClick={setSelectedAlert}
            isSelected={
              selectedAlert?.alert_id === alert.alert_id
            }
          />

        ))}

      </aside>


      {/* Map */}

      <main className="map-area">

        <MapView
          alerts={alerts}
          selectedAlert={selectedAlert}
        />

      </main>


      {/* Alert Details */}

      {selectedAlert && (

        <AlertSidebar
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onValidate={handleValidation}
        />

      )}

    </div>

  );

}


export default App;
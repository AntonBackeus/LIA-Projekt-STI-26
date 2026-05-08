import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [statuses, setStatuses] = useState([]);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      fetch('/api/status')
        .then(res => res.json())
        .then(data => setStatuses(data))
        .catch(err => console.error(err));
        
      fetch('/api/errors')
        .then(res => res.json())
        .then(data => setErrors(data))
        .catch(err => console.error(err));
    };
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Omron Status Monitor</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '40px', marginTop: '30px' }}>
        {statuses.map(robot => {
          const data = robot.enriched_data || {};
          const isOn = data.Value >= 3; // 3+ means power is on in Omron Robot State
          const robotError = errors.find(e => e.robot_address === robot.robot_address);
          
          return (
            <div key={robot.robot_address} className={`status-card ${isOn ? 'running' : 'fatal'}`} style={{ borderRadius: '12px', padding: '20px', minWidth: '250px', backgroundColor: isOn ? '#d4edda' : '#f8d7da', color: '#333' }}>
              <h2>{robot.robot_address}</h2>
              <h3 style={{ color: isOn ? '#155724' : '#721c24' }}>{isOn ? 'ON' : 'OFF'}</h3>
              <p>{data.Meaning}</p>
              <small>Last Update: {new Date(robot.ts).toLocaleTimeString()}</small>
              {robotError && (
                <div className="error-card" style={{ marginTop: '15px', padding: '10px', borderRadius: '8px', color: 'white' }}>
                  <strong>⚠️ ERROR:</strong> {robotError.enriched_data?.Meaning || 'Unknown Error'}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default App;
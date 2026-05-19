import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CombinedRobotData {
  robot_address: string;
  status_data?: {
    Value?: number;
    Meaning?: string;
  };
  status_ts?: string;
  error_data?: {
    Meaning?: string;
  };
  error_ts?: string;
}

export default function App() {
  const [robots, setRobots] = useState<CombinedRobotData[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsRefreshing(true);
      try {
        const response = await fetch('/api/Status_and_errors');
        if (response.ok) {
          const data: CombinedRobotData[] = await response.json();
          setRobots(data);
          if (isOffline) setIsOffline(false);
        } else {
          // Handle server errors (e.g., 500)
          if (!isOffline) setIsOffline(true);
        }
      } catch (err) {
        // Handle network errors (e.g., server is down)
        console.error("API connection failed:", err);
        if (!isOffline) setIsOffline(true);
      } finally {
        setTimeout(() => setIsRefreshing(false), 500);
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [isOffline]);

  return (
    <div className="min-h-screen bg-slate-50 font-sans p-4">
      <h1 className="text-3xl font-bold text-center mb-8 text-slate-800">Omron Status Monitor</h1>
      
      <div className="max-w-md mx-auto space-y-6">
        {robots.length === 0 && !isOffline && (
          <div className="text-center py-10 px-6 bg-slate-100 rounded-xl shadow-sm">
            <p className="font-semibold text-slate-600">Awaiting Data</p>
            <p className="text-sm text-slate-400 mt-1">
              No robot data has been received. Make sure robots are connected and sending data to the TCP server.
            </p>
          </div>
        )}
        <AnimatePresence mode="popLayout">
          {robots.map((robot) => {
            const statusData = robot.status_data || {};
            const isOn = (statusData.Value || 0) >= 3;
            const lastUpdate = robot.status_ts || robot.error_ts;
            return (
              <motion.div
                key={robot.robot_address}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className={`rounded-xl p-5 shadow-sm transition-colors ${
                  isOn 
                    ? 'bg-[#d4edda] text-[#155724]' 
                    : 'bg-[#f8d7da] text-[#721c24]'
                }`}
              >
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold truncate">{robot.robot_address}</h2>
                  <span className="text-3xl font-black">{isOn ? 'ON' : 'OFF'}</span>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-[10px] uppercase font-bold opacity-60 mb-0.5">Current State</p>
                    <p className="font-semibold leading-snug">{statusData.Meaning || 'Awaiting Data...'}</p>
                  </div>

                  <div className="flex justify-between items-center opacity-70 text-[11px] font-bold">
                    <span>Last Update:</span>
                    <span>{lastUpdate ? new Date(lastUpdate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }) : '--:--'}</span>
                  </div>

                  {robot.error_data && (
                    <div className="mt-4 bg-red-700 text-white rounded-lg p-3 shadow-inner">
                      <p className="text-sm font-bold">
                        ERROR: <span className="font-medium opacity-90">{robot.error_data.Meaning || 'System fault detected'}</span>
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
      
      <AnimatePresence>
        {isOffline && (
          <motion.div 
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-red-600 text-white font-bold py-2 px-6 rounded-full shadow-lg">Connection to Server Lost</motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}

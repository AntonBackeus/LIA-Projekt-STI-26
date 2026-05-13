import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface RobotData {
  Value?: number;
  Meaning?: string;
}

interface RobotStatus {
  robot_address: string;
  ts: string;
  enriched_data: RobotData;
}

interface RobotError {
  robot_address: string;
  enriched_data?: {
    Meaning?: string;
  };
}

const MOCK_STATUSES: RobotStatus[] = [
  {
    robot_address: "Robot_01",
    ts: new Date().toISOString(),
    enriched_data: { Value: 4, Meaning: "Normal Operation" }
  },
  {
    robot_address: "Robot_02",
    ts: new Date().toISOString(),
    enriched_data: { Value: 1, Meaning: "Emergency Stop" }
  }
];

const MOCK_ERRORS: RobotError[] = [
  {
    robot_address: "Robot_02",
    enriched_data: { Meaning: "Joint 3 torque limit exceeded" }
  }
];

export default function App() {
  const [statuses, setStatuses] = useState<RobotStatus[]>(MOCK_STATUSES);
  const [errors, setErrors] = useState<RobotError[]>(MOCK_ERRORS);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsRefreshing(true);
      try {
        const [statusRes, errorRes] = await Promise.all([
          fetch('/api/status').catch(() => null),
          fetch('/api/errors').catch(() => null)
        ]);

        if (statusRes && statusRes.ok) {
          const data = await statusRes.json();
          setStatuses(data);
        }
        
        if (errorRes && errorRes.ok) {
          const data = await errorRes.json();
          setErrors(data);
        }
      } catch (err) {
        console.error("Link offline");
      } finally {
        setTimeout(() => setIsRefreshing(false), 500);
      }
    };

    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 font-sans p-4">
      <h1 className="text-3xl font-bold text-center mb-8 text-slate-800">Omron Status Monitor</h1>
      
      <div className="max-w-md mx-auto space-y-6">
        <AnimatePresence mode="popLayout">
          {statuses.map((robot) => {
            const data = robot.enriched_data || {};
            const isOn = (data.Value || 0) >= 3;
            const robotError = errors.find(e => e.robot_address === robot.robot_address);
            
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
                    <p className="font-semibold leading-snug">{data.Meaning || 'Unknown State'}</p>
                  </div>

                  <div className="flex justify-between items-center opacity-70 text-[11px] font-bold">
                    <span>Last Update:</span>
                    <span>{new Date(robot.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</span>
                  </div>

                  {robotError && (
                    <div className="mt-4 bg-red-700 text-white rounded-lg p-3 shadow-inner">
                      <p className="text-sm font-bold">
                        ERROR: <span className="font-medium opacity-90">{robotError.enriched_data?.Meaning || 'System fault detected'}</span>
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

    </div>
  );
}

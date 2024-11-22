import { useState, useEffect } from 'react';
import { LineChart, BarChart, Card, Badge } from '@/components/ui';
import { Settings, Power, Droplet, Clock, TrendingDown } from 'lucide-react';

const Dashboard = () => {
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [rates, setRates] = useState([]);
  const [mode, setMode] = useState('optimized');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, statsRes, ratesRes] = await Promise.all([
          fetch('/api/status'),
          fetch('/api/statistics'),
          fetch('/api/rates/history')
        ]);
        
        setStatus(await statusRes.json());
        setStats(await statsRes.json());
        setRates(await ratesRes.json());
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleModeChange = async (newMode, duration = 0) => {
    try {
      await fetch('/api/mode', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: newMode, boost_duration: duration })
      });
      setMode(newMode);
    } catch (error) {
      console.error('Failed to update mode:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Smart Water Heating</h1>
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-full hover:bg-gray-200"
          >
            <Settings className="w-6 h-6" />
          </button>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Current Rate</p>
                <p className="text-2xl font-bold">
                  {status?.current_rate?.toFixed(2)}p/kWh
                </p>
              </div>
              <Badge variant={status?.is_peak ? "destructive" : "success"}>
                {status?.is_peak ? "Peak" : "Off-Peak"}
              </Badge>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Heating Status</p>
                <p className="text-2xl font-bold">{status?.is_heating ? "On" : "Off"}</p>
              </div>
              <Power 
                className={`w-6 h-6 ${status?.is_heating ? "text-green-500" : "text-gray-400"}`}
              />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Monthly Savings</p>
                <p className="text-2xl font-bold">
                  £{stats?.savings?.toFixed(2)}
                </p>
              </div>
              <TrendingDown className="w-6 h-6 text-green-500" />
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-4">
            <h2 className="text-lg font-semibold mb-4">Electricity Rates</h2>
            <LineChart 
              data={rates}
              width={500}
              height={300}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            />
          </Card>

          <Card className="p-4">
            <h2 className="text-lg font-semibold mb-4">Heating Duration</h2>
            <BarChart 
              data={stats?.heating_durations || []}
              width={500}
              height={300}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            />
          </Card>
        </div>

        {/* Controls */}
        <Card className="mt-6 p-4">
          <h2 className="text-lg font-semibold mb-4">Quick Controls</h2>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => handleModeChange('optimized')}
              className={`px-4 py-2 rounded-lg ${
                mode === 'optimized' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Optimized
            </button>
            <button
              onClick={() => handleModeChange('boost', 30)}
              className={`px-4 py-2 rounded-lg ${
                mode === 'boost'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              30min Boost
            </button>
            <button
              onClick={() => handleModeChange('boost', 60)}
              className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300"
            >
              60min Boost
            </button>
            <button
              onClick={() => handleModeChange('off')}
              className={`px-4 py-2 rounded-lg ${
                mode === 'off'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Turn Off
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
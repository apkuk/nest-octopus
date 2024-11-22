import { useState, useEffect } from 'react';
import { Card, Button, Input, Switch, Alert } from '@/components/ui';
import { Plus, Trash2, Save, Clock, Calendar } from 'lucide-react';

const Settings = () => {
  const [heatingWindows, setHeatingWindows] = useState([]);
  const [systemSettings, setSystemSettings] = useState({
    minTemp: 50,
    maxTemp: 60,
    cheapRateThreshold: 15,
    expensiveRateThreshold: 25,
    peakStartTime: '16:00',
    peakEndTime: '19:00'
  });
  const [showAlert, setShowAlert] = useState(false);

  const daysOfWeek = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
    'Friday', 'Saturday', 'Sunday'
  ];

  useEffect(() => {
    fetchHeatingWindows();
    fetchSystemSettings();
  }, []);

  const fetchHeatingWindows = async () => {
    try {
      const response = await fetch('/api/heating-windows');
      const data = await response.json();
      setHeatingWindows(data.windows);
    } catch (error) {
      console.error('Failed to fetch heating windows:', error);
    }
  };

  const fetchSystemSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSystemSettings(data);
    } catch (error) {
      console.error('Failed to fetch system settings:', error);
    }
  };

  const addHeatingWindow = () => {
    setHeatingWindows([
      ...heatingWindows,
      {
        start_time: '06:00',
        duration: 60,
        days: [],
        enabled: true
      }
    ]);
  };

  const updateHeatingWindow = (index, field, value) => {
    const updatedWindows = [...heatingWindows];
    updatedWindows[index] = {
      ...updatedWindows[index],
      [field]: value
    };
    setHeatingWindows(updatedWindows);
  };

  const deleteHeatingWindow = (index) => {
    setHeatingWindows(heatingWindows.filter((_, i) => i !== index));
  };

  const saveSettings = async () => {
    try {
      await Promise.all([
        fetch('/api/heating-windows', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ windows: heatingWindows })
        }),
        fetch('/api/settings', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(systemSettings)
        })
      ]);
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {showAlert && (
        <Alert className="mb-4 bg-green-100 border-green-500">
          Settings saved successfully!
        </Alert>
      )}

      <Card className="mb-6">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Clock className="mr-2" />
            Heating Windows
          </h2>
          
          <div className="space-y-4">
            {heatingWindows.map((window, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Start Time
                    </label>
                    <Input
                      type="time"
                      value={window.start_time}
                      onChange={(e) => updateHeatingWindow(index, 'start_time', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Duration (minutes)
                    </label>
                    <Input
                      type="number"
                      value={window.duration}
                      onChange={(e) => updateHeatingWindow(index, 'duration', parseInt(e.target.value))}
                      min="15"
                      max="180"
                      step="15"
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <label className="block text-sm font-medium mb-1">Days</label>
                    <div className="flex flex-wrap gap-2">
                      {daysOfWeek.map((day, dayIndex) => (
                        <button
                          key={dayIndex}
                          className={`px-2 py-1 rounded-md text-sm ${
                            window.days.includes(dayIndex)
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-200 text-gray-700'
                          }`}
                          onClick={() => {
                            const days = window.days.includes(dayIndex)
                              ? window.days.filter(d => d !== dayIndex)
                              : [...window.days, dayIndex];
                            updateHeatingWindow(index, 'days', days);
                          }}
                        >
                          {day.slice(0, 3)}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center mt-4">
                  <Switch
                    checked={window.enabled}
                    onCheckedChange={(checked) => updateHeatingWindow(index, 'enabled', checked)}
                  />
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => deleteHeatingWindow(index)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
            
            <Button
              variant="outline"
              onClick={addHeatingWindow}
              className="w-full"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Heating Window
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">System Settings</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Temperature Limits</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Minimum Temperature (°C)
                  </label>
                  <Input
                    type="number"
                    value={systemSettings.minTemp}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      minTemp: parseInt(e.target.value)
                    })}
                    min="45"
                    max="55"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Maximum Temperature (°C)
                  </label>
                  <Input
                    type="number"
                    value={systemSettings.maxTemp}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      maxTemp: parseInt(e.target.value)
                    })}
                    min="50"
                    max="65"
                  />
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-3">Rate Thresholds</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Cheap Rate Threshold (p/kWh)
                  </label>
                  <Input
                    type="number"
                    value={systemSettings.cheapRateThreshold}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      cheapRateThreshold: parseFloat(e.target.value)
                    })}
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Expensive Rate Threshold (p/kWh)
                  </label>
                  <Input
                    type="number"
                    value={systemSettings.expensiveRateThreshold}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      expensiveRateThreshold: parseFloat(e.target.value)
                    })}
                    step="0.1"
                  />
                </div>
              </div>
            </div>
            
            <div className="md:col-span-2">
              <h3 className="text-lg font-semibold mb-3">Peak Times</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Peak Start Time
                  </label>
                  <Input
                    type="time"
                    value={systemSettings.peakStartTime}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      peakStartTime: e.target.value
                    })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Peak End Time
                  </label>
                  <Input
                    type="time"
                    value={systemSettings.peakEndTime}
                    onChange={(e) => setSystemSettings({
                      ...systemSettings,
                      peakEndTime: e.target.value
                    })}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <Button onClick={saveSettings} className="w-full">
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
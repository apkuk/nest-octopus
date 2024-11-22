import { useState, useEffect } from 'react';
import { 
  LineChart, 
  AreaChart, 
  BarChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Card, Tabs, TabsContent, TabsList, TabsTrigger, Button } from '@/components/ui';
import { Download, TrendingUp, PoundSterling, Clock, Battery, Calendar } from 'lucide-react';

const Analytics = () => {
  const [timeframe, setTimeframe] = useState('week');
  const [data, setData] = useState({
    rates: [],
    usage: [],
    costs: [],
    patterns: [],
    dailyPatterns: []
  });
  const [summary, setSummary] = useState({
    totalSavings: 0,
    averageRate: 0,
    heatingDuration: 0,
    efficiency: 0
  });

  useEffect(() => {
    fetchAnalytics(timeframe);
  }, [timeframe]);

  const fetchAnalytics = async (period) => {
    try {
      const [rates, usage, costs, patterns, summary] = await Promise.all([
        fetch(`/api/rates/history?period=${period}`).then(r => r.json()),
        fetch(`/api/usage/history?period=${period}`).then(r => r.json()),
        fetch(`/api/costs/history?period=${period}`).then(r => r.json()),
        fetch(`/api/patterns/history?period=${period}`).then(r => r.json()),
        fetch(`/api/summary?period=${period}`).then(r => r.json())
      ]);
      
      setData({ rates, usage, costs, patterns });
      setSummary(summary);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const downloadData = async () => {
    try {
      const response = await fetch(`/api/export?period=${timeframe}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `smart-heating-data-${timeframe}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download data:', error);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="flex gap-4">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="rounded-lg border p-2"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </select>
          <Button onClick={downloadData} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Savings</p>
              <p className="text-2xl font-bold">£{summary.totalSavings.toFixed(2)}</p>
            </div>
            <PoundSterling className="w-6 h-6 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Average Rate</p>
              <p className="text-2xl font-bold">{summary.averageRate.toFixed(2)}p/kWh</p>
            </div>
            <TrendingUp className="w-6 h-6 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Heating Duration</p>
              <p className="text-2xl font-bold">{summary.heatingDuration}min</p>
            </div>
            <Clock className="w-6 h-6 text-orange-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Efficiency</p>
              <p className="text-2xl font-bold">{summary.efficiency}%</p>
            </div>
            <Battery className="w-6 h-6 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Main Charts */}
      <Tabs defaultValue="rates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="rates">Electricity Rates</TabsTrigger>
          <TabsTrigger value="usage">Usage Patterns</TabsTrigger>
          <TabsTrigger value="costs">Cost Analysis</TabsTrigger>
          <TabsTrigger value="patterns">Heating Patterns</TabsTrigger>
        </TabsList>

        <TabsContent value="rates">
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Electricity Rate Analysis</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={data.rates}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="rate" stroke="#8884d8" name="Rate (p/kWh)" />
                <Line type="monotone" dataKey="average" stroke="#82ca9d" name="Average Rate" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="usage">
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Daily Usage Patterns</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={data.usage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="duration" fill="#8884d8" name="Heating Duration (min)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="costs">
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Cost Comparison</h2>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={data.costs}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="actual" 
                  stackId="1" 
                  stroke="#82ca9d" 
                  fill="#82ca9d" 
                  name="Actual Cost"
                />
                <Area 
                  type="monotone" 
                  dataKey="potential" 
                  stackId="2" 
                  stroke="#8884d8" 
                  fill="#8884d8" 
                  name="Standard Rate Cost"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="patterns">
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Weekly Heating Patterns</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-md font-medium mb-3">Heating Duration by Day</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={data.patterns}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="duration" fill="#82ca9d" name="Duration (min)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div>
                <h3 className="text-md font-medium mb-3">Average Temperature</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={data.patterns}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="temp" stroke="#8884d8" name="Temperature (°C)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Additional Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-3">Peak Usage Times</h3>
          <div className="space-y-2">
            {data.dailyPatterns.map((pattern, index) => (
              <div key={index} className="flex justify-between items-center">
                <span>{pattern.timeSlot}</span>
                <div className="w-2/3 bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-blue-500 rounded-full h-4"
                    style={{ width: `${pattern.percentage}%` }}
                  />
                </div>
                <span>{pattern.percentage}%</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-3">Optimization Suggestions</h3>
          <ul className="space-y-2">
            {data.patterns.suggestions?.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <Calendar className="w-4 h-4 mr-2 mt-1" />
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;
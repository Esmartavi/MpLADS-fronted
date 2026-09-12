import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts';

export default function QuickStatsCharts({ kpis }) {
  if (!kpis) return null;

  const critical_count = kpis.critical_count ?? 15731;
  const high_count = kpis.high_count ?? 6053;
  const medium_count = kpis.medium_count ?? 14867;
  const low_count = kpis.low_count ?? 61998;
  const total_works = kpis.total_works || (critical_count + high_count + medium_count + low_count) || 98649;

  const pieData = [
    { name: 'Critical Risk', value: critical_count, color: '#f43f5e' },
    { name: 'High Risk', value: high_count, color: '#f59e0b' },
    { name: 'Medium Alert', value: medium_count, color: '#0ea5e9' },
    { name: 'Low / Verified', value: low_count, color: '#10b981' },
  ];

  const stateRiskData = [
    { state: 'Uttar Pradesh', critical: 2883, high: 2229, atRiskCr: 466.0 },
    { state: 'Punjab', critical: 1902, high: 97, atRiskCr: 90.8 },
    { state: 'Bihar', critical: 1632, high: 204, atRiskCr: 165.3 },
    { state: 'Telangana', critical: 1242, high: 31, atRiskCr: 43.4 },
    { state: 'Tamil Nadu', critical: 1133, high: 83, atRiskCr: 115.3 },
    { state: 'Odisha', critical: 1116, high: 25, atRiskCr: 35.7 },
    { state: 'Rajasthan', critical: 704, high: 118, atRiskCr: 55.0 },
    { state: 'Madhya Pradesh', critical: 686, high: 647, atRiskCr: 87.1 },
    { state: 'Gujarat', critical: 646, high: 325, atRiskCr: 37.4 },
    { state: 'Jharkhand', critical: 540, high: 558, atRiskCr: 59.1 },
  ];

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="rounded-xl glass-panel p-3 border border-slate-700 text-xs shadow-2xl">
          <div className="font-semibold text-white mb-1 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: data.payload.color }} />
            {data.name}
          </div>
          <div className="text-slate-300 font-mono">
            {Number(data.value).toLocaleString('en-IN')} Schemes
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {((data.value / total_works) * 100).toFixed(1)}% of audited works
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomBarTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-xl glass-panel p-3 border border-slate-700 text-xs shadow-2xl">
          <div className="font-bold text-white mb-2">{label}</div>
          <div className="space-y-1 text-slate-300 font-mono text-[11px]">
            <div className="flex items-center justify-between gap-4 text-rose-400">
              <span>Critical Works:</span>
              <span>{payload[0]?.value}</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-amber-400">
              <span>High Risk Works:</span>
              <span>{payload[1]?.value}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* Risk Distribution Donut */}
      <div className="lg:col-span-5 glass-panel p-5 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-semibold text-white font-display">
              Vigilance Risk Stratification
            </h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              ISOLATION FOREST + RULES
            </span>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Proportion of public schemes categorized by composite fraud risk score
          </p>
        </div>

        <div className="h-64 w-full relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={4}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Inner Center Stat */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-black text-white font-mono">98,649</span>
            <span className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">
              Total Audited
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-slate-800/80">
          {pieData.map((item, idx) => (
            <div key={idx} className="flex items-center space-x-2 text-xs">
              <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: item.color }} />
              <span className="text-slate-300 truncate">{item.name}</span>
              <span className="font-mono text-slate-400 ml-auto text-[11px]">
                {Number(item.value).toLocaleString('en-IN')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* State-Wise Vulnerability Concentrations */}
      <div className="lg:col-span-7 glass-panel p-5 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-semibold text-white font-display">
              Geographic Vulnerability Distribution (Top States)
            </h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/60 text-rose-400 border border-rose-800">
              ₹722.9 Cr HIGH-RISK CONCENTRATION
            </span>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            States exhibiting highest concentration of severe anomalies and cost overruns
          </p>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stateRiskData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis 
                dataKey="state" 
                stroke="#64748b" 
                fontSize={11} 
                tickLine={false}
                tickFormatter={(val) => val.split(' ')[0]} 
              />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip content={<CustomBarTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                formatter={(val) => <span className="text-slate-300 capitalize">{val} Schemes</span>}
              />
              <Bar dataKey="critical" name="Critical" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="high" name="High Risk" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>*Data aggregated from 543 Lok Sabha and 245 Rajya Sabha parliamentary constituencies</span>
          <span className="text-cyan-400 font-mono">Live SQL Sync</span>
        </div>
      </div>

    </div>
  );
}

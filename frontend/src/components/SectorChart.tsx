'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

interface SectorChartProps {
  data?: Record<string, number>;
}

export function SectorChart({ data }: SectorChartProps) {
  const chartData = data
    ? Object.entries(data).map(([sector, change]) => ({
        sector,
        change: Number(change),
      }))
    : [
        { sector: 'Auto & EV', change: 3.1 },
        { sector: 'Energy', change: 1.1 },
        { sector: 'Technology', change: 0.8 },
        { sector: 'Banking', change: 0.4 },
        { sector: 'FMCG', change: 0.2 },
        { sector: 'Pharma', change: -0.6 },
      ];

  return (
    <div className="w-full h-64 sm:h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <XAxis
            dataKey="sector"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(val) => `${val > 0 ? '+' : ''}${val}%`}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                const isPos = item.change >= 0;
                return (
                  <div className="bg-[#151923] border border-white/[0.1] px-3 py-2 rounded-lg text-xs shadow-xl font-mono">
                    <div className="text-slate-300 font-sans font-semibold mb-0.5">{item.sector}</div>
                    <div className={isPos ? 'text-[#00d09c]' : 'text-[#eb5b3c]'}>
                      {isPos ? '+' : ''}{item.change.toFixed(2)}% today
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <ReferenceLine y={0} stroke="#334155" strokeDasharray="3 3" />
          <Bar dataKey="change" radius={[4, 4, 4, 4]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.change >= 0 ? '#00d09c' : '#eb5b3c'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

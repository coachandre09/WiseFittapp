'use client'

import { useEffect, useState } from 'react'
import { AppShell } from '../components/AppShell'
import { MetricsCards } from '../components/MetricsCards'
import { apiFetch } from '../lib/api'
import { Bar, BarChart, CartesianGrid, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from 'recharts'

const colors = ['#d2ae6d','#886b25','#f3deb5','#8f8f8f','#525252']

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [days, setDays] = useState(30)
  const [source, setSource] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch(`/metrics/conversion/?days=${days}${source ? `&source=${encodeURIComponent(source)}` : ''}`).then(setMetrics).catch((e)=>setError(String(e)))
  }, [days, source])

  return <AppShell>
    <div className='mb-5 flex flex-wrap items-center gap-3'>
      <select className='input max-w-40' value={days} onChange={(e)=>setDays(Number(e.target.value))}><option value={14}>14 days</option><option value={30}>30 days</option><option value={90}>90 days</option></select>
      <input className='input max-w-60' placeholder='Filter by source...' value={source} onChange={(e)=>setSource(e.target.value)} />
    </div>
    {!metrics && !error && <div className='card p-10 animate-pulse'>Loading dashboard...</div>}
    {error && <div className='card p-6 text-red-400'>Failed to load: {error}</div>}
    {metrics && <>
      <MetricsCards metrics={metrics} />
      <div className='mt-5 grid gap-5 lg:grid-cols-2'>
        <div className='card p-5'><h3 className='mb-4 text-lg font-semibold'>Prospects per day</h3><div className='h-72'><ResponsiveContainer width='100%' height='100%'><BarChart data={metrics.timeseries}><CartesianGrid strokeDasharray='3 3' stroke='#222' /><XAxis dataKey='date' stroke='#999'/><YAxis stroke='#999'/><Tooltip /><Bar dataKey='count' fill='#d2ae6d' radius={[8,8,0,0]} /></BarChart></ResponsiveContainer></div></div>
        <div className='card p-5'><h3 className='mb-4 text-lg font-semibold'>Source breakdown</h3><div className='h-72'><ResponsiveContainer width='100%' height='100%'><PieChart><Pie data={metrics.by_source} dataKey='total' nameKey='source' outerRadius={95}>{(metrics.by_source||[]).map((_:any,i:number)=><Cell key={i} fill={colors[i%colors.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></div>
      </div>
    </>}
  </AppShell>
}

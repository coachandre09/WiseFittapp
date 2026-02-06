export function MetricsCards({ metrics }: { metrics: any }) {
  const items = [
    ['Total Prospects', metrics.total_prospects ?? 0],
    ['Converted', metrics.converted ?? 0],
    ['Conversion Rate', `${metrics.conversion_rate ?? 0}%`],
    ['New 7 days', metrics.new_prospects_7d ?? 0],
  ]
  return <div className='grid gap-4 sm:grid-cols-2 xl:grid-cols-4'>{items.map(([k,v]) => <div key={k} className='card p-5'><p className='text-xs text-white/70'>{k}</p><p className='mt-3 text-3xl font-semibold text-[#f3deb5]'>{String(v)}</p></div>)}</div>
}

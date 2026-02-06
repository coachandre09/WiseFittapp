'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { apiFetch } from '../../lib/api'

const stages = ['new','contacted','booked_consultation','attended','trial_started','converted','active_member','at_risk','churned']

export default function ProspectsPage() {
  const [data, setData] = useState<any[]>([])
  const [q, setQ] = useState('')
  const [stage, setStage] = useState('')
  const [source, setSource] = useState('')
  const [error, setError] = useState('')

  const query = useMemo(()=>`?q=${encodeURIComponent(q)}${stage?`&stages=${stage}`:''}${source?`&sources=${source}`:''}`,[q,stage,source])
  useEffect(()=>{ apiFetch<any[]>(`/leads/${query}`).then(setData).catch((e)=>setError(String(e))) },[query])

  async function addProspect(){
    const full_name = prompt('Prospect name')
    if(!full_name) return
    await apiFetch('/leads/', {method:'POST', body: JSON.stringify({full_name, source: 'Manual', stage: 'new'})})
    const refreshed = await apiFetch<any[]>(`/leads/${query}`)
    setData(refreshed)
  }

  async function convert(id:number){
    if(!confirm('Convert this prospect to member?')) return
    await apiFetch(`/leads/${id}/convert/`, {method:'POST'})
    const refreshed = await apiFetch<any[]>(`/leads/${query}`)
    setData(refreshed)
  }

  async function markLost(id:number){
    const lost_reason = prompt('Lost reason') || ''
    await apiFetch(`/leads/${id}/mark_lost/`, {method:'POST', body: JSON.stringify({lost_reason})})
    const refreshed = await apiFetch<any[]>(`/leads/${query}`)
    setData(refreshed)
  }

  return <AppShell>
    <div className='mb-4 flex flex-wrap gap-3'>
      <input className='input max-w-64' placeholder='Search name/email/phone' value={q} onChange={(e)=>setQ(e.target.value)} />
      <select className='input max-w-52' value={stage} onChange={(e)=>setStage(e.target.value)}><option value=''>All stages</option>{stages.map(s=><option key={s} value={s}>{s}</option>)}</select>
      <input className='input max-w-52' placeholder='Source' value={source} onChange={(e)=>setSource(e.target.value)} />
      <button className='btn-primary' onClick={addProspect}>Add Prospect</button>
    </div>
    {error && <div className='card p-4 text-red-400 mb-3'>{error}</div>}
    <div className='card overflow-hidden'>
      <table className='w-full text-sm'>
        <thead className='bg-white/5 text-left text-white/70'><tr><th className='p-3'>Name</th><th>Phone</th><th>Email</th><th>Source</th><th>Stage</th><th>Created</th><th>Converted?</th><th className='p-3'>Actions</th></tr></thead>
        <tbody>{data.map((r)=><tr key={r.id} className='border-t border-white/5 hover:bg-white/5'><td className='p-3'><Link href={`/prospects/${r.id}`} className='text-[#f3deb5] hover:underline'>{r.full_name}</Link></td><td>{r.phone || '-'}</td><td>{r.email || '-'}</td><td>{r.source || '-'}</td><td><span className='badge-gold'>{r.stage}</span></td><td>{new Date(r.created_at).toLocaleDateString()}</td><td>{r.converted_member ? 'Yes':'No'}</td><td className='p-3 space-x-2'><button className='btn-secondary' onClick={()=>convert(r.id)}>Convert</button><button className='btn-secondary' onClick={()=>markLost(r.id)}>Mark Lost</button></td></tr>)}</tbody>
      </table>
      {!data.length && <div className='p-12 text-center text-white/50'>No prospects found.</div>}
    </div>
  </AppShell>
}

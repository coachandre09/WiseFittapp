'use client'

import { useEffect, useMemo, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { apiFetch } from '../../lib/api'

export default function MembersPage(){
  const [data, setData] = useState<any[]>([])
  const [q, setQ] = useState('')

  useEffect(()=>{ apiFetch<any[]>('/members-overview/').then(setData).catch(()=>setData([])) },[])
  const filtered = useMemo(()=>data.filter(x=>`${x.name} ${x.email} ${x.phone}`.toLowerCase().includes(q.toLowerCase())),[data,q])

  return <AppShell>
    <div className='mb-4'><input className='input max-w-72' placeholder='Search members' value={q} onChange={e=>setQ(e.target.value)} /></div>
    <div className='card overflow-hidden'>
      <table className='w-full text-sm'>
        <thead className='bg-white/5 text-left text-white/70'><tr><th className='p-3'>Name</th><th>Email</th><th>Phone</th><th>Active Membership</th><th>Package</th><th>Start</th></tr></thead>
        <tbody>{filtered.map((m)=> <tr key={m.id} className='border-t border-white/5'><td className='p-3 text-[#f3deb5]'>{m.name}</td><td>{m.email || '-'}</td><td>{m.phone || '-'}</td><td>{m.active_membership ? 'Yes':'No'}</td><td>{m.package}</td><td>{m.start_date || '-'}</td></tr>)}</tbody>
      </table>
      {!filtered.length && <div className='p-12 text-center text-white/50'>No members found.</div>}
    </div>
  </AppShell>
}

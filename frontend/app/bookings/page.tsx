'use client'

import { useEffect, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { apiFetch } from '../../lib/api'

export default function TrainingPlannerPage() {
  const [members, setMembers] = useState<any[]>([])
  const [memberId, setMemberId] = useState<number | ''>('')
  const [block, setBlock] = useState<any[]>([])

  useEffect(() => {
    apiFetch<any[]>('/members-overview/').then((m) => {
      setMembers(m)
      if (m.length) setMemberId(m[0].id)
    })
  }, [])

  useEffect(() => {
    if (!memberId) return
    apiFetch<any>(`/mobility/members/${memberId}/block/`).then((d) => setBlock(d.mobility_block || []))
  }, [memberId])

  return <AppShell>
    <h2 className='mb-4 text-2xl font-semibold text-[#f3deb5]'>Training Program Builder</h2>
    <div className='card p-5'>
      <label className='text-sm text-white/70'>Select member</label>
      <select className='input mt-2 max-w-sm' value={memberId} onChange={(e)=>setMemberId(Number(e.target.value))}>
        {members.map((m)=><option value={m.id} key={m.id}>{m.name}</option>)}
      </select>

      <div className='mt-6 grid gap-4 lg:grid-cols-2'>
        <div className='rounded-2xl border border-white/10 bg-white/5 p-4'>
          <h3 className='mb-2 font-semibold'>Main Program Block</h3>
          <ul className='list-disc pl-5 text-sm text-white/80'>
            <li>Strength: Squat 5x5</li>
            <li>Conditioning: EMOM 12</li>
            <li>Accessory: Core 3 rounds</li>
          </ul>
        </div>
        <div className='rounded-2xl border border-[#d2ae6d]/30 bg-[#d2ae6d]/10 p-4'>
          <h3 className='mb-2 font-semibold text-[#f3deb5]'>Mobility Block (auto from latest plan)</h3>
          {!block.length && <p className='text-sm text-white/70'>No mobility plan available for this member.</p>}
          <ul className='space-y-2'>
            {block.map((b, idx)=> <li key={idx} className='rounded-xl bg-black/30 p-3 text-sm'>
              <div className='font-medium'>{b.exercise}</div>
              <div className='text-white/80'>{b.sets} sets • {b.reps_or_time} • {b.frequency_per_week}x/week</div>
            </li>)}
          </ul>
        </div>
      </div>
    </div>
  </AppShell>
}

'use client'

import { useEffect, useState } from 'react'
import { AppShell } from '../../../components/AppShell'
import { apiFetch } from '../../../lib/api'

export default function ProspectDetail({ params }: { params: { id: string } }) {
  const id = params.id
  const [lead, setLead] = useState<any>(null)
  const [activities, setActivities] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])
  const [note, setNote] = useState('')

  async function load(){
    const l = await apiFetch<any>(`/leads/${id}/`)
    setLead(l)
    setActivities((await apiFetch<any[]>('/lead-activities/')).filter(a=>a.lead===l.id))
    setTasks((await apiFetch<any[]>('/lead-tasks/')).filter(t=>t.lead===l.id))
  }
  useEffect(()=>{load()},[id])

  async function saveLead(){
    const updated = await apiFetch<any>(`/leads/${id}/`, {method:'PATCH', body: JSON.stringify(lead)})
    setLead(updated)
  }

  async function addActivity(){
    if(!note) return
    await apiFetch('/lead-activities/', {method:'POST', body: JSON.stringify({lead: Number(id), activity_type:'note', content: note})})
    setNote('')
    load()
  }

  async function addTask(){
    const title = prompt('Task title')
    if(!title) return
    const due = new Date().toISOString().slice(0,10)
    await apiFetch('/lead-tasks/', {method:'POST', body: JSON.stringify({lead: Number(id), title, due_date: due})})
    load()
  }

  async function convert(){
    await apiFetch(`/leads/${id}/convert/`, {method:'POST'})
    load()
  }

  if(!lead) return <AppShell><div className='card p-10 animate-pulse'>Loading prospect...</div></AppShell>

  return <AppShell>
    <div className='card p-5'>
      <div className='flex items-center justify-between'><h2 className='text-2xl font-semibold text-[#f3deb5]'>{lead.full_name}</h2><span className='badge-gold'>{lead.stage}</span></div>
      <div className='mt-4 grid gap-3 md:grid-cols-2'>
        <input className='input' value={lead.full_name || ''} onChange={e=>setLead({...lead, full_name:e.target.value})} />
        <input className='input' value={lead.email || ''} onChange={e=>setLead({...lead, email:e.target.value})} />
        <input className='input' value={lead.phone || ''} onChange={e=>setLead({...lead, phone:e.target.value})} />
        <input className='input' value={lead.source || ''} onChange={e=>setLead({...lead, source:e.target.value})} />
        <textarea className='input md:col-span-2' value={lead.notes || ''} onChange={e=>setLead({...lead, notes:e.target.value})} placeholder='Notes' />
      </div>
      <div className='mt-4 flex gap-2'><button className='btn-primary' onClick={saveLead}>Save</button><button className='btn-secondary' onClick={convert}>Convert to Member</button></div>
    </div>

    <div className='mt-5 grid gap-5 lg:grid-cols-2'>
      <div className='card p-5'><h3 className='mb-3 text-lg font-semibold'>Activities</h3><div className='space-y-2'>{activities.map(a=><div key={a.id} className='rounded-xl bg-white/5 p-3 text-sm'>{a.content || a.activity_type}</div>)}</div><div className='mt-3 flex gap-2'><input className='input' value={note} onChange={e=>setNote(e.target.value)} placeholder='Add activity note' /><button className='btn-secondary' onClick={addActivity}>Add</button></div></div>
      <div className='card p-5'><h3 className='mb-3 text-lg font-semibold'>Tasks</h3><div className='space-y-2'>{tasks.map(t=><div key={t.id} className='rounded-xl bg-white/5 p-3 text-sm'>{t.title}</div>)}</div><button className='btn-secondary mt-3' onClick={addTask}>Create Task</button></div>
    </div>
  </AppShell>
}

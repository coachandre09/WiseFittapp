'use client'

import { useEffect, useMemo, useState } from 'react'
import { AppShell } from '../../../components/AppShell'
import { apiFetch } from '../../../lib/api'

const today = new Date().toISOString().slice(0, 10)

export default function MemberMobilityPage({ params }: { params: { id: string } }) {
  const memberId = Number(params.id)
  const [member, setMember] = useState<any>(null)
  const [latest, setLatest] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState<any>({
    member: memberId,
    assessed_on: today,
    pain_flag: false,
    ankle_left_score: 2,
    ankle_right_score: 2,
    aslr_left_score: 2,
    aslr_right_score: 2,
    shoulder_left_score: 2,
    shoulder_right_score: 2,
    overhead_squat_score: 2,
    wall_angels_score: 2,
    notes: '',
  })

  async function load() {
    const members = await apiFetch<any[]>('/members-overview/')
    setMember(members.find((m) => m.id === memberId))
    const l = await apiFetch<any>(`/mobility/members/${memberId}/latest/`)
    setLatest(l)
  }

  useEffect(() => {
    load().catch((e) => setError(String(e)))
  }, [memberId])

  const computed = useMemo(() => ({
    ankle_final: Math.min(Number(form.ankle_left_score), Number(form.ankle_right_score)),
    aslr_final: Math.min(Number(form.aslr_left_score), Number(form.aslr_right_score)),
    shoulder_final: Math.min(Number(form.shoulder_left_score), Number(form.shoulder_right_score)),
  }), [form])

  async function saveAssessment() {
    setLoading(true)
    setError('')
    try {
      await apiFetch('/mobility/assessments/', {
        method: 'POST',
        body: JSON.stringify({ ...form, ...computed }),
      })
      await load()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function generatePlan() {
    if (!latest?.assessment?.id) return
    setLoading(true)
    try {
      await apiFetch(`/mobility/assessments/${latest.assessment.id}/generate-plan/`, { method: 'POST' })
      await load()
    } finally {
      setLoading(false)
    }
  }

  return <AppShell>
    <div className='mb-4 flex items-center justify-between'>
      <h2 className='text-2xl font-semibold text-[#f3deb5]'>Mobility • {member?.name || `Member ${memberId}`}</h2>
      <span className='badge-gold'>Protocol: barefoot / no warm-up / pain-free</span>
    </div>

    {error && <div className='card p-4 text-red-400 mb-4'>{error}</div>}

    <div className='grid gap-5 lg:grid-cols-2'>
      <div className='card p-5'>
        <h3 className='mb-4 text-lg font-semibold'>New Mobility Assessment</h3>
        <div className='grid grid-cols-2 gap-3'>
          {[
            ['Ankle Left', 'ankle_left_score'], ['Ankle Right', 'ankle_right_score'],
            ['ASLR Left', 'aslr_left_score'], ['ASLR Right', 'aslr_right_score'],
            ['Shoulder Left', 'shoulder_left_score'], ['Shoulder Right', 'shoulder_right_score'],
            ['Overhead Squat', 'overhead_squat_score'], ['Wall Angels', 'wall_angels_score'],
          ].map(([label, key]) => (
            <label key={key} className='text-sm'>
              <span className='mb-1 block text-white/70'>{label}</span>
              <select className='input' value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}>
                <option value={1}>1</option><option value={2}>2</option><option value={3}>3</option>
              </select>
            </label>
          ))}
          <label className='col-span-2 text-sm flex items-center gap-2 pt-2'>
            <input type='checkbox' checked={form.pain_flag} onChange={(e) => setForm({ ...form, pain_flag: e.target.checked })} />
            Pain present (auto score 1)
          </label>
          <textarea className='input col-span-2' placeholder='Notes' value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
        <div className='mt-3 text-sm text-white/70'>Computed finals — Ankle: <b>{computed.ankle_final}</b>, ASLR: <b>{computed.aslr_final}</b>, Shoulder: <b>{computed.shoulder_final}</b></div>
        <button className='btn-primary mt-4' onClick={saveAssessment} disabled={loading}>{loading ? 'Saving...' : 'Save Assessment'}</button>
      </div>

      <div className='card p-5'>
        <h3 className='mb-4 text-lg font-semibold'>Latest Results & Plan</h3>
        {!latest?.assessment && <p className='text-white/60'>No assessment yet.</p>}
        {latest?.assessment && (
          <>
            <div className='grid grid-cols-2 gap-3 text-sm'>
              <div className='rounded-xl bg-white/5 p-3'>Ankle final: <b>{latest.assessment.ankle_final_score}</b></div>
              <div className='rounded-xl bg-white/5 p-3'>ASLR final: <b>{latest.assessment.aslr_final_score}</b></div>
              <div className='rounded-xl bg-white/5 p-3'>Shoulder final: <b>{latest.assessment.shoulder_final_score}</b></div>
              <div className='rounded-xl bg-white/5 p-3'>Wall Angels: <b>{latest.assessment.wall_angels_score}</b></div>
            </div>
            <button className='btn-secondary mt-4' onClick={generatePlan}>Generate Mobility Plan</button>
          </>
        )}

        <div className='mt-5'>
          <h4 className='mb-2 text-[#f3deb5]'>Current plan</h4>
          {!latest?.plan?.items?.length && <p className='text-white/60'>No active mobility plan.</p>}
          <div className='space-y-2'>
            {(latest?.plan?.items || []).map((i: any) => (
              <div key={i.id} className='rounded-xl bg-white/5 p-3 text-sm'>
                <div className='font-medium text-[#f3deb5]'>{i.exercise_name}</div>
                <div>{i.sets} sets • {i.reps_or_time} • {i.frequency_per_week}x/week</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  </AppShell>
}

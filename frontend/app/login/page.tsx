'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { z } from 'zod'
import { API_BASE } from '../../lib/api'
import { authStore } from '../../lib/auth'

const schema = z.object({ username: z.string().min(1), password: z.string().min(1) })

export default function LoginPage() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin1234')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const parsed = schema.safeParse({ username, password })
    if (!parsed.success) return setError('Please provide username and password')
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE}/auth/token/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) })
      if (!res.ok) throw new Error('Invalid credentials')
      const data = await res.json()
      authStore.setTokens(data)
      router.push('/')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return <div className='mx-auto mt-20 max-w-md card p-8'>
    <h1 className='text-3xl font-semibold text-[#f3deb5]'>Welcome back</h1>
    <p className='mt-2 text-white/70'>Sign in to WiseFitt CRM</p>
    <form className='mt-6 space-y-4' onSubmit={submit}>
      <input className='input' value={username} onChange={(e)=>setUsername(e.target.value)} placeholder='Username' />
      <input className='input' value={password} onChange={(e)=>setPassword(e.target.value)} placeholder='Password' type='password' />
      {error && <p className='text-sm text-red-400'>{error}</p>}
      <button className='btn-primary w-full' disabled={loading}>{loading ? 'Signing in...' : 'Login'}</button>
    </form>
  </div>
}

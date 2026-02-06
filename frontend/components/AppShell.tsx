'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { authStore } from '../lib/auth'

const nav = [
  ['/', 'Dashboard'],
  ['/prospects', 'Prospects'],
  ['/members', 'Members'],
  ['/tv/sgpt', 'SGPT TV'],
  ['/tv/functional', 'Functional TV'],
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const p = usePathname()
  const r = useRouter()
  return (
    <div className='min-h-screen md:grid md:grid-cols-[240px_1fr]'>
      <aside className='border-r border-white/10 bg-black/50 p-4'>
        <div className='mb-6 text-xl font-semibold tracking-wide text-[#f3deb5]'>WiseFitt</div>
        <nav className='space-y-2'>
          {nav.map(([href, label]) => (
            <Link key={href} href={href} className={`block rounded-xl px-3 py-2 text-sm transition ${p === href ? 'bg-[#d2ae6d]/20 text-[#f3deb5]' : 'hover:bg-white/5'}`}>
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <section>
        <header className='sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-black/40 px-4 py-3 backdrop-blur'>
          <h1 className='text-sm text-white/80'>Premium CRM</h1>
          <button className='btn-secondary' onClick={() => { authStore.clear(); r.push('/login') }}>Logout</button>
        </header>
        <main className='p-4 md:p-6'>{children}</main>
      </section>
    </div>
  )
}

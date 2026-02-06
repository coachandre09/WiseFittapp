'use client'

import { useEffect, useState } from 'react'
import { apiFetch } from '../../../lib/api'

export default function Page(){
  const [data, setData] = useState<any>(null)
  useEffect(()=>{ apiFetch('/screens/functional/', undefined, false).then(setData) },[])
  return <div className='p-8'><h1 className='text-4xl font-bold text-[#f3deb5] mb-5'>Functional Room Screen</h1><pre className='card p-5 overflow-auto'>{JSON.stringify(data,null,2)}</pre></div>
}

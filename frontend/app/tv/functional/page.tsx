import { fetchJson } from '../../../lib/api'

export default async function Page(){
  const data = await fetchJson('/screens/functional/');
  return <div><h1 className='text-3xl font-bold mb-4'>Functional Room Screen</h1><pre className='bg-slate-900 p-4 rounded-xl overflow-auto'>{JSON.stringify(data,null,2)}</pre></div>
}

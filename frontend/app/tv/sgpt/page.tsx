import { fetchJson } from '../../../lib/api'

export default async function Page(){
  const data = await fetchJson('/screens/sgpt/');
  return <div><h1 className='text-3xl font-bold mb-4'>SGPT Room Screen</h1><pre className='bg-slate-900 p-4 rounded-xl overflow-auto'>{JSON.stringify(data,null,2)}</pre></div>
}

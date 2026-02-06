export default function Page(){return <div className='grid md:grid-cols-2 gap-4'><Card t='Bookings & Sessions'/><Card t='CRM & Leads'/><Card t='Finance Dashboard'/><Card t='Treatments'/></div>}
function Card({t}:{t:string}){return <div className='bg-slate-800 p-6 rounded-xl'>{t}</div>}

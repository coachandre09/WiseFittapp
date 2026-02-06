import './globals.css'
import Link from 'next/link'

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html><body><nav className='p-4 flex gap-4 bg-slate-900'><Link href='/'>Dashboard</Link><Link href='/tv/sgpt'>SGPT TV</Link><Link href='/tv/functional'>Functional TV</Link></nav><main className='p-4'>{children}</main></body></html>
}

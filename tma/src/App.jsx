import React, { useEffect, useMemo, useState } from 'react'
import { retrieveLaunchParams } from '@telegram-apps/sdk'

export default function App() {
  const [status, setStatus] = useState('')

  const lp = useMemo(() => {
    try {
      return retrieveLaunchParams()
    } catch (e) {
      return null
    }
  }, [])

  const tg = lp?.initDataUnsafe
  const tgUser = tg?.user
  const refCode = tg?.start_param || 'direct'

  useEffect(() => {
    if (window?.Telegram?.WebApp) {
      try {
        window.Telegram.WebApp.ready()
      } catch {}
    }
  }, [])

  async function onActivate() {
    setStatus('Активация...')
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    try {
      const res = await fetch(`${apiUrl}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tg_id: tgUser?.id,
          ref_code: refCode,
        }),
      })
      const data = await res.json()
      if (!res.ok || !data?.ok) throw new Error(data?.detail || 'Activation failed')
      setStatus('Триал активирован!')
    } catch (err) {
      setStatus(`Ошибка: ${err.message}`)
    }
  }

  return (
    <div style={{ fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial', padding: 24 }}>
      <h1 style={{ margin: '0 0 8px' }}>Активируй 3-дневный триал</h1>
      <p style={{ margin: '0 0 16px', opacity: 0.85 }}>Подключи аккаунт и установи BIO для активации</p>
      <button onClick={onActivate} style={{ padding: '10px 16px', borderRadius: 8, border: 'none', background: '#2481cc', color: '#fff', cursor: 'pointer' }}>
        Подключить Telegram
      </button>
      <div style={{ marginTop: 16, minHeight: 20 }}>{status}</div>
    </div>
  )
}

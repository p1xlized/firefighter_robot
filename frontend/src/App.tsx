
import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type Command = 'F' | 'B' | 'L' | 'R' | 'S'

async function sendCommand(command: Command): Promise<void> {
  const response = await fetch(`${API_URL}/robot/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(error?.detail ?? 'Could not control the robot')
  }
}

function App() {
  const [status, setStatus] = useState('Ready')

  const control = (command: Command) => {
    void sendCommand(command)
      .then(() => setStatus(`Command ${command} sent`))
      .catch((error: unknown) => {
        setStatus(error instanceof Error ? error.message : 'Connection failed')
      })
  }

  useEffect(() => {
    const stop = () => control('S')
    window.addEventListener('blur', stop)
    return () => window.removeEventListener('blur', stop)
  })

  const movementButton = (
    label: string,
    command: Exclude<Command, 'S'>,
  ) => (
    <button
      type="button"
      onPointerDown={() => control(command)}
      onPointerUp={() => control('S')}
      onPointerLeave={() => control('S')}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') control(command)
      }}
    >
      {label}
    </button>
  )

  return (
    <main style={styles.page}>
      <h1>Firefighter Robot</h1>
      <p style={styles.status}>{status}</p>

      <section style={styles.layout}>
        <div style={styles.card}>
          <h2>Live feed</h2>
          <img
            src={`${API_URL}/video_feed`}
            alt="Live camera feed from the firefighter robot"
            style={styles.feed}
          />
        </div>

        <div style={styles.card}>
          <h2>Robot control</h2>
          <div style={styles.controls}>
            <span />
            {movementButton('Forward', 'F')}
            <span />
            {movementButton('Left', 'L')}
            <button type="button" onClick={() => control('S')}>
              Stop
            </button>
            {movementButton('Right', 'R')}
            <span />
            {movementButton('Backward', 'B')}
            <span />
          </div>
          <p>Hold a direction button to move. Release it to stop.</p>
        </div>
      </section>
    </main>
  )
}

const styles = {
  page: {
    maxWidth: 1100,
    margin: '0 auto',
    padding: 24,
    fontFamily: 'system-ui, sans-serif',
  },
  status: {
    minHeight: 24,
  },
  layout: {
    display: 'grid',
    gridTemplateColumns: 'minmax(0, 2fr) minmax(260px, 1fr)',
    gap: 24,
  },
  card: {
    padding: 20,
    border: '1px solid #ddd',
    borderRadius: 12,
  },
  feed: {
    display: 'block',
    width: '100%',
    minHeight: 240,
    objectFit: 'cover' as const,
    background: '#111',
    borderRadius: 8,
  },
  controls: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 12,
    margin: '32px 0',
  },
} as const

export default App

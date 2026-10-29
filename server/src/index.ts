import { Elysia } from 'elysia'
import { node } from '@elysia/node'

const mediaMtxUrl = 'http://10.143.21.7:8889/camera'

const app = new Elysia({ adapter: node() })
	.get('/', () => 'Firefighter robot server')
	.get('/video-feed', () => new Response(`<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Firefighter robot video</title>
    <style>
      body { margin: 0; padding: 2rem; background: #111; color: #fff;
        font: 1rem system-ui, sans-serif; text-align: center; }
      iframe { width: min(100%, 960px); height: min(70vh, 540px);
        border: 0; border-radius: 8px; background: #000; }
    </style>
  </head>
  <body>
    <h1>Firefighter robot video</h1>
    <iframe src="${mediaMtxUrl}" allow="autoplay; fullscreen" allowfullscreen
      title="Raspberry Pi camera stream"></iframe>
  </body>
</html>`, {
		headers: { 'content-type': 'text/html; charset=utf-8' },
	}))
	.listen(3000, ({ hostname, port }) => {
		console.log(
			`🦊 Elysia is running at ${hostname}:${port}`
		)
	})

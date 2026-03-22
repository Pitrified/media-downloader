# Using the HTTP API

`media-downloader` exposes a FastAPI server with two usage patterns: a synchronous endpoint that blocks until the download completes, and an asynchronous job queue for fire-and-forget use cases.

## Starting the server

```bash
# Development (auto-reload on file changes)
uvicorn media_downloader.webapp.app:app --reload

# Production
uvicorn media_downloader.webapp.app:app --host 0.0.0.0 --port 8000
```

The server reads configuration from environment variables (or `~/cred/media-downloader/.env`). Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Health check

```
GET /health
```

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## Synchronous download

`POST /download` downloads the URL immediately and returns the result in the response body. The request blocks until the download (and any transcription) is complete.

**Request body:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | required | The URL to download |
| `download_video` | bool | `true` | Whether to download video (respected by yt-dlp and instaloader) |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Detected source type (`youtube`, `instagram`, `tiktok`, `web_recipe`) |
| `source_id` | string | Platform-specific content ID |
| `files` | list[string] | Absolute paths to downloaded files |
| `caption` | string | Description or caption from the source |
| `transcript` | string \| null | Transcription text, if enabled |
| `language` | string \| null | Detected language code |

### Example - YouTube

```bash
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

```json
{
  "source": "youtube",
  "source_id": "dQw4w9WgXcQ",
  "files": [
    "/data/media/youtube/dQw4w9WgXcQ/video.mp4",
    "/data/media/youtube/dQw4w9WgXcQ/video.jpg"
  ],
  "caption": "Rick Astley - Never Gonna Give You Up",
  "transcript": null,
  "language": null
}
```

### Example - Web recipe

```bash
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/"}'
```

### Example with Python `httpx`

```python
import httpx

BASE_URL = "http://localhost:8000"

response = httpx.post(
    f"{BASE_URL}/download",
    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
)
response.raise_for_status()
result = response.json()
print(result["source"])     # "youtube"
print(result["files"])      # list of file paths
print(result["transcript"]) # None if transcription not configured
```

---

## Asynchronous job queue

For long-running downloads, use the two-step job queue: submit with `POST /jobs`, then poll with `GET /jobs/{id}`.

### Submit a job

```
POST /jobs
```

**Request body:** same as `POST /download`

**Response:** `201 Created`

```json
{
  "id": "3f2d1a9b-4e8c-4f0d-a1b2-c3d4e5f6a7b8",
  "url": "https://www.youtube.com/watch?v=...",
  "source": "",
  "source_id": "",
  "status": "pending",
  "error": null,
  "created_at": "2026-03-22T10:00:00Z",
  "updated_at": "2026-03-22T10:00:00Z",
  "transcript": null,
  "language": null,
  "media_files": []
}
```

### Poll job status

```
GET /jobs/{job_id}
```

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Job identifier |
| `status` | string | `pending`, `running`, `completed`, or `failed` |
| `source` | string | Detected source type |
| `source_id` | string | Platform-specific content ID |
| `error` | string \| null | Error message if `status == "failed"` |
| `transcript` | string \| null | Transcription text when completed |
| `language` | string \| null | Detected language code |
| `media_files` | list | Files persisted to disk |

### Full polling example in Python

```python
import time
import httpx

BASE_URL = "http://localhost:8000"

# Step 1 - submit the job
resp = httpx.post(
    f"{BASE_URL}/jobs",
    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
)
resp.raise_for_status()
job_id = resp.json()["id"]
print(f"Submitted job {job_id}")

# Step 2 - poll until done
while True:
    resp = httpx.get(f"{BASE_URL}/jobs/{job_id}")
    resp.raise_for_status()
    job = resp.json()

    status = job["status"]
    print(f"  Status: {status}")

    if status == "completed":
        print(f"  Files: {[f['file_path'] for f in job['media_files']]}")
        print(f"  Transcript: {job['transcript']}")
        break

    if status == "failed":
        print(f"  Error: {job['error']}")
        break

    time.sleep(5)  # wait before next poll
```

### Async polling with httpx

```python
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def download_and_wait(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}/jobs", json={"url": url})
        resp.raise_for_status()
        job_id = resp.json()["id"]

        while True:
            resp = await client.get(f"{BASE_URL}/jobs/{job_id}")
            job = resp.json()
            if job["status"] in ("completed", "failed"):
                return job
            await asyncio.sleep(3)

result = asyncio.run(download_and_wait("https://www.youtube.com/watch?v=..."))
```

---

## Error responses

| Status | When |
|--------|------|
| `400 Bad Request` | URL source is not supported, or the provider rejected the URL |
| `404 Not Found` | `GET /jobs/{id}` with an unknown job ID |
| `500 Internal Server Error` | Unexpected error during download |

Error body:
```json
{"detail": "No downloader registered for source: unknown"}
```

---

## Interactive docs

When running in development mode, full Swagger UI and ReDoc are available:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

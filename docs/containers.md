# Containerised programs and 3D rendering

You send your own program (a Docker image) and your files. NEURAX splits the job into tasks; every
task is executed by **two nodes of two different partners** and is paid only if the results match.
If they do not match the task goes to a third node; without agreement it fails and is refunded.

## Isolation on the node
No network, no privileges, read-only system files, unprivileged user, limits on CPU, memory,
processes and time. Inputs read-only in `/in`, outputs in `/out`.
In the standard tier data can be read by the partner that processes it: encrypt or anonymise
sensitive data, or use `"confidential": true` or the Sovereign Tier.

## Large files (up to 20 GB)
| Call | What it does |
|---|---|
| `POST /v1/uploads` `{"name","size"}` | opens an upload → `upload_id`, `chunk_size` (50 MB), `chunks` |
| `PUT /v1/uploads/{id}/{n}` | sends chunk `n` (from 0), binary body |
| `GET /v1/uploads/{id}` | chunks already received, to resume after an interruption |
| `POST /v1/uploads/{id}/complete` | closes the upload and returns `{name, sha256, size}` |

Abandoned uploads are deleted after 24 hours.

## Container job: `POST /v1/jobs/container`
| Field | Meaning |
|---|---|
| `image` | public Docker image |
| `command` | command, as a list of arguments |
| `tasks` | optional: one command per task, run in parallel |
| `inputs` | uploaded files, `[{name, sha256, size}]` |
| `cpus`, `mem_mb`, `timeout_s` | resources per task |
| `match` | `exact` (identical files) or `image` (images with PSNR ≥ 35 dB) |
| `max_output_mb`, `env`, `label` | optional |
| `region`, `sovereign`, `confidential` | boundaries |

## Rendering: `POST /v1/jobs/render`
`file` (the uploaded `.blend` scene), `frame_start`, `frame_end`, `frames_per_task`, `engine`
(`CYCLES`, `BLENDER_EEVEE_NEXT`, `BLENDER_WORKBENCH`), `cpus`, `mem_mb`, `minutes_per_frame`, `label` and the boundaries.
Blender 4.2, CPU only.

## Price
Reserved in advance: CPUs × maximum time × price per CPU-hour × 2 executions.
Charged at the end of each task for the actual time; the rest goes back to your credit.

## Results
`GET /v1/jobs/{id}/result` lists the files produced; `GET /v1/files/{sha256}` downloads them;
`GET /v1/batches/{batch}/zip`, with the `batch` value of the result, downloads the whole job as one ZIP.

# Programmi in contenitore e rendering 3D

Invii il tuo programma (un'immagine Docker) e i tuoi file. NEURAX divide il lavoro in compiti; ogni
compito viene eseguito da **due nodi di partner diversi** e viene pagato solo se i risultati coincidono.
Se non coincidono, il compito passa a un terzo nodo; senza accordo, fallisce ed è rimborsato.

## Isolamento sul nodo
Senza rete, senza privilegi, file di sistema in sola lettura, utente non privilegiato, limiti di CPU,
memoria, processi e tempo. Ingressi in sola lettura in `/in`, uscite in `/out`.
Nel livello standard i dati sono leggibili dal partner che li elabora: cifra o anonimizza i dati
sensibili, oppure usa `"confidential": true` o il Livello Sovrano.

## File grandi (fino a 20 GB)
| Chiamata | Che cosa fa |
|---|---|
| `POST /v1/uploads` `{"name","size"}` | apre un caricamento → `upload_id`, `chunk_size` (50 MB), `chunks` |
| `PUT /v1/uploads/{id}/{n}` | invia il pezzo `n` (da 0), corpo binario |
| `GET /v1/uploads/{id}` | pezzi già ricevuti, per riprendere dopo un'interruzione |
| `POST /v1/uploads/{id}/complete` | chiude e restituisce `{name, sha256, size}` |

I caricamenti abbandonati vengono cancellati dopo 24 ore.

## Lavoro in contenitore: `POST /v1/jobs/container`
| Campo | Significato |
|---|---|
| `image` | immagine Docker pubblica |
| `command` | comando, come lista di argomenti |
| `tasks` | facoltativo: un comando per compito, eseguiti in parallelo |
| `inputs` | file caricati, `[{name, sha256, size}]` |
| `cpus`, `mem_mb`, `timeout_s` | risorse per compito |
| `match` | `exact` (stessi file) o `image` (immagini con PSNR ≥ 35 dB) |
| `max_output_mb`, `env`, `label` | facoltativi |
| `region`, `sovereign`, `confidential` | confini |

## Rendering: `POST /v1/jobs/render`
`file` (la scena `.blend` caricata), `frame_start`, `frame_end`, `frames_per_task`, `engine`
(`CYCLES`, `BLENDER_EEVEE_NEXT`, `BLENDER_WORKBENCH`), `cpus`, `mem_mb`, `minutes_per_frame`, `label` e i confini.
Blender 4.2, solo processore.

## Prezzo
Riservato in anticipo: CPU × tempo massimo × prezzo per ora-CPU × 2 esecuzioni.
Addebitato a fine compito il tempo effettivo; il resto torna sul credito.

## Risultati
`GET /v1/jobs/{id}/result` elenca i file prodotti; `GET /v1/files/{sha256}` li scarica;
`GET /v1/batches/{batch}/zip`, con il valore `batch` del risultato, scarica tutto il lavoro in un unico ZIP.

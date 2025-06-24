# Product URL Crawler

This repository contains a scalable backend service for discovering and listing all product URLs across multiple e‑commerce websites. It comprises:

1. **Crawler module** (`crawler_worker.py`): An asynchronous Python script that uses sitemaps (and HTML fallback) to locate product page URLs based on domain‑specific patterns.
2. **Django REST API**: Exposes endpoints to enqueue crawl jobs, track their status, and retrieve discovered URLs.
3. **Celery worker**: Executes crawl jobs asynchronously, storing each URL in PostgreSQL.
4. **Persistence**: PostgreSQL for job & URL storage, Redis as Celery broker.

---

## Architecture

```text
+------------+      POST     +--------+     Queue      +--------+      +-------------+
|  Client    |  ----------> |  API   |  ---------->  | Celery | ---> | crawler.py   |
| (curl/JS)  |              | Django |                |Worker  |      | / tasks.py   |
+------------+              +--------+                +--------+      +-------------+
     |                         |  GET/PUT                   |                |
     |                         | <--------------------------                |
     |                         |                                    write URLs to DB
     |                         |                                           |
     |                         v                                           v
     |                     +---------+                               +-------------+
     |                     | Postgres|                               | Redis       |
     |                     +---------+                               +-------------+
     v
 Output JSON
```

- **URL discovery**: For each domain, the crawler first retrieves `robots.txt` + sitemaps; it parses `<loc>` entries and filters those matching a per‑domain regex (e.g. `/products/[^/?#]+`). If a site has fewer than 50 URLs in sitemaps, it falls back to an HTML link‑crawl up to 3 levels deep.
- **Async & resilient**: Uses `aiohttp` with SSL disabled, gzip‑aware sitemap parsing, and concurrent requests.
- **Job tracking**: Each request creates a `CrawlJob` record; Celery picks up the job, updates its status, and saves discovered `ProductURL` records.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- (Optional) Docker & Docker Compose

### Environment

1. Clone this repo:
   ```bash
   git clone https://github.com/your-org/product-url-crawler.git
   cd product-url-crawler
   ```
2. Create a virtual environment & install:
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in DB & broker URLs.

### Database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running services

#### Without Docker

```bash
# Run Django API
python manage.py runserver

# In another shell, start Celery
celery -A backend worker --loglevel=info
```

#### With Docker Compose

```bash
docker-compose up --build -d
```

---

## Usage

### Command‑line crawler (direct)

```bash
python crawler_worker.py https://www.westside.com/
```

Output:

```json
{
  "https://www.westside.com/": ["https://www.westside.com/products/12345", ...]
}
```

### API Endpoints (Django REST Framework)

1. **Enqueue a job**

   ```bash
   curl -X POST http://127.0.0.1:8000/api/jobs/ \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.westside.com/"}'
   ```

   Response:

   ```json
   { "id": 42, "url": "...", "status": "PENDING", "products": [] }
   ```

2. **Get job details**

   ```bash
   curl http://127.0.0.1:8000/api/jobs/42/
   ```

   Response (once complete):

   ```json
   { "id": 42, "url": "...", "status": "SUCCESS", "products": ["https://...", ...] }
   ```

3. **List all jobs**

   ```bash
   curl http://127.0.0.1:8000/api/jobs/
   ```

---

## Output

- **Structured JSON** mapping each domain to its list of unique product URLs.
- All URLs point directly to product pages (e.g. `.../product/12345`).
- Data persisted in two tables:
  - `crawler_crawljob` (id, url, status, timestamps)
  - `crawler_producturl` (foreign key → job, url text)

You can export the `crawler_producturl` table as CSV:

```bash
python manage.py dumpdata crawler.ProductURL --format=csv --output=product_urls.csv
```

---

## Video Walkthrough

A short Loom walkthrough explaining the code structure, crawler logic, and API usage:

👉 **Watch on Loom**: [https://loom.com/share/your-video-url](https://loom.com/share/your-video-url)

---

## Directory Structure

```
mycrawler/
├── backend/                      # Django project
│   ├── backend/                  # project settings
│   ├── crawler/                  # core app (models, views, tasks)
│   ├── manage.py
│   ├── celery.py                 # Celery config
│   └── requirements.txt
├── crawler_worker.py            # standalone CLI crawler
├── docker-compose.yaml
├── .env.example
└── README.md
```

---

## License

This project is released under the MIT License. Feel free to reuse and adapt!


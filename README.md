# Sales Data Analyzer Agent

Streamlit asosidagi sodda sales analizatori:
- CSV/Excel fayl upload
- Dataframe preview
- Metric cardlar (Total Sales, Total Orders, Avg Order Value)
- Top Products va Regional Sales bar chartlari
- Monthly trend line chart
- Natural language savollarga OpenAI agent (fallback: rule-based)
- Savol-javob loglarini DB'ga saqlash (SQLite/PostgreSQL)

## 1) Lokal ishga tushirish

### Talablar
- Python 3.10+

### Qadamlar
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
streamlit run app.py
```

Brauzerda oching: `http://localhost:8501`

## 2) Docker Compose bilan ishga tushirish (app + db)

### Qadamlar
```bash
cp .env.example .env
docker compose up --build
```

Brauzerda oching: `http://localhost:8501`

Compose ichida:
- `app`: Streamlit ilova
- `postgres`: PostgreSQL DB (query loglar uchun)

## 3) Streamlit Cloud deploy

### GitHub'ga push
1. Loyihani GitHub repository'ga joylang.
2. `app.py` ildiz papkada tursin.

### Streamlit Cloud
1. https://share.streamlit.io ga kiring.
2. `New app` -> repository tanlang.
3. Main file path: `app.py`
4. Deploy tugmasini bosing.

Agar PostgreSQL ishlatsangiz, Streamlit Cloud `Secrets`ga quyidagini qo'shing:
```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME"
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4.1-mini"
```

OpenAI agent yoqilgan bo'lsa, ilova savollarga AI orqali javob beradi. Key yo'q bo'lsa yoki API xato bersa, ilova avtomatik rule-based fallback javobga o'tadi.

Deploydan keyin sizga **live public URL** beriladi.

## 4) Public access uchun Docker deploy (VPS)

Agar Streamlit Cloud o'rniga Docker bilan public qilish kerak bo'lsa:
1. VPS oling (Ubuntu/Windows Server).
2. Docker va Docker Compose o'rnating.
3. Repo'ni serverga clone qiling.
4. `docker compose up -d --build`
5. Firewall'da `8501` portni oching yoki reverse proxy (Nginx) bilan domen ulang.

Shunda ilova public URL orqali ochiladi.

## 4.1) Tashqi Nginx reverse proxy (server ichidagi Nginx)

Loyiha ichida tayyor fayllar:
- `deploy/nginx/sales-analyzer.conf`
- `deploy/nginx/enable-nginx.sh`
- `deploy/nginx/enable-https.sh`

### Aktivlashtirish (HTTP)

Serverda loyiha papkasiga kirib:
```bash
docker compose up -d --build
sudo bash deploy/nginx/enable-nginx.sh your-domain.com
```

Yoki domain bo'lmasa:
```bash
sudo bash deploy/nginx/enable-nginx.sh SERVER_PUBLIC_IP
```

### HTTPS yoqish (Let's Encrypt)

```bash
sudo bash deploy/nginx/enable-https.sh your-domain.com your-email@example.com
```

### Tekshiruv

```bash
sudo nginx -t
sudo systemctl status nginx
curl -I http://your-domain.com
```

Eslatma: `docker-compose.yml` ichida app va postgres portlari faqat localhostga bind qilingan (`127.0.0.1`). Tashqi trafikni Nginx qabul qiladi.

## 5) Savol namunalar
- `Jami savdo qancha?`
- `Top product qaysi?`
- `Regionlar bo'yicha analiz ber`
- `Monthly trend ko'rsat`
- `Jadvalda nechta qator bor?`

## Texnik stack
- Frontend: Streamlit
- Backend: Python, Pandas
- DB: SQLite (default) yoki PostgreSQL (docker compose orqali)

## Project structure (Clean code)

```text
sales_analyzer/
	config.py                   # Env config va app settings
	domain/
		analyzer.py               # Core analytics/domain logic
	infrastructure/
		db.py                     # DB adapter va migration
		openai_agent.py           # OpenAI adapter
	services/
		file_service.py           # CSV/Excel file reader service
		question_service.py       # Savolni qayta ishlash orchestrator
	ui/
		sidebar.py                # Sidebar komponentlari
		overview.py               # Metrics va chartlar
		question_panel.py         # Q&A va performance panel
app.py                        # Thin entrypoint/orchestrator
```

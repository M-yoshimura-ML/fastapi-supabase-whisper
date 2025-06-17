### Web stack 
- Python>=3.12
- FastAPI==0.110.0
- supabase==2.15.0
- openai==1.17.0

### Installation
- `pip install -r requirements.txt`

### Set up project
- Copy .env.local to .env
- Get OpenAI API key and set it in .env
- Create Supabase project and set URLs for async and sync in .env
- Get email provider info in .env

### Start app
- `uvicorn app.main:app --port 8000 --log-level debug`


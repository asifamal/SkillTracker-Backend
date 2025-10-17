# SkillStack - Personal Skill Building Tracker

A full-stack application for tracking personal learning progress and skill development.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### Setup

1. **Clone and setup database**
```bash
git clone <repository-url>
cd Skill-Tracker

# Create PostgreSQL database
psql -u admin
CREATE DATABASE skill_tracker_db;
\q
```

2. **Backend setup**
```bash
cd backend
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. **Frontend setup**
```bash
cd ../front end
npm install
npm run dev
```

**Access the app at:** `http://localhost:5173`

## 🛠️ Tech Stack

**Backend:** Django 5.2.7, Django REST Framework, PostgreSQL  
**Frontend:** React 18, TypeScript, Vite, Tailwind CSS

## 📋 Features

- **Dashboard** - Overview with statistics and charts
- **Skills Management** - Add, view, update, delete learning goals
- **Progress Tracking** - Update status, hours, difficulty
- **Timeline View** - Chronological learning activities
- **Auto-Categorization** - Smart skill categorization
- **Filtering** - Filter by progress and category

## 📁 Project Structure

```
Skill-Tracker/
├── backend/          # Django API
├── front end/        # React app
└── README.md
```

## 🔧 API Endpoints

- `GET /skills/list_skills/` - List skills
- `POST /skills/skill_create/` - Create skill
- `GET /skills/skill_detail/<id>/` - Get skill details
- `PATCH /skills/update_skill/<id>/` - Update skill
- `DELETE /skills/delete_skill/<id>/` - Delete skill
- `GET /skills/dashboard/` - Dashboard data
- `GET /skills/timeline/` - Timeline data

## 📖 Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

---

**Happy Learning! 🚀**

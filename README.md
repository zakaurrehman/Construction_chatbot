# Construction Project Management Chatbot

A modern AI-powered chatbot for construction project management using Google's Gemini API and PostgreSQL database. This system provides natural language interaction with your project data, offering insights on project status, timelines, budgets, and more.

## ✨ Features

- **Natural Language Queries**: Ask questions about projects in plain English
- **Real-time Database Integration**: Dynamic SQL query generation based on user requests
- **Project Management**: Track phases, milestones, selections, and walkthroughs
- **Budget Monitoring**: View project budgets and payment milestones
- **Progress Tracking**: Visual progress indicators and detailed status reports
- **Smart Formatting**: Markdown-based responses with tables, charts, and visual elements

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Gemini API
- **Database**: PostgreSQL
- **Frontend**: React.js with Marked for markdown rendering
- **Styling**: Custom CSS with responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd construction-chatbot
```

2. **Run the setup script**
```bash
python setup.py
```

3. **Configure environment variables**
```bash
# Edit .env file with your values
cp .env.example .env
nano .env
```

Add your Gemini API key and database credentials:
```
GEMINI_API_KEY=your-gemini-api-key-here
DB_HOST=localhost
DB_NAME=construction_db
DB_USER=postgres
DB_PASSWORD=your-password
```

4. **Start the application**

Backend:
```bash
python app.py
```

Frontend (in a new terminal):
```bash
cd frontend
npm start
```

## 📁 Project Structure

```
construction-chatbot/
├── app.py                      # Entry point
├── main.py                     # Flask app setup
├── config.py                   # Configuration
├── routes.py                   # API endpoints
├── database/
│   ├── __init__.py
│   ├── db_connector.py         # Database connection
│   └── schema_extractor.py     # Schema analysis
├── chatbot/
│   ├── __init__.py
│   ├── gemini_client.py        # Gemini API client
│   └── chat_handler.py         # Chat logic
├── frontend/
│   └── src/
│       ├── Home.jsx           # React chat component
│       └── home.css           # Styling
├── logs/                       # Application logs
└── .env                        # Environment variables
```

## 💬 Usage Examples

### Project Status
```
"What's the status of JAIN-1B project?"
"Show me all active projects"
"What phase is CABOT-1B in?"
```

### Progress Tracking
```
"Show me progress of ELMGROVE-1B"
"What tasks are pending in Phase 2?"
"Which projects are behind schedule?"
```

### Budget Management
```
"What's the budget status for all projects?"
"Show me payment milestones for JAIN-1B"
"Which projects can be billed this week?"
```

### Selections and Walkthroughs
```
"What selections are due next week?"
"Show me pending PD walkthroughs"
"Are there any overdue client walkthroughs?"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | construction_db |
| `DB_USER` | Database user | postgres |
| `MAX_CONVERSATION_LENGTH` | Max chat history | 20 |

### Database Schema

The system expects a PostgreSQL database with tables for:
- Projects and phases
- Tasks and milestones
- Selections and materials
- Walkthroughs and inspections
- Budget and payments

## 🔒 Security

- SQL injection prevention with parameterized queries
- Input validation and sanitization
- Safe SQL query generation with restrictions
- Environment variable configuration

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in .env
   - Ensure database exists

2. **Gemini API Error**
   - Verify API key is correct
   - Check internet connection
   - Ensure API usage limits not exceeded

3. **Frontend Not Loading**
   - Run `npm install` in frontend directory
   - Ensure backend is running on port 5000
   - Check browser console for errors

## 📝 Development

### Adding New Features

1. **New Database Tables**: Add to schema and update `schema_extractor.py`
2. **Custom Queries**: Add methods to `db_connector.py`
3. **UI Components**: Extend React components in `frontend/src/`

### Code Style

- Python: Follow PEP 8 guidelines
- JavaScript: Use ESLint with React configuration
- CSS: Follow BEM naming convention

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## 🔗 Links

- [Google Gemini API Documentation](https://ai.google.dev/tutorials/python_quickstart)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

Made with ❤️ for construction professionals
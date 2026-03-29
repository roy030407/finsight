# FinSight

AI-powered personal finance platform for intelligent financial management and insights.

## 🚀 Features

- **Dashboard** - Comprehensive financial overview with real-time analytics
- **Transaction Management** - Track income and expenses with categorization
- **Smart Analytics** - AI-powered spending insights and recommendations
- **Goal Setting** - Set and track financial goals with progress tracking
- **Investment Tracking** - Monitor portfolio performance and returns
- **AI Chat Assistant** - Get personalized financial advice and insights
- **Data Export** - Power BI integration with CSV and JSON exports
- **Responsive Design** - Modern UI that works on all devices

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|--------|---------|
| FastAPI | 0.104+ | REST API framework |
| SQLAlchemy | 2.0+ | ORM and database management |
| PostgreSQL | 15+ | Primary database |
| Pydantic | 2.0+ | Data validation and serialization |
| JWT | - | Authentication tokens |
| Gemini AI | - | AI-powered insights |
| bcrypt | - | Password hashing |

### Frontend
| Technology | Version | Purpose |
|------------|--------|---------|
| React | 18+ | UI framework |
| React Router | 7+ | Client-side routing |
| Zustand | - | State management |
| Tailwind CSS | - | Styling |
| ShadCN/UI | - | Component library |
| Recharts | - | Data visualization |
| Axios | - | HTTP client |

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend    │    │    Backend     │    │   Database      │
│   (React)     │◄──►│   (FastAPI)    │◄──►│  (PostgreSQL)   │
│   Port: 5173  │    │   Port: 8000   │    │   Port: 5432   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/personal-finance-dashboard.git
   cd personal-finance-dashboard
   ```

2. **Set up environment variables**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   
   # Frontend environment
   cp frontend/.env.example frontend/.env
   # Edit frontend/.env with your settings
   ```

3. **Start the services**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   # Terminal 2: Start frontend
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## ⚙️ Environment Variables

### Backend (.env)
| Variable | Description | Default |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | postgresql://localhost/finsight |
| SECRET_KEY | JWT signing secret | your-secret-key |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |
| GEMINI_API_KEY | Google Gemini API key | - |

### Frontend (.env)
| Variable | Description | Default |
|----------|-------------|----------|
| VITE_API_URL | Backend API URL | http://localhost:8000 |

## 📡 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Transactions
- `GET /transactions/` - List all transactions
- `POST /transactions/` - Create new transaction
- `GET /transactions/summary` - Get transaction summary
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

### Analytics
- `GET /analytics/insights` - Get spending insights
- `GET /analytics/trends` - Get spending trends
- `GET /analytics/categories` - Category breakdown

### Goals
- `GET /goals/` - List all goals
- `POST /goals/` - Create new goal
- `PUT /goals/{id}` - Update goal
- `DELETE /goals/{id}` - Delete goal

### Investments
- `GET /investments/` - List all investments
- `POST /investments/` - Add new investment
- `GET /investments/performance` - Get portfolio performance

### AI Chat
- `POST /chat/ask` - Ask AI financial questions
- `GET /chat/history` - Get chat history

### Export
- `GET /export/transactions.csv` - Download transactions as CSV
- `GET /export/summary.json` - Export data for Power BI

## 🔌 Power BI Integration

1. Open Power BI Desktop
2. Go to **Get Data → Web**
3. URL: `http://localhost:8000/export/summary.json`
4. Add Authorization header: `Bearer YOUR_JWT_TOKEN`
5. Refresh data to get latest financial insights

## 📊 Data Export Formats

### CSV Export
- All transactions with full details
- Compatible with Excel, Google Sheets
- Includes: Date, Description, Category, Amount, Type, Payment Mode

### JSON Export
- Power BI-optimized structure
- Includes aggregated data by category and month
- Contains user metadata and savings rate
- Real-time data refresh capability

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
- ESLint for frontend code linting
- Pylint for backend code linting
- Prettier for code formatting
- Pre-commit hooks for code quality

## 📦 Deployment

### Production Setup
1. Set up PostgreSQL database
2. Configure environment variables
3. Deploy backend to your preferred hosting platform
4. Build and deploy frontend to your preferred hosting platform

### Environment Setup
- **Development**: Local development with hot reload
- **Staging**: Pre-production testing environment
- **Production**: Optimized for performance and security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [React](https://reactjs.org/) - UI framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
- [ShadCN/UI](https://ui.shadcn.com/) - Component library
- [Google Gemini](https://ai.google.dev/) - AI capabilities

---

**Built by Roy Harwani, NIT Warangal**

[GitHub](https://github.com/your-username) • [Portfolio](https://your-portfolio.com)

# Sleepr Frontend

A modern React TypeScript frontend for the Sleepr fantasy football dynasty management application.

## Features

- **Authentication**: JWT-based authentication with Sleeper ID integration
- **Dashboard**: Overview of all teams, performance metrics, and quick actions
- **Team Management**: View and manage dynasty/redraft teams with sync capabilities
- **Waiver Wire**: AI-powered pickup recommendations with scoring system
- **Responsive Design**: Mobile-first design using Material-UI components
- **API Integration**: Full integration with Go backend API

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for component library
- **React Router** for navigation
- **Axios** for API communication
- **JWT** for authentication
- **ESLint** for code quality

## Project Structure

```
web/frontend/
├── package.json           # Dependencies and scripts
├── src/
│   ├── App.tsx           # Main application component with routing
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx # Main dashboard with stats and quick actions
│   │   ├── Login.tsx     # Authentication page
│   │   ├── Teams.tsx     # Team management and overview
│   │   └── WaiverWire.tsx # AI-powered waiver recommendations
│   └── services/         # API and utility services
│       ├── api.ts        # API service layer with axios
│       └── AuthContext.tsx # JWT authentication context
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Sleepr backend API running on port 8080

### Installation

1. Install dependencies:
```bash
cd web/frontend
npm install
```

2. Set environment variables:
```bash
# Create .env file
REACT_APP_API_URL=http://localhost:8080/api/v1
```

3. Start development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

## Pages Overview

### Login Page
- Clean, professional login interface
- Sleeper User ID authentication
- Instructions for finding Sleeper ID
- Error handling and loading states

### Dashboard
- Welcome message with user info
- Key statistics cards (teams, win rate, rankings)
- Quick action buttons (sync, analytics, waiver wire)
- Recent activity and upcoming tasks
- Responsive grid layout

### Teams Page
- List of all user teams (dynasty and redraft)
- Team performance metrics and records
- Win percentage visualization
- Individual team sync and analytics actions
- Overview statistics summary

### Waiver Wire
- AI-powered player recommendations
- Recommendation scoring (1-10 scale)
- Position-based filtering and priorities
- Detailed reasoning for each recommendation
- Watchlist management
- Weekly strategy insights

## API Integration

The frontend communicates with the Go backend through a comprehensive API service:

### Authentication Endpoints
- `POST /public/auth/login` - Login with username/Sleeper ID
- `POST /auth/refresh` - Refresh JWT token

### Team Endpoints
- `GET /teams` - Get user teams
- `GET /teams/:id` - Get specific team
- `POST /teams/:id/sync` - Sync team with Sleeper

### Player Endpoints
- `GET /players` - Get players
- `GET /players/:id` - Get specific player

### Analytics Endpoints
- `GET /public/analytics/waiver-wire` - Get waiver recommendations
- `GET /analytics/teams/:id/recommendations` - Get team recommendations
- `GET /analytics/players/:id/projection` - Get player projections

## Authentication System

The app uses JWT-based authentication:

1. User logs in with username and Sleeper User ID
2. Backend validates and returns JWT token
3. Token stored in localStorage
4. All API requests include Authorization header
5. Automatic redirect to login on token expiration
6. Token refresh capability for extended sessions

## State Management

- **AuthContext**: Manages user authentication state
- **API Service**: Centralized API communication with interceptors
- **Local State**: Component-level state for UI interactions
- **Error Handling**: Consistent error handling across components

## Styling and Theme

- Material-UI default theme with customizations
- Responsive breakpoints for mobile/tablet/desktop
- Consistent color scheme:
  - Primary: Blue (dynasty teams, main actions)
  - Secondary: Purple (redraft teams, secondary actions)
  - Success: Green (positive metrics, wins)
  - Warning: Orange (medium priority, cautions)
  - Error: Red (high priority, losses)

## Development Guidelines

### Code Organization
- Components in PascalCase
- Services in camelCase
- Clear separation of concerns
- TypeScript interfaces for all data structures

### Error Handling
- Try-catch blocks for async operations
- User-friendly error messages
- Fallback to mock data when API unavailable
- Loading states for better UX

### Best Practices
- Responsive design first
- Accessibility considerations
- Clean, readable code
- Proper TypeScript typing
- Consistent naming conventions

## Future Enhancements

- [ ] Real-time updates with WebSocket
- [ ] Advanced analytics charts
- [ ] Trade analyzer
- [ ] Player comparison tools
- [ ] Push notifications
- [ ] Offline mode support
- [ ] Advanced filtering and search
- [ ] Custom dashboard widgets
- [ ] Team chat integration
- [ ] Historical data visualization

## API Dependencies

The frontend expects the backend API to be running with the following endpoints available:

- Authentication endpoints for login/refresh
- Team management endpoints
- Player data endpoints
- Analytics endpoints for recommendations
- Health check endpoint

Ensure the backend is properly configured with CORS to allow frontend requests.

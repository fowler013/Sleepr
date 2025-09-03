import axios, { AxiosInstance } from 'axios';

interface LoginRequest {
  username: string;
  sleeper_id: string;
}

interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    display_name: string;
    sleeper_id: string;
    email?: string;
  };
}

interface Team {
  id: number;
  name: string;
  owner: string;
  is_dynasty: boolean;
  league_id: string;
}

interface Player {
  id: number;
  name: string;
  position: string;
  team: string;
  fantasy_points: number;
}

interface WaiverWirePlayer {
  player_id: number;
  name: string;
  position: string;
  team: string;
  recommendation_score: number;
  reason: string;
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1',
      timeout: 10000,
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('sleepr_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('sleepr_token');
          localStorage.removeItem('sleepr_user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string | null) {
    if (token) {
      this.client.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.Authorization;
    }
  }

  // Auth endpoints
  async login(username: string, sleeperId: string): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/public/auth/login', {
      username,
      sleeper_id: sleeperId,
    });
    return response.data;
  }

  async refreshToken(): Promise<{ token: string }> {
    const response = await this.client.post<{ token: string }>('/auth/refresh');
    return response.data;
  }

  // Team endpoints
  async getTeams(): Promise<Team[]> {
    const response = await this.client.get<Team[]>('/teams');
    return response.data;
  }

  async getTeam(id: number): Promise<Team> {
    const response = await this.client.get<Team>(`/teams/${id}`);
    return response.data;
  }

  async syncTeam(teamId: string): Promise<void> {
    await this.client.post(`/teams/${teamId}/sync`);
  }

  // Player endpoints
  async getPlayers(): Promise<Player[]> {
    const response = await this.client.get<Player[]>('/players');
    return response.data;
  }

  async getPlayer(id: number): Promise<Player> {
    const response = await this.client.get<Player>(`/players/${id}`);
    return response.data;
  }

  // Analytics endpoints
  async getWaiverWireRecommendations(): Promise<WaiverWirePlayer[]> {
    const response = await this.client.get<WaiverWirePlayer[]>('/public/analytics/waiver-wire');
    return response.data;
  }

  async getTeamRecommendations(teamId: number): Promise<any> {
    const response = await this.client.get(`/analytics/teams/${teamId}/recommendations`);
    return response.data;
  }

  async getPlayerProjection(playerId: number): Promise<any> {
    const response = await this.client.get(`/analytics/players/${playerId}/projection`);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiService();

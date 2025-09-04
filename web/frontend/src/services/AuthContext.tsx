import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from './api';

interface User {
  id: number;
  username: string;
  display_name: string;
  sleeper_id: string;
  email?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, sleeperId: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = localStorage.getItem('sleepr_token');
    const savedUser = localStorage.getItem('sleepr_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      api.setAuthToken(savedToken);
    }
    
    setLoading(false);
  }, []);

  const login = async (username: string, sleeperId: string) => {
    try {
      setLoading(true);
      const response = await api.login(username, sleeperId);
      
      setToken(response.token);
      setUser(response.user);
      
      localStorage.setItem('sleepr_token', response.token);
      localStorage.setItem('sleepr_user', JSON.stringify(response.user));
      
      api.setAuthToken(response.token);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('sleepr_token');
    localStorage.removeItem('sleepr_user');
    api.setAuthToken(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

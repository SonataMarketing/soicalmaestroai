"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, authService, LoginCredentials, SignupData } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (data: SignupData) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && authService.isAuthenticated();

  const login = async (credentials: LoginCredentials) => {
    try {
      await authService.login(credentials);
      const user = await authService.getCurrentUser();
      setUser(user);
    } catch (error) {
      throw error;
    }
  };

  const signup = async (data: SignupData) => {
    try {
      const newUser = await authService.signup(data);
      // Note: Signup doesn't automatically log in the user
      // They need to login separately
      return newUser;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        setUser(user);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      logout();
    }
  };

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          // Try to refresh token if it's close to expiring
          if (authService.isTokenExpired()) {
            try {
              await authService.refreshToken();
            } catch (error) {
              console.error('Token refresh failed:', error);
              logout();
              return;
            }
          }

          const user = await authService.getCurrentUser();
          setUser(user);
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(async () => {
      if (authService.isTokenExpired()) {
        try {
          await authService.refreshToken();
          await refreshUser();
        } catch (error) {
          console.error('Auto token refresh failed:', error);
          logout();
        }
      }
    }, 5 * 60 * 1000); // Check every 5 minutes

    return () => clearInterval(interval);
  }, [isAuthenticated, refreshUser]);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
    refreshUser,
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

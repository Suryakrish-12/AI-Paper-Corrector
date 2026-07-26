import { create } from 'zustand';
import { api } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  student_id?: number | null;
  faculty_id?: number | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  loading: true,
  
  login: async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      
      const userResponse = await api.get('/auth/me');
      set({ user: userResponse.data, token, loading: false });
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, loading: false });
  },
  
  loadUser: async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userResponse = await api.get('/auth/me');
        set({ user: userResponse.data, token, loading: false });
      } else {
        set({ loading: false });
      }
    } catch (error) {
      localStorage.removeItem('token');
      set({ user: null, token: null, loading: false });
    }
  }
}));

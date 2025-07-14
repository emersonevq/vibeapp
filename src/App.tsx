import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Auth } from './components/auth/Auth';  // Atualizado
import { Feed } from './components/Feed';
import { Profile } from './components/profile/Profile';  // Atualizado
import { NotificationCenter } from './components/notifications/NotificationCenter';  // Atualizado
import { notificationService } from './services/NotificationService';

interface User {
  id?: number;
  name: string;
  email: string;
  avatar?: string;
  bio?: string;
  location?: string;
  joinDate?: string;
  token: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [realtimeNotifications, setRealtimeNotifications] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData(token);
    } else {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user?.id) {
      const handleNewNotification = (newNotification: any) => {
        setRealtimeNotifications(prev => [newNotification, ...prev]);
      };

      const removeListener = notificationService.addListener(handleNewNotification);
      notificationService.connect(user.id, user.token);

      return () => {
        removeListener();
        notificationService.disconnect();
      };
    }
  }, [user]);

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          id: userData.id,
          name: `${userData.first_name} ${userData.last_name}`,
          email: userData.email,
          bio: userData.bio || 'Apaixonado por conexões genuínas e boas vibes! 🌟',
          location: userData.location || 'São Paulo, Brasil',
          joinDate: 'Janeiro 2025',
          token,
        });
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData: { name: string; email: string; token: string }) => {
    const userWithDefaults = {
      ...userData,
      bio: 'Apaixonado por conexões genuínas e boas vibes! 🌟',
      location: 'São Paulo, Brasil',
      joinDate: 'Janeiro 2025'
    };
    setUser(userWithDefaults);
    localStorage.setItem('token', userData.token);
  };

  const handleLogout = () => {
    notificationService.disconnect();
    localStorage.removeItem('token');
    setUser(null);
    setRealtimeNotifications([]);
  };

  const clearRealtimeNotifications = () => {
    setRealtimeNotifications([]);
  };

  if (loading) {
    return <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <Router>
      <Layout user={user} onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Feed user={user} />} />
          <Route path="/profile" element={<Profile user={user} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
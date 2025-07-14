import React, { useState, useEffect } from 'react';
import { MapPin, Calendar, Briefcase, Heart, Users, MessageCircle, UserPlus, Mail } from 'lucide-react';

interface UserProfileProps {
  userId: number;
  userToken: string;
  onClose: () => void;
}

interface UserData {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  bio?: string;
  location?: string;
  avatar?: string;
  birth_date?: string;
  relationship_status?: string;
  work_company?: string;
  work_position?: string;
  hometown?: string;
  current_city?: string;
  created_at: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  userId,
  userToken,
  onClose
}) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [friendshipStatus, setFriendshipStatus] = useState<'none' | 'pending' | 'friends'>('none');

  useEffect(() => {
    fetchUserData();
    checkFriendshipStatus();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      }
    } catch (error) {
      console.error('Erro ao carregar dados do usuário:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkFriendshipStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8000/friendships/status/${userId}`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setFriendshipStatus(data.status);
      }
    } catch (error) {
      console.error('Erro ao verificar status de amizade:', error);
    }
  };

  const handleSendFriendRequest = async () => {
    try {
      const response = await fetch('http://localhost:8000/friendships/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          addressee_id: userId
        }),
      });

      if (response.ok) {
        setFriendshipStatus('pending');
      }
    } catch (error) {
      console.error('Erro ao enviar solicitação de amizade:', error);
    }
  };

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 text-center">
          <p>Usuário não encontrado</p>
          <button onClick={onClose} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">
            Fechar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="relative">
          <div className="h-32 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 bg-black bg-opacity-20 text-white rounded-full hover:bg-opacity-40"
          >
            ×
          </button>
        </div>

        {/* Profile Info */}
        <div className="px-6 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-end sm:space-x-6">
            {/* Avatar */}
            <div className="relative -mt-16 mb-4 sm:mb-0">
              <img
                src={user.avatar || `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}&background=3B82F6&color=fff`}
                alt={`${user.first_name} ${user.last_name}`}
                className="w-32 h-32 rounded-full border-4 border-white"
              />
            </div>
            
            {/* User Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-gray-900">
                {user.first_name} {user.last_name}
              </h1>
              {user.bio && (
                <p className="text-gray-600 mt-1">{user.bio}</p>
              )}
              
              <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500">
                {user.current_city && (
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-4 h-4" />
                    <span>{user.current_city}</span>
                  </div>
                )}
                {user.birth_date && (
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{calculateAge(user.birth_date)} anos</span>
                  </div>
                )}
                {user.work_company && (
                  <div className="flex items-center space-x-1">
                    <Briefcase className="w-4 h-4" />
                    <span>{user.work_position} em {user.work_company}</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex space-x-3 mt-4 sm:mt-0">
              {friendshipStatus === 'none' && (
                <button
                  onClick={handleSendFriendRequest}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all flex items-center space-x-2"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Adicionar</span>
                </button>
              )}
              {friendshipStatus === 'pending' && (
                <button
                  disabled
                  className="px-6 py-2 bg-gray-400 text-white rounded-lg font-medium cursor-not-allowed"
                >
                  Solicitação enviada
                </button>
              )}
              {friendshipStatus === 'friends' && (
                <button className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium">
                  Amigos
                </button>
              )}
              <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>Mensagem</span>
              </button>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="px-6 pb-6 space-y-4">
          {user.relationship_status && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Estado Civil</h3>
              <p className="text-gray-600">{user.relationship_status}</p>
            </div>
          )}
          
          {user.hometown && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Cidade Natal</h3>
              <p className="text-gray-600">{user.hometown}</p>
            </div>
          )}
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Membro desde</h3>
            <p className="text-gray-600">
              {new Date(user.created_at).toLocaleDateString('pt-BR', {
                month: 'long',
                year: 'numeric'
              })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
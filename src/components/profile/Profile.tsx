import React, { useState, useEffect } from 'react';
import { MapPin, Calendar, Briefcase, Heart, Users, MessageCircle, Settings } from 'lucide-react';
import { PostCard } from '../posts/PostCard';

interface ProfileProps {
  user: {
    id?: number;
    name: string;
    email: string;
    bio?: string;
    location?: string;
    joinDate?: string;
    token: string;
  };
}

interface Post {
  id: string;
  author: {
    id: number;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  content: string;
  post_type: 'post' | 'testimonial';
  created_at: string;
  reactions_count: number;
  comments_count: number;
  shares_count: number;
}

export function Profile({ user }: ProfileProps) {
  const [activeTab, setActiveTab] = useState<'posts' | 'testimonials'>('posts');
  const [posts, setPosts] = useState<Post[]>([]);
  const [testimonials, setTestimonials] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserPosts();
    fetchUserTestimonials();
  }, []);

  const fetchUserPosts = async () => {
    try {
      const response = await fetch(`http://localhost:8000/users/${user.id}/posts`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPosts(data.filter((post: Post) => post.post_type === 'post'));
      }
    } catch (error) {
      console.error('Erro ao carregar posts:', error);
    }
  };

  const fetchUserTestimonials = async () => {
    try {
      const response = await fetch(`http://localhost:8000/users/${user.id}/testimonials`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setTestimonials(data.filter((post: Post) => post.post_type === 'testimonial'));
      }
    } catch (error) {
      console.error('Erro ao carregar depoimentos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePostDeleted = () => {
    fetchUserPosts();
    fetchUserTestimonials();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Cover Photo */}
        <div className="h-48 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
        
        {/* Profile Info */}
        <div className="px-6 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-end sm:space-x-6">
            {/* Avatar */}
            <div className="relative -mt-16 mb-4 sm:mb-0">
              <img
                src={user.avatar || `https://ui-avatars.com/api/?name=${user.name}&background=3B82F6&color=fff`}
                alt={user.name}
                className="w-32 h-32 rounded-full border-4 border-white"
              />
            </div>
            
            {/* User Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-gray-900">{user.name}</h1>
              <p className="text-gray-600 mt-1">{user.bio}</p>
              
              <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500">
                {user.location && (
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-4 h-4" />
                    <span>{user.location}</span>
                  </div>
                )}
                {user.joinDate && (
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>Entrou em {user.joinDate}</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  <Briefcase className="w-4 h-4" />
                  <span>Desenvolvedor</span>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex space-x-3 mt-4 sm:mt-0">
              <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all">
                Editar Perfil
              </button>
              <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Heart className="w-6 h-6 text-red-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">1.2k</h3>
          <p className="text-gray-600">Curtidas</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">342</h3>
          <p className="text-gray-600">Amigos</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <MessageCircle className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{posts.length + testimonials.length}</h3>
          <p className="text-gray-600">Posts</p>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('posts')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'posts'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Posts ({posts.length})
            </button>
            <button
              onClick={() => setActiveTab('testimonials')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'testimonials'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Depoimentos ({testimonials.length})
            </button>
          </nav>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {activeTab === 'posts' && (
                <>
                  {posts.length === 0 ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Nenhum post ainda</p>
                    </div>
                  ) : (
                    posts.map((post) => (
                      <PostCard
                        key={post.id}
                        post={post}
                        userToken={user.token}
                        currentUserId={user.id}
                        onPostDeleted={handlePostDeleted}
                        showAuthor={true}
                      />
                    ))
                  )}
                </>
              )}

              {activeTab === 'testimonials' && (
                <>
                  {testimonials.length === 0 ? (
                    <div className="text-center py-12">
                      <Heart className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Nenhum depoimento ainda</p>
                    </div>
                  ) : (
                    testimonials.map((testimonial) => (
                      <PostCard
                        key={testimonial.id}
                        post={testimonial}
                        userToken={user.token}
                        currentUserId={user.id}
                        onPostDeleted={handlePostDeleted}
                        showAuthor={true}
                      />
                    ))
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
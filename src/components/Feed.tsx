import React, { useState, useEffect } from 'react';
import { CreatePostModal } from './modals/CreatePostModal';
import { CreateStoryModal } from './modals/CreateStoryModal';
import { PostCard } from './posts/PostCard';
import { StoriesBar } from './stories/StoriesBar';

interface FeedProps {
  user: {
    id?: number;
    name: string;
    email: string;
    avatar?: string;
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
  media_type?: string;
  media_url?: string;
  created_at: string;
  reactions_count: number;
  comments_count: number;
  shares_count: number;
}

export const Feed: React.FC<FeedProps> = ({ user }) => {
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [showCreateStory, setShowCreateStory] = useState(false);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPosts();
  }, [user.token]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/posts/', {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPosts(data.map((post: any) => ({
          ...post,
          author: {
            ...post.author,
            name: `${post.author.first_name} ${post.author.last_name}`
          }
        })));
      } else if (response.status === 401) {
        setError('Sessão expirada. Faça login novamente.');
      } else {
        setError('Erro ao carregar posts');
      }
    } catch (error) {
      console.error('Erro ao carregar posts:', error);
      setError('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (content: string, type: 'post' | 'testimonial', mediaData?: any) => {
    try {
      const payload = {
        content,
        post_type: type,
        media_type: mediaData?.type || null,
        media_url: mediaData?.url || null,
        media_metadata: mediaData ? JSON.stringify(mediaData) : null
      };

      const response = await fetch('http://localhost:8000/posts/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        fetchPosts();
      } else {
        console.error('Erro ao criar post');
      }
    } catch (error) {
      console.error('Erro ao criar publicação:', error);
    }
  };

  const handleCreateStory = async (content: string, mediaData?: any, storyDuration?: number, backgroundColor?: string) => {
    try {
      const payload = {
        content,
        media_type: mediaData?.type || null,
        media_url: mediaData?.url || null,
        duration_hours: storyDuration || 24,
        background_color: backgroundColor
      };

      const response = await fetch('http://localhost:8000/stories/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        // Refresh stories will be handled by StoriesBar component
      } else {
        console.error('Erro ao criar story');
      }
    } catch (error) {
      console.error('Erro ao criar story:', error);
    }
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchPosts}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stories Bar */}
      <StoriesBar 
        userToken={user.token} 
        onCreateStory={() => setShowCreateStory(true)}
        currentUser={user}
      />

      {/* Create Post */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-4">
          <img
            src={user.avatar || `https://ui-avatars.com/api/?name=${user.name}&background=3B82F6&color=fff`}
            alt={user.name}
            className="w-12 h-12 rounded-full"
          />
          <button
            onClick={() => setShowCreatePost(true)}
            className="flex-1 text-left p-4 bg-slate-100 rounded-full text-slate-600 hover:bg-slate-200 transition-colors"
          >
            No que você está pensando, {user.name.split(' ')[0]}?
          </button>
        </div>
      </div>

      {/* Posts Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : posts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <p className="text-slate-500 text-lg">Nenhum post ainda.</p>
            <p className="text-slate-400 mt-2">Seja o primeiro a compartilhar algo!</p>
          </div>
        ) : (
          posts.map((post) => (
            <PostCard key={post.id} post={post} userToken={user.token} onPostDeleted={fetchPosts} />
          ))
        )}
      </div>

      {/* Create Post Modal */}
      <CreatePostModal
        isOpen={showCreatePost}
        onClose={() => setShowCreatePost(false)}
        onSubmit={handleCreatePost}
      />

      {/* Create Story Modal */}
      <CreateStoryModal
        isOpen={showCreateStory}
        onClose={() => setShowCreateStory(false)}
        onSubmit={handleCreateStory}
      />
    </div>
  );
};
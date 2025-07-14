import React, { useState } from 'react';
import { X, Image, Video, Smile, Type, Palette, Globe, Users, Lock } from 'lucide-react';

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string, type: 'post' | 'testimonial', privacyLevel: string, mediaData?: any) => void;
}

export function CreatePostModal({ isOpen, onClose, onSubmit }: CreatePostModalProps) {
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState<'post' | 'testimonial'>('post');
  const [privacyLevel, setPrivacyLevel] = useState('public');
  const [testimonialStyle, setTestimonialStyle] = useState({
    fontSize: '16',
    fontWeight: 'normal',
    color: '#000000',
    backgroundColor: '#ffffff',
    textShadow: false,
    fontFamily: 'Arial'
  });

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!content.trim()) return;
    
    let finalContent = content;
    
    if (postType === 'testimonial') {
      const styles = {
        fontSize: testimonialStyle.fontSize + 'px',
        fontWeight: testimonialStyle.fontWeight,
        color: testimonialStyle.color,
        backgroundColor: testimonialStyle.backgroundColor,
        fontFamily: testimonialStyle.fontFamily,
        textShadow: testimonialStyle.textShadow ? '2px 2px 4px rgba(0,0,0,0.5)' : 'none'
      };
      
      finalContent = JSON.stringify({
        content: content,
        styles: styles
      });
    } else {
      // Para posts normais, bloquear HTML/estilos
      finalContent = content.replace(/<[^>]*>/g, '');
    }
    
    onSubmit(finalContent, postType, privacyLevel);
    setContent('');
    setPostType('post');
    setPrivacyLevel('public');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Criar publicação</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Tipo de Post */}
          <div className="mb-4">
            <div className="flex space-x-4">
              <button
                onClick={() => setPostType('post')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  postType === 'post'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Post Normal
              </button>
              <button
                onClick={() => setPostType('testimonial')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  postType === 'testimonial'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Depoimento
              </button>
            </div>
          </div>

          {/* Privacy Level */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quem pode ver?
            </label>
            <select
              value={privacyLevel}
              onChange={(e) => setPrivacyLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="public">🌍 Público</option>
              <option value="friends">👥 Apenas amigos</option>
              <option value="private">🔒 Apenas eu</option>
            </select>
          </div>

          {/* Estilos do Depoimento */}
          {postType === 'testimonial' && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg space-y-4">
              <h3 className="font-medium text-gray-900">Personalizar Depoimento</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tamanho da Fonte
                  </label>
                  <select
                    value={testimonialStyle.fontSize}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, fontSize: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="14">Pequena</option>
                    <option value="16">Normal</option>
                    <option value="18">Grande</option>
                    <option value="24">Muito Grande</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Peso da Fonte
                  </label>
                  <select
                    value={testimonialStyle.fontWeight}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, fontWeight: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="normal">Normal</option>
                    <option value="bold">Negrito</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cor do Texto
                  </label>
                  <input
                    type="color"
                    value={testimonialStyle.color}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, color: e.target.value})}
                    className="w-full h-10 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cor de Fundo
                  </label>
                  <input
                    type="color"
                    value={testimonialStyle.backgroundColor}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, backgroundColor: e.target.value})}
                    className="w-full h-10 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fonte
                  </label>
                  <select
                    value={testimonialStyle.fontFamily}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, fontFamily: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="Arial">Arial</option>
                    <option value="Georgia">Georgia</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Helvetica">Helvetica</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="textShadow"
                    checked={testimonialStyle.textShadow}
                    onChange={(e) => setTestimonialStyle({...testimonialStyle, textShadow: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="textShadow" className="text-sm font-medium text-gray-700">
                    Sombra no Texto
                  </label>
                </div>
              </div>

              {/* Preview */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Preview:</label>
                <div className="p-4 rounded-lg border">
                  {content ? (
                    <div 
                      style={{
                        fontSize: testimonialStyle.fontSize + 'px',
                        fontWeight: testimonialStyle.fontWeight,
                        color: testimonialStyle.color,
                        backgroundColor: testimonialStyle.backgroundColor,
                        fontFamily: testimonialStyle.fontFamily,
                        textShadow: testimonialStyle.textShadow ? '2px 2px 4px rgba(0,0,0,0.5)' : 'none'
                      }}
                      dangerouslySetInnerHTML={{ 
                        __html: content 
                      }}
                    />
                  ) : (
                    <div 
                      style={{
                        fontSize: testimonialStyle.fontSize + 'px',
                        fontWeight: testimonialStyle.fontWeight,
                        color: testimonialStyle.color,
                        backgroundColor: testimonialStyle.backgroundColor,
                        fontFamily: testimonialStyle.fontFamily,
                        textShadow: testimonialStyle.textShadow ? '2px 2px 4px rgba(0,0,0,0.5)' : 'none'
                      }}
                    >
                      Digite seu depoimento para ver o preview...
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Textarea */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={postType === 'testimonial' ? 'Escreva seu depoimento...' : 'O que você está pensando?'}
            className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
          />

          {/* Actions */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex space-x-4">
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Image className="w-5 h-5" />
                <span className="text-sm">Foto</span>
              </button>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Video className="w-5 h-5" />
                <span className="text-sm">Vídeo</span>
              </button>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Smile className="w-5 h-5" />
                <span className="text-sm">Emoji</span>
              </button>
            </div>
            <button
              onClick={handleSubmit}
              disabled={!content.trim()}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Publicar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
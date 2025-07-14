import React, { useState } from 'react';
import { X, Send } from 'lucide-react';

interface MessagesModalProps {
  isOpen: boolean;
  onClose: () => void;
  userToken: string;
}

export function MessagesModal({ isOpen, onClose, userToken }: MessagesModalProps) {
  const [conversations, setConversations] = useState([]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full h-[600px] flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Mensagens</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 flex">
          {/* Lista de conversas */}
          <div className="w-1/3 border-r border-gray-200 p-4">
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhuma conversa ainda</p>
            </div>
          </div>

          {/* Área de mensagens */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 p-4">
              <div className="text-center py-12">
                <p className="text-gray-500">Selecione uma conversa</p>
              </div>
            </div>

            {/* Input de mensagem */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Digite uma mensagem..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
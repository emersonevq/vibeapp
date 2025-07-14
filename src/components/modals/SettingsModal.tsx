import React from 'react';
import { X, User, Shield, Bell, Palette, LogOut } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  userToken: string;
  onLogout: () => void;
}

export function SettingsModal({ isOpen, onClose, userToken, onLogout }: SettingsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-md w-full">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Configurações</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg flex items-center space-x-3">
            <User className="w-5 h-5 text-gray-600" />
            <span>Editar Perfil</span>
          </button>

          <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg flex items-center space-x-3">
            <Shield className="w-5 h-5 text-gray-600" />
            <span>Privacidade</span>
          </button>

          <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg flex items-center space-x-3">
            <Bell className="w-5 h-5 text-gray-600" />
            <span>Notificações</span>
          </button>

          <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg flex items-center space-x-3">
            <Palette className="w-5 h-5 text-gray-600" />
            <span>Tema</span>
          </button>

          <hr className="my-4" />

          <button
            onClick={onLogout}
            className="w-full text-left p-3 hover:bg-red-50 rounded-lg flex items-center space-x-3 text-red-600"
          >
            <LogOut className="w-5 h-5" />
            <span>Sair</span>
          </button>
        </div>
      </div>
    </div>
  );
}
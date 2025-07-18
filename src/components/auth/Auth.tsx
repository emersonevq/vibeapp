import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Users, MessageCircle, Sparkles, Eye, EyeOff, ChevronLeft, ChevronRight } from 'lucide-react';
import { Logo } from "../ui/logo";



interface AuthProps {
  onLogin: (userData: { name: string; email: string; token: string }) => void;
}

export function Auth({ onLogin }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    gender: '',
    birthDate: '',
    phone: ''
  });

  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkIfMobile();
    window.addEventListener('resize', checkIfMobile);
    return () => window.removeEventListener('resize', checkIfMobile);
  }, []);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    setTouchStart(e.targetTouches[0].clientX);
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  }, []);

  const handleTouchEnd = useCallback(() => {
    if (touchStart - touchEnd > 50) {
      setActiveSlide(1);
    }

    if (touchStart - touchEnd < -50) {
      setActiveSlide(0);
    }
  }, [touchStart, touchEnd]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const response = await fetch('http://localhost:8000/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          onLogin({
            name: data.user?.first_name ? `${data.user.first_name} ${data.user.last_name}` : 'Usuário',
            email: formData.email,
            token: data.access_token,
          });
        } else {
          const error = await response.json();
          alert(error.detail || 'Erro ao fazer login');
        }
      } else {
        // Validate required fields for registration
        if (!formData.firstName.trim() || !formData.lastName.trim()) {
          alert('Nome e sobrenome são obrigatórios');
          return;
        }
        
        if (formData.password !== formData.confirmPassword) {
          alert('As senhas não coincidem');
          return;
        }

        const response = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            first_name: formData.firstName,
            last_name: formData.lastName,
            email: formData.email,
            password: formData.password,
            gender: formData.gender || null,
            birth_date: formData.birthDate || null,
            phone: formData.phone || null,
          }),
        });

        if (response.ok) {
          const loginResponse = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: formData.email,
              password: formData.password,
            }),
          });

          if (loginResponse.ok) {
            const data = await loginResponse.json();
            onLogin({
              name: `${formData.firstName} ${formData.lastName}`,
              email: formData.email,
              token: data.access_token,
            });
          }
        } else {
          const error = await response.json();
          alert(error.detail || 'Erro ao criar conta');
        }
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro de conexão. Verifique se o servidor está rodando.');
    } finally {
      setLoading(false);
    }
  }, [isLogin, formData, onLogin]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  }, []);

  const togglePasswordVisibility = useCallback(() => {
    setShowPassword(prev => !prev);
  }, []);

  const toggleAuthMode = useCallback(() => {
    setIsLogin(prev => !prev);
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      gender: '',
      birthDate: '',
      phone: ''
    });
  }, []);

  const handleForgotPassword = useCallback(() => {
    alert('Funcionalidade de recuperação de senha será implementada em breve!');
  }, []);

  // Componente do formulário reutilizável - Memoizado para evitar re-renders
  const AuthForm = useMemo(() => {
    return (
      <form onSubmit={handleSubmit} className="space-y-6 flex-1 flex flex-col">
        <div className="space-y-4 flex-1">
          {!isLogin && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nome
                  </label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    required
                    autoComplete="given-name"
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sobrenome
                  </label>
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    required
                    autoComplete="family-name"
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gênero
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                >
                  <option value="">Selecione</option>
                  <option value="masculino">Masculino</option>
                  <option value="feminino">Feminino</option>
                  <option value="outro">Outro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data de nascimento
                </label>
                <input
                  type="date"
                  name="birthDate"
                  value={formData.birthDate}
                  onChange={handleInputChange}
                  className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Telefone
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  autoComplete="tel"
                  className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              autoComplete="email"
              className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Senha
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                className="w-full px-4 py-4 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 p-2"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmar senha
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
                autoComplete="new-password"
                className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
              />
            </div>
          )}
        </div>

        <div className="space-y-4 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-base"
          >
            {loading ? 'Carregando...' : (isLogin ? 'Entrar' : 'Criar conta')}
          </button>

          {isLogin && (
            <button
              type="button"
              onClick={handleForgotPassword}
              className="w-full text-blue-600 hover:text-blue-700 font-medium py-2 text-sm"
            >
              Esqueceu sua senha?
            </button>
          )}

          <button
            type="button"
            onClick={toggleAuthMode}
            className="w-full text-blue-600 hover:text-blue-700 font-medium py-2"
          >
            {isLogin ? 'Não tem uma conta? Cadastre-se' : 'Já tem uma conta? Entre'}
          </button>
        </div>
      </form>
    );
  }, [isLogin, formData, loading, showPassword, handleSubmit, handleInputChange, togglePasswordVisibility, toggleAuthMode, handleForgotPassword]);

  // Desktop Layout (side by side)
  if (!isMobile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
        <div className="max-w-6xl w-full grid lg:grid-cols-2 gap-8 items-center">
          {/* Left side - Branding */}
          <div className="text-center lg:text-left space-y-8">
            <div className="space-y-4">
              <div className="flex justify-center lg:justify-start">
                <Logo size="lg" showText={true} />
              </div>
              <p className="text-xl text-gray-600 max-w-md">
                Conecte-se com pessoas genuínas e compartilhe boas vibes
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-md mx-auto lg:mx-0">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <p className="text-sm text-gray-600">Conecte-se com amigos</p>
              </div>
              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto">
                  <MessageCircle className="w-6 h-6 text-purple-600" />
                </div>
                <p className="text-sm text-gray-600">Converse em tempo real</p>
              </div>
              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto">
                  <Sparkles className="w-6 h-6 text-indigo-600" />
                </div>
                <p className="text-sm text-gray-600">Compartilhe momentos</p>
              </div>
            </div>
          </div>

          {/* Right side - Auth Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md mx-auto w-full">
            <div className="text-center mb-8">
              <div className="flex justify-center mb-4">
                <Logo size="md" showText={false} />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {isLogin ? 'Entrar' : 'Criar conta'}
              </h2>
              <p className="text-gray-600">
                {isLogin ? 'Bem-vindo de volta!' : 'Junte-se à nossa comunidade'}
              </p>
            </div>

            {AuthForm}
          </div>
        </div>
      </div>
    );
  }

  // Mobile Layout - Tela cheia com slides
  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex flex-col overflow-hidden">
      {/* Mobile navigation dots */}
      <div className="flex justify-center pt-4 pb-2 space-x-2 flex-shrink-0">
        <button
          onClick={() => setActiveSlide(0)}
          className={`w-2 h-2 rounded-full transition-colors ${
            activeSlide === 0 ? 'bg-blue-600' : 'bg-gray-300'
          }`}
        />
        <button
          onClick={() => setActiveSlide(1)}
          className={`w-2 h-2 rounded-full transition-colors ${
            activeSlide === 1 ? 'bg-blue-600' : 'bg-gray-300'
          }`}
        />
      </div>

      {/* Slides container - Ocupa toda a altura restante */}
      <div className="flex-1 relative overflow-hidden">
        {/* Mobile navigation arrows */}
        <div className="absolute top-1/2 left-0 right-0 z-10 flex justify-between px-4 transform -translate-y-1/2 pointer-events-none">
          <button
            onClick={() => setActiveSlide(0)}
            className={`p-2 rounded-full bg-white shadow-md transition-opacity pointer-events-auto ${
              activeSlide === 0 ? 'opacity-0 pointer-events-none' : 'opacity-100'
            }`}
          >
            <ChevronLeft className="w-5 h-5 text-blue-600" />
          </button>
          <button
            onClick={() => setActiveSlide(1)}
            className={`p-2 rounded-full bg-white shadow-md transition-opacity pointer-events-auto ${
              activeSlide === 1 ? 'opacity-0 pointer-events-none' : 'opacity-100'
            }`}
          >
            <ChevronRight className="w-5 h-5 text-blue-600" />
          </button>
        </div>

        <div
          className="flex h-full transition-transform duration-300 ease-in-out"
          style={{ transform: `translateX(-${activeSlide * 100}%)` }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          {/* Slide 1 - Branding - Tela cheia */}
          <div className="min-w-full h-full flex flex-col justify-center px-6 py-8">
            <div className="text-center space-y-8 max-w-md mx-auto">
              <div className="flex justify-center">
                <Logo size="lg" showText={true} />
              </div>
              
              <p className="text-xl text-gray-600">
                Conecte-se com pessoas genuínas e compartilhe boas vibes
              </p>

              <div className="grid grid-cols-1 gap-6">
                <div className="text-center space-y-2">
                  <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto">
                    <Users className="w-8 h-8 text-blue-600" />
                  </div>
                  <p className="text-gray-600">Conecte-se com amigos</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mx-auto">
                    <MessageCircle className="w-8 h-8 text-purple-600" />
                  </div>
                  <p className="text-gray-600">Converse em tempo real</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto">
                    <Sparkles className="w-8 h-8 text-indigo-600" />
                  </div>
                  <p className="text-gray-600">Compartilhe momentos</p>
                </div>
              </div>

              <div className="pt-8">
                <button
                  onClick={() => setActiveSlide(1)}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 text-lg"
                >
                  Começar
                </button>
              </div>
            </div>
          </div>

          {/* Slide 2 - Auth Form - Tela cheia */}
          <div className="min-w-full h-full flex flex-col bg-white">
            {/* Header fixo */}
            <div className="bg-white shadow-sm px-6 py-4 flex items-center justify-between border-b flex-shrink-0">
              <button
                onClick={() => setActiveSlide(0)}
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="text-center">
                <h2 className="text-lg font-bold text-gray-900">
                  {isLogin ? 'Entrar' : 'Criar conta'}
                </h2>
              </div>
              <div className="w-9"></div> {/* Spacer para centralizar o título */}
            </div>

            {/* Formulário que ocupa toda a altura restante */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto">
                <div className="p-6 h-full flex flex-col">
                  {/* Logo e mensagem no topo */}
                  <div className="text-center mb-8 pt-4">
                    <div className="flex justify-center mb-4">
                      <Logo size="md" showText={false} />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {isLogin ? 'Entrar' : 'Criar conta'}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {isLogin ? 'Bem-vindo de volta!' : 'Junte-se à nossa comunidade'}
                    </p>
                  </div>

                  {/* Formulário centralizado */}
                  <div className="flex-1 flex flex-col justify-center">
                    {AuthForm}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
# Vibe - Rede Social

Uma rede social moderna e intuitiva construída com React e FastAPI.

## 🚀 Funcionalidades

### Front-end (React)
- **Autenticação**: Sistema completo de login e cadastro
- **Feed Interativo**: Visualização de posts e depoimentos
- **Criação de Conteúdo**: Modal para criar posts e depoimentos com editor rico
- **Perfil de Usuário**: Seções para posts e depoimentos recebidos
- **Interações Sociais**: Curtir, amar, comentar e responder comentários
- **Design Responsivo**: Interface adaptável para todos os dispositivos

### Back-end (FastAPI)
- **API RESTful**: Endpoints organizados por funcionalidade
- **Autenticação JWT**: Sistema seguro de autenticação
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **Validação**: Pydantic para validação de dados
- **Documentação**: Swagger UI automática

## 🛠️ Tecnologias Utilizadas

### Front-end
- React 18 com TypeScript
- Tailwind CSS para estilização
- Lucide React para ícones
- React Router para navegação

### Back-end
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite Database
- JWT para autenticação
- Pydantic para validação

## 📦 Instalação

### Front-end
```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

### Back-end
```bash
# Navegar para o diretório do backend
cd backend

# Instalar dependências
pip install -r requirements.txt

# Executar o servidor
python run.py
```

## 🌟 Funcionalidades Principais

### Posts e Depoimentos
- Criação de posts simples
- Depoimentos com formatação rica (negrito, itálico, sublinhado)
- Pré-visualização em tempo real para depoimentos
- Opção de adicionar mídia e marcar amigos

### Interações Sociais
- Sistema de curtidas e reações "amei"
- Comentários com suporte a respostas
- Compartilhamento de posts
- Salvar posts favoritos

### Perfil de Usuário
- Informações pessoais editáveis
- Seção de posts criados
- Seção de depoimentos recebidos
- Estatísticas de engajamento

## 🎨 Design

O Vibe possui um design moderno e atrativo com:
- Paleta de cores vibrante (roxo, rosa, laranja)
- Logomarca exclusiva com gradientes
- Animações suaves e micro-interações
- Layout responsivo e acessível

## 📱 Uso

1. **Cadastro/Login**: Crie sua conta ou faça login
2. **Feed**: Visualize posts da comunidade
3. **Criar Post**: Clique em "No que você está pensando?" para criar conteúdo
4. **Interagir**: Curta, comente e compartilhe posts
5. **Perfil**: Acesse seu perfil para ver seus posts e depoimentos

## 🔧 Configuração da API

A API roda por padrão em `http://localhost:8000` e inclui:
- `/docs` - Documentação interativa (Swagger)
- `/redoc` - Documentação alternativa
- Endpoints organizados por funcionalidade

## 🚀 Deploy

### Front-end
```bash
npm run build
```

### Back-end
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📄 Licença

Este projeto está sob licença MIT.

## 👥 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Submeter pull requests

---

Desenvolvido com ❤️ para conectar pessoas através de boas vibes!
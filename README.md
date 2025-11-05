# Pokedex API

Projeto de Pokedex que consulta dados da [PokeAPI](https://pokeapi.co/), uma API pública com informações completas sobre Pokémons. Este backend fornece uma interface estruturada para acessar e gerenciar dados de Pokémons, incluindo suas características, evoluções e relacionamentos.

## 🎮 Funcionalidades Principais

### Dados de Pokémons

A aplicação fornece acesso a informações detalhadas sobre cada Pokémon:

- **Flavor Text**: Descrição em inglês do Pokémon
- **Altura**: Altura do Pokémon em decímetros
- **Peso**: Peso do Pokémon em hectogramas
- **Habilidades**: Lista de habilidades ordenadas alfabeticamente
- **Tipos**: Tipos do Pokémon (ex: grass, fire, water) ordenados alfabeticamente
- **Sprites**: Imagens oficiais do Pokémon (versão normal e shiny)
- **Cadeia de Evolução**: Relacionamento evolutivo completo do Pokémon

### Busca e Navegação

- **Listagem Navegável**: Lista paginada de Pokémons com navegação entre páginas
- **Busca por Nome**: Pesquisa de Pokémons por nome (case-insensitive)

### Autenticação e Usuários

- **Registro de Usuário**: Criação de conta pública com primeiro nome, segundo nome, email e senha
- **Login**: Autenticação via JWT (JSON Web Tokens)
- **Favoritar Pokémons**: Sistema para marcar Pokémons como favoritos

### Sistema de Cache Inteligente

A aplicação implementa uma camada de cache no backend para otimizar o desempenho:

1. **Busca na Base de Dados**: Primeiro verifica se o Pokémon existe no banco local
2. **Validação de Atualização**: Se encontrado, verifica se foi atualizado na última semana
3. **Atualização Automática**: Se não encontrado ou desatualizado (>7 dias), busca na PokeAPI
4. **Armazenamento**: Salva o JSON completo retornado pela PokeAPI no banco de dados
5. **Acesso Rápido**: Caso contrário, retorna diretamente da base de dados

Esta estratégia reduz chamadas desnecessárias à API externa e melhora a performance da aplicação.

## 🛠️ Tecnologias

- **Backend**: Django (framework web Python)
- **API REST**: Django REST Framework
- **Banco de Dados**: PostgreSQL
- **Cache e Filas**: Redis
- **Tarefas Assíncronas**: Celery (scheduler configurado, mas não utilizado atualmente)
- **Containerização**: Docker e Docker Compose
- **Autenticação**: JWT (JSON Web Tokens)

## 🏗️ Arquitetura

### Estrutura de Aplicações Django

#### App `pokemons` (Principal)

Aplicação principal que gerencia todos os dados relacionados a Pokémons:

- **`models.py`**: Definição dos models principais:

  - `Pokemon`: Model principal com propriedades para acessar dados formatados do JSON
  - `PokemonSpecie`: Informações sobre a espécie do Pokémon
  - `PokemonEvolutionChain`: Cadeias de evolução compartilhadas por múltiplas espécies

- **`services.py`**: Classe `PokeApiService` para comunicação estruturada com a PokeAPI

  - Métodos organizados para diferentes endpoints da API
  - Centraliza toda a lógica de chamadas HTTP à API externa

- **`helpers.py`**: Centraliza a lógica principal da aplicação

  - Helpers para buscar, criar e atualizar Pokémons
  - Implementação da estratégia de cache
  - Coordenação entre banco de dados e API externa

- **`views.py`**: Endpoints da API REST

  - Views para listagem, busca e detalhes de Pokémons
  - Integração com serializers para formatação de respostas

- **`serializers.py`**: Serialização de dados para a API
  - Formatação de respostas JSON
  - Validação de dados de entrada

#### App `authentication`

Gerenciamento de autenticação e tokens:

- Registro de novos usuários
- Login e geração de tokens JWT
- Refresh de tokens
- Troca de tokens Google OAuth (opcional)

#### App `users`

Gerenciamento de usuários:

- Model de usuário customizado
- Serializers para manipulação de dados de usuários
- Permissões e grupos

#### App `common`

Utilitários compartilhados:

- Modelos abstratos reutilizáveis
- Funções auxiliares
- Utilitários para requisições HTTP

## 📦 Armazenamento de Dados

A base de dados armazena o JSON completo retornado pela PokeAPI no campo `data` de cada modelo. Isso facilita:

- **Estruturação Flexível**: Manipulação dos dados apenas manipulando o JSON
- **Versionamento**: Manter histórico completo dos dados da API
- **Performance**: Evitar múltiplas chamadas à API externa
- **Propriedades Computadas**: Models Python podem criar propriedades que extraem e formatam dados específicos do JSON

Exemplo: O model `Pokemon` possui propriedades como `abilities`, `height`, `weight`, `types`, `sprites` que extraem dados do JSON armazenado e os formatam de forma conveniente.

## 🚀 Como Iniciar o Projeto

### Pré-requisitos

- Docker e Docker Compose instalados
- Make (opcional, mas recomendado)

### Configuração Inicial

1. **Clone o repositório** (se ainda não tiver feito)

2. **Configure as variáveis de ambiente**:

   ```bash
   cp .env.example .env
   ```

   Edite o arquivo `.env` com os mesmos valores do `.env.example`, ajustando conforme necessário para seu ambiente.

3. **Inicie o projeto em modo desenvolvimento**:

   ```bash
   make watch
   ```

   Este comando irá:

   - Parar containers existentes
   - Subir os serviços (principal, postgres, scheduler, redis)
   - Baixar automaticamente os requirements
   - Iniciar o servidor na porta **8882**
   - Exibir logs em tempo real

### Acessos

- **API**: `http://localhost:8882/api/`
- **Admin Django**: `http://localhost:8882/admin/` (para desenvolvedores)
- **Documentação Swagger**: `http://localhost:8882/api/docs/`
- **Documentação ReDoc**: `http://localhost:8882/api/redoc/`

## 🐳 Estrutura Docker

O projeto utiliza Docker Compose com os seguintes serviços:

- **pokeapi-service**: Serviço principal Django (porta 8882)
- **postgres**: Banco de dados PostgreSQL
- **pokeapi-scheduler**: Serviço Celery para tarefas agendadas (não utilizado atualmente, mas útil para futuras implementações)
- **redis**: Cache e broker de mensagens para Celery

## 📝 Endpoints Principais

### Autenticação

- `POST /api/auth/register/` - Registro de novo usuário
- `POST /api/auth/token/obtain/` - Obter tokens JWT (login)
- `POST /api/auth/token/refresh/` - Atualizar access token
- `GET /api/auth/user/` - Informações do usuário autenticado

### Pokémons

- `GET /api/pokemons/pokemons/` - Lista paginada de Pokémons
- `GET /api/pokemons/pokemons/{pokemon_name_or_id}/` - Detalhes de um Pokémon específico
- `POST /api/pokemons/pokemons/{pokemon_name_or_id}/favorite/` - Favoritar um Pokémon
- `POST /api/pokemons/pokemons/{pokemon_name_or_id}/unfavorite/` - Remover dos favoritos
- `POST /api/pokemons/favorited-pokemons/` - Lista paginada de Pokémons favoritos
- `GET /api/pokemons/evolution-chains/{pokemon_name_or_id}/` - Cadeia de evolução de um Pokémon

## 🔧 Comandos Úteis

```bash
# Iniciar projeto e ver logs
make watch

# Parar containers
make stop

# Parar e remover volumes
make down

# Rebuild containers
make build

# Acessar shell do container principal
make bash

# Ver logs do serviço
make service-logs

# Ver logs do scheduler
make scheduler-logs
```

## 📚 Documentação da API

A documentação completa da API está disponível em:

- **Swagger UI**: `http://localhost:8882/api/docs/`
- **ReDoc**: `http://localhost:8882/api/redoc/`
- **Schema OpenAPI**: `http://localhost:8882/api/schema/`

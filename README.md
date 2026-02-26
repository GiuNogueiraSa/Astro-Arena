🚀 Astro-Arena: Documentação de Projeto

1. Visão Geral
Astro-Arena é um jogo de combate de arena baseado em física, onde a inércia é sua maior aliada e sua pior inimiga. O objetivo é simples: ser o último círculo dentro da zona de combate.

Gênero: Arcade / Physics-based Combat.
Plataforma: Web (GitHub Pages).
Motor: Python + Pygame-ce.

2. Mecânicas Principais (Core Mechanics)
A diversão do jogo reside na fórmula do momento linear:
p = m * v
Onde p é a força do impacto, m é a massa da sua nave e v é a velocidade no momento do choque.

O Dash (Arrancada): A única forma de ataque. O jogador acumula energia e dispara em uma direção.
Colisão Elástica: Ao colidir, a energia é transferida. Se você atingir um inimigo parado enquanto está em alta velocidade, ele será arremessado longe.
Sistema de Massa: Ao derrotar inimigos, sua nave absorve "poeira estelar", aumentando sua massa (m). Isso torna você mais difícil de ser empurrado, mas mais lento para acelerar.
Arena Dinâmica: As bordas podem ser elásticas (estilo "pinball") ou inexistentes (quem sair da tela perde).

3. Stack Técnica e Fluxo de Trabalho
Configuração do Repositório:
- Main Branch: Versão estável que será exibida no GitHub Pages.
- Dev Branch: Onde você fará os testes das novas ondas e inimigos.

Deploy via GitHub Pages:
Utilizaremos Pygbag para compilar o código Python para HTML5/WASM.
Sempre que você der "Push" no GitHub Desktop, o script compila o código Python para HTML5 via GitHub Actions.

4. Estrutura de Pastas Sugerida
astro-arena/
├── assets/             # Sprites de naves, sons de impacto e trilha lo-fi
├── src/                # Código fonte
│   ├── main.py         # Loop principal do jogo
│   ├── entities.py     # Classes de Jogador e Inimigos
│   └── physics.py      # Cálculos de colisão e dash
└── README.md           # Esta documentação

5. Como Usar

### Versionamento com GitHub Desktop
1. Abra o **GitHub Desktop**.
2. Vá em `File > Add Local Repository...` e selecione a pasta `Astro-Arena`.
3. Faça o seu primeiro commit com a mensagem "Initial game setup".
4. Clique em **Publish repository** para subir para o seu GitHub.
5. Verifique se a branch principal se chama `main`.

### Deploy Automático
O projeto já conta com uma **GitHub Action** configurada. Sempre que você fizer um `Push` para a branch `main`, o jogo será compilado e enviado para a branch `gh-pages` automaticamente. O link será: `https://seu-usuario.github.io/astro-arena/`.

### Teste Local
Para rodar o jogo no seu computador:
1. Instale o Pygame: `pip install pygame-ce` (ou `pygame`).
2. Execute o comando: `python main.py`.

Para testar a versão Web localmente:
1. Instale o Pygbag: `pip install pygbag`.
2. Execute: `pygbag .` e acesse `http://localhost:8000` no navegador.

6. Roadmap de Desenvolvimento
Fase 01: Criar círculo que se move com física básica. [Concluído ✅]
Fase 02: Implementar mecânica de Dash com cooldown. [Concluído ✅]
Fase 03: Add primeiro inimigo (IA de perseguição simples). [Concluído ✅]
Fase 04: Sistema de colisão e "morte" por sair da arena. [Concluído ✅]
Fase 05: Deploy inicial no GitHub Pages. [Configurado 🚀]

🚀 Astro-Arena: Battle Edition

1. Visão Geral
Astro-Arena evoluiu para um jogo de combate espacial frenético. Agora, você não apenas empurra seus inimigos, mas utiliza canhões lasers para destruí-los e avançar pelas fases.

2. Mecânicas Principais (Core Mechanics)
- **Sistema de Tiro**: O Dash foi substituído por disparos de energia. Use `ESPAÇO` ou `MOUSE` para atirar.
- **Física de Inércia**: A nave mantém o movimento, exigindo habilidade para navegar e mirar.
- **Progressão por Fases**: Complete 3 níveis com dificuldade progressiva.
- **Visual Espacial**: Fundo com estrelas em paralaxe e naves com design geométrico moderno.

3. Controles
- **WASD ou Setas**: Movimentação e rotação.
- **Espaço ou Clique Esquerdo**: Atirar.
- **Menu**: Clique em INICIAR para começar ou SAIR para fechar.

4. Roadmap de Desenvolvimento
Fase 01: Movimento e Tiro básico. [Concluído ✅]
Fase 02: Design de Naves e Estrelas. [Concluído ✅]
Fase 03: Sistema de 3 Fases e Menus. [Concluído ✅]
Fase 04: IA agressiva e efeitos de impacto. [Concluído ✅]
Fase 05: Deploy Web atualizado. [Pronto 🚀]

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

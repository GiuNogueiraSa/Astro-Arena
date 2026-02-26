# 🚀 Astro-Arena: Documentação de Projeto

## 1. Visão Geral
Astro-Arena é um jogo de combate de arena baseado em física, onde a inércia é sua maior aliada e sua pior inimiga. O objetivo é simples: ser o último círculo dentro da zona de combate.

**Gênero:** Arcade / Physics-based Combat.  
**Plataforma:** Web (GitHub Pages).  
**Motor:** Python + Antigravity (Pygame-ce).

## 2. Mecânicas Principais (Core Mechanics)
A diversão do jogo reside na fórmula do momento linear:
$$p = m \cdot v$$
Onde $p$ é a força do impacto, $m$ é a massa da sua nave e $v$ é a velocidade no momento do choque.

- **O Dash (Arrancada):** A única forma de ataque. O jogador acumula energia e dispara em uma direção.
- **Colisão Elástica:** Ao colidir, a energia é transferida. Se você atingir um inimigo parado enquanto está em alta velocidade, ele será arremessado longe.
- **Sistema de Massa:** Ao derrotar inimigos, sua nave absorve "poeira estelar", aumentando sua massa ($m$). Isso torna você mais difícil de ser empurrado, mas mais lento para acelerar.
- **Arena Dinâmica:** As bordas podem ser elásticas (estilo "pinball") ou inexistentes (quem sair da tela perde).

## 3. Stack Técnica e Fluxo de Trabalho
Para manter seu projeto organizado no GitHub Desktop, seguiremos esta estrutura:

### Configuração do Repositório
- **Main Branch:** Versão estável que será exibida no GitHub Pages.
- **Dev Branch:** Onde você fará os testes das novas ondas e inimigos.

### Deploy via GitHub Pages
Como o Antigravity/Pygame roda no navegador através do WebAssembly (Wasm), utilizaremos uma GitHub Action para automatizar o deploy:
1. Sempre que você der "Push" no GitHub Desktop, o script compila o código Python para HTML5.
2. O resultado vai direto para o link `seu-usuario.github.io/astro-arena/`.

## 4. Estrutura de Pastas Sugerida
```plaintext
astro-arena/
├── assets/             # Sprites de naves, sons de impacto e trilha lo-fi
├── src/                # Código fonte
│   ├── main.py         # Loop principal do jogo
│   ├── entities.py     # Classes de Jogador e Inimigos
│   └── physics.py      # Cálculos de colisão e dash
├── index.html          # Gerado pelo build do Antigravity
└── README.md           # Esta documentação
```

## 5. Roadmap de Desenvolvimento
| Fase | Meta | Status |
| :--- | :--- | :--- |
| 01 | Criar círculo que se move com física básica. | ⏳ Pendente |
| 02 | Implementar mecânica de Dash com cooldown. | ⏳ Pendente |
| 03 | Adicionar primeiro inimigo (IA de perseguição simples). | ⏳ Pendente |
| 04 | Sistema de colisão e "morte" por sair da arena. | ⏳ Pendente |
| 05 | Deploy inicial no GitHub Pages. | ⏳ Pendente |

---

### 💡 Dica de Ouro para o "Pulo do Gato"
Para o impacto ser satisfatório, use **Screen Shake** (tremidinha na tela) e **Partículas** que voam das naves no momento da batida. No Antigravity, isso é fácil de implementar e muda completamente a percepção de "peso" do jogo.

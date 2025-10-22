# AutoClicker Pro

Auto-clicker moderno e customizável com interface gráfica minimalista. Permite fazer cliques automáticos ao segurar o botão do mouse, com controle total sobre a velocidade e configurações avançadas.

## Funcionalidades

- **Interface Moderna**: Design minimalista e dark mode com CustomTkinter
- **Controle de Velocidade**: Slider para ajustar de 1 a 50 clicks por segundo
- **Ativar/Desativar**: Clique no botão do scroll (botão do meio) para alternar o modo auto-click
- **Atalhos Customizáveis**: Configure seu próprio atalho de teclado
- **Auto-Click**: Quando ativado, segure o botão do mouse (esquerdo ou direito) para fazer cliques automáticos
- **Botão Direito**: Opção para habilitar auto-click também no botão direito
- **System Tray**: Minimize o programa para a bandeja do sistema
- **Configurações Persistentes**: Suas preferências são salvas automaticamente

## Instalação

1. Clone o repositório ou baixe os arquivos

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Interface Gráfica (Recomendado)

Execute a interface gráfica:
```bash
python gui.py
```

### Modo Console

Execute o script sem interface:
```bash
python auto_clicker.py
```

## Configuração

### Via Interface Gráfica

Todas as configurações podem ser ajustadas diretamente na interface:
- **CPS Range**: Use o slider para ajustar de 1 a 50 clicks/segundo (recomendado: 20)
- **Botão Direito**: Ative o switch para habilitar auto-click no botão direito
- **Minimizar para Bandeja**: Ative para esconder o programa na system tray
- **Atalho de Teclado**: Digite o atalho desejado (ex: `<ctrl>+<shift>+a`)

### Arquivo de Configuração

As configurações são salvas automaticamente em `config.json`:
```json
{
    "cps": 20,
    "enable_right_click": false,
    "hotkey": "<ctrl>+<shift>+a",
    "hide_on_minimize": false
}
```

## Como Usar

1. Inicie o programa executando `python gui.py`
2. Ajuste o slider de CPS para a velocidade desejada
3. Clique no **botão do scroll** do mouse ou use o **atalho de teclado** para ativar
4. Quando ativado, **segure o botão esquerdo** (ou direito, se habilitado) para fazer cliques automáticos
5. Solte o botão para parar os cliques
6. Clique no botão do scroll novamente para desativar o modo auto-click

## Requisitos

- Python 3.7+
- pynput 1.7.6
- customtkinter 5.2.1
- pillow 10.1.0
- pystray 0.19.5

## Arquitetura

- [gui.py](gui.py) - Interface gráfica com CustomTkinter
- [auto_clicker.py](auto_clicker.py) - Core do auto-clicker (pode ser usado standalone)
- [config.json](config.json) - Arquivo de configurações (gerado automaticamente)

## Aviso

Use este programa de forma responsável e ética. Não utilize em:
- Jogos online onde auto-clickers sejam contra os termos de serviço
- Aplicações onde possa violar políticas de uso
- Situações que possam prejudicar outros usuários

O uso deste software é de sua total responsabilidade.

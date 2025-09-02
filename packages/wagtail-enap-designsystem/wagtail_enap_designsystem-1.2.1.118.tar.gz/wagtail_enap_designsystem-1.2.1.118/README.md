# 🏗️ ENAP Design System

Sistema de design baseado em Wagtail e Django, criado para padronizar e reutilizar componentes em diversos projetos.


### 🛫 Outros READMEs
 README.md, doc geral do projeto [README.md](README.md) [ATUAL]
 README-use.md, doc do uso do módulo [README-use.md](README-use.md)
 README-pypi.md, doc subir pacote pypi [README-pypi.md](README-pypi.md)

--- 

## 🛠️ Pré-requisitos

Certifique-se de ter instalados:
- **Python 3.13+**
- **Git** (devidamente configurado)

---

## 🔧 Configuração do Git no Windows

Se você nunca usou Git antes, siga os passos abaixo para instalá-lo e configurá-lo no Windows:

### **1. Instalar o Git**
1. Acesse o site oficial: [git-scm.com](https://git-scm.com/)
2. Baixe a versão mais recente para Windows.
3. Execute o instalador e **mantenha as opções padrão**.
4. Após a instalação, abra o **Prompt de Comando (cmd)** ou o **PowerShell** e digite:
   ```bash
   git --version
   ```
   Se aparecer algo como `git version X.Y.Z`, significa que o Git foi instalado corretamente.

### **2. Configurar seu Nome e E-mail** *(Necessário para autenticação e commits)*

Digite os seguintes comandos, substituindo pelas suas informações:
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"
```

### **3. Configurar a Autenticação com o GitHub ou GitLab** *(Se necessário SSH)*

Se o repositório exigir autenticação via SSH:
1. Gere uma chave SSH:
   ```bash
   ssh-keygen -t ed25519 -C "seu-email@example.com"
   ```
2. Copie sua chave pública:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. Adicione essa chave ao GitHub ou GitLab nas configurações de SSH.
4. Teste a conexão:
   ```bash
   ssh -T git@github.com
   ```

##### Caso o repositório use HTTPS, o Git pedirá seu usuário e senha na primeira vez.

---

### 📘 **Aprenda os Comandos Básicos do Git**
Para aprender mais sobre comandos essenciais do Git, veja:
- [freeCodeCamp (10 comandos)](https://www.freecodecamp.org/portuguese/news/10-comandos-do-git-que-todo-desenvolvedor-deveria-conhecer/)
- [gist de comandos úteis](https://gist.github.com/leocomelli/2545add34e4fec21ec16)
- [somostera (15 comandos)](https://blog.somostera.com/desenvolvimento-web/comandos-git)
- Também existem programas com interface gráfica (GUI) para trabalhar com Git, facilitando a visualização do que está acontecendo. Além disso, o próprio Visual Studio Code possui extensões para Git.
---

## 🚀 Ambiente de Desenvolvimento

### **1. Clonar o Repositório**
```bash
# git clone: Este comando baixa o projeto e cria automaticamente uma pasta com o nome do repositório.
git clone https://gitlab.enap.gov.br/cgti-sistemas/estrategia-de-portais-design-system.git

# Entre no diretório criado:
cd estrategia-de-portais-design-system
```

### **2. Criar e Ativar o Ambiente Virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows (Powershell)
```

### **3. Instalar Dependências** (na raiz do projeto)
```bash
# Instala dependencias do módulo e do sandbox
pip install -r requirements.txt
```

---

## 📂 **Estrutura do Projeto**

```
estrategia-de-portais-design-system/
├── enap_designsystem/          # Módulo principal do ENAP Design System
│   ├── __init__.py                 # Arquivo para tornar o diretório um módulo Python
│   ├── apps.py                     # Configuração da aplicação Django
│   ├── models.py                   # Modelos de banco de dados (Django ORM)
│   ├── requirements.txt            # Dependências principais da aplicação
│   ├── settings.py                 # Configuração principal (base de settings)
│   ├── wagtail_hooks.py            # Hooks para personalizar o painel do Wagtail
│   │
│   ├── blocks/                     # Blocos personalizados usados pelo Wagtail
│   │   ├── __init__.py             # Marca a pasta como módulo Python
│   │   ├── base_blocks.py          # Blocos reutilizáveis comuns
│   │   ├── content_blocks.py       # Blocos de conteúdo (texto, imagem, vídeo)
│   │   ├── html_blocks.py          # Blocos para conteúdo HTML personalizado
│   │   └── layout_blocks.py        # Blocos de layout (colunas, seções)
│   │
│   ├── migrations/                 # Histórico de alterações no banco de dados
│   │   ├── __init__.py             
│   │   ├── 0001_initial.py         
│   │   └── ... .py
│   │
│   ├── static/                     # Arquivos estáticos como CSS e JS
│   │   └── enap_designsystem/
│   │       ├── css/                # Arquivos CSS personalizados
│   │       │   ├── main_layout.css  # Estilo principal
│   │       │   └── mid_layout.css   # Estilo para layout intermediário
│   │       │
│   │       └── js/                 # Scripts JavaScript
│   │           ├── main_layout.js   # Lógica do layout principal
│   │           └── mid_layout.js    # Lógica do layout intermediário
│   │
│   └── templates/                  # Templates HTML usados pelo Django/Wagtail
│       └── enap_designsystem/
│           ├── base.html            # Template base com estrutura padrão
│           ├── main_layout.html     # Template para layout principal
│           ├── mid_layout.html      # Template para layout intermediário
│           │
│           ├── blocks/              # Templates específicos de blocos
│           │   └── button_block.html # Template do bloco de botão
│           │
│           └── pages/               # Templates de páginas principais
│               ├── enap_layout.html  # Página principal com layout ENAP
│               └── root_page.html    # Página raiz
│
├── setup.py                        # Configuração do pacote para o PyPI
├── MANIFEST.in                     # Garante que arquivos estáticos e templates sejam incluídos
├── LICENSE                         # Arquivo com a licença do projeto, definindo os termos de uso, distribuição e atribuição
├── README.md                       # Este arquivo 📄
│
└── wagtail_sandbox/            # Projeto sandbox para testes locais do módulo
                                # Contém um projeto Wagtail completo para testar
                                # as funcionalidades do módulo `enap_designsystem`.

```

---

## 🧪 Executando o Sandbox (`wagtail_sandbox`)

### **1. Configurar as Variáveis de Ambiente**
Entre na pasta `wagtail_sandbox`

```bash
# Todos os comandos a seguir deverão ser executados
# dentro da pasta wagtail_sandbox
cd wagtail_sandbox
```

### **2. Executar Migrações**
```bash
# Alterações no enap_designsystem também precisarão rodar esse comando aqui,
# Pelo projeto enap_designsystem não ter um manage.py próprio, é necessário
# utilizar o sandbox para criar as migrations dele.
python manage.py makemigrations enap_designsystem
python manage.py migrate
```

### **3. Criar um Superusuário**
```bash
python manage.py createsuperuser
```

### **4. Rode o `collectstatic` para garantir que os arquivos CSS/JS sejam carregados corretamente:**
```bash
python manage.py collectstatic
```

### **5. Rode o build do SASS**
```
python manage.py sass -g website/static/website/src/custom.scss website/static/website/css/
```
### **6. Iniciar o Servidor**
```bash
python manage.py runserver
```

Acesse no navegador: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**  
Admin Wagtail: **[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)**

---

### Comandos úteis (Makefile)
Os comandos a seguir devem ser executados dentro de ".../wagtail_sandbox"

- `make dev` — roda o servidor local
- `make build-css` — gera o arquivo bundle.css agrupado do módulo em "enap_designsystem/static/enap_designsystem/blocks/bundle.css"
- `make makemigrations-enap` — cria migrações do módulo enap_designsystem
- `make migrate` — aplica as migrações
- `make createsuperuser` — cria um superusuário
- `make shell` — entra no modo shell do python
- `make clean` — limpa arquivos temporários
- `make collectstatic` — roda o comando "py manage.py collectstatic --noinput"


> Requer [Make instalado](https://www.gnu.org/software/make/) (já incluso em Linux/macOS e disponível via Git Bash no Windows).

---

## 📌 Gitflow - Fluxo de Trabalho

Para manter um controle eficiente do código e organizar o desenvolvimento do projeto, utilizamos o **Gitflow**.

#### **O que é Gitflow?**
Gitflow é um fluxo de trabalho baseado no Git que facilita a colaboração entre desenvolvedores e a organização do ciclo de vida do código. Ele define um conjunto de regras para criar branches e gerenciar versões do software de maneira estruturada.

#### **Como funciona o Gitflow?**
O Gitflow utiliza diferentes branches para organizar o desenvolvimento:

1. **`main`**: Contém o código estável e pronto para produção.
2. **`develop`**: Branch principal de desenvolvimento, onde novas funcionalidades são integradas antes de serem lançadas.
3. **`feature/*`**: Usado para desenvolver novas funcionalidades. Criado a partir do `develop` e, quando finalizado, mesclado de volta ao `develop`.
4. **`release/*`**: Utilizado para preparar uma nova versão antes de ir para produção. Criado a partir do `develop`, permitindo ajustes finais.
5. **`hotfix/*`**: Criado a partir do `main` para corrigir bugs críticos em produção. Após a correção, é mesclado tanto no `main` quanto no `develop`.

#### **Fluxo de Trabalho**
1. Criar uma nova funcionalidade:
   ```bash
   git checkout develop
   git checkout -b feature/nova-funcionalidade
   ```
2. Finalizar a funcionalidade e integrar ao `develop`:
   ```bash
   git checkout develop
   git merge feature/nova-funcionalidade
   git branch -d feature/nova-funcionalidade
   ```
3. Criar uma nova versão de lançamento:
   ```bash
   git checkout develop
   git checkout -b release/v1.0.0
   ```
4. Corrigir um bug crítico em produção:
   ```bash
   git checkout main
   git checkout -b hotfix/corrigir-bug
   ```

Esse fluxo garante um desenvolvimento organizado e reduz conflitos entre branches. Para mais informações, consulte a [documentação oficial do Gitflow](https://nvie.com/posts/a-successful-git-branching-model/).

---

## 📜 **Licença**

Este projeto está licenciado sob os termos da licença **MIT**. Consulte o arquivo [LICENSE](./LICENSE) para obter mais detalhes.

---

## ✅ Observações

- **Módulo principal:** `enap_designsystem/` → Este é o pacote reutilizável com blocos e templates.  
- **Projeto de Teste:** `wagtail_sandbox/` → Serve como playground local para validar o módulo antes de publicá-lo.  

Bom desenvolvimento! 🚀💙

---

🏛️ **Desenvolvido por ENAP** 

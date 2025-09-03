# 📦 Enap Design System - Módulo para Wagtail

Este é um módulo customizado para o **Wagtail**, criado para facilitar a implementação de layouts e componentes reutilizáveis no CMS.

### 🛫 Outros READMEs
 README.md, doc geral do projeto [README.md](README.md)
 README-use.md, doc do uso do módulo [README-use.md](README-use.md) [ATUAL]
 README-pypi.md, doc subir pacote pypi [README-pypi.md](README-pypi.md)


# ENAP Design System

O **ENAP Design System** é um módulo para o Wagtail, baseado no CodeRedCMS, que fornece componentes reutilizáveis e templates pré-configurados para facilitar a criação de sites institucionais.

## Instalação

Para instalar o pacote via PyPI, utilize:

```bash
pip install wagtail-enap-designsystem
```

### Requisitos

- **Wagtail 6.4+**
- **CodeRedCMS 4.1.1+**
- **Django 4+**

## Configuração

Após a instalação, adicione `enap_designsystem` ao seu `INSTALLED_APPS` no `settings.py`:

```python
INSTALLED_APPS = [
    "enap_designsystem",
    "coderedcms",  # Certifique-se de que o CodeRedCMS está instalado

    # ... outros módulos, como por exemplo: ...
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "taggit",
    "modelcluster",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

### Executando Migrações

Após a instalação e configuração, rode as migrações para garantir que todas as tabelas necessárias sejam criadas:

```bash
python manage.py migrate
```

## Uso

O `enap_designsystem` adiciona os seguintes recursos ao seu projeto:

- **ENAPLayout**: Página base herdando de `CoderedWebPage`, com suporte a anotações.
- **RootPage**: Página raiz configurada para permitir apenas subpáginas do tipo `ENAPLayout`.
- **Componentes Wagtail**: Blocos personalizados para layouts institucionais.
- **Templates Pré-preenchidos**: Modelos prontos para diferentes tipos de páginas.

### Criando uma Página com ENAPLayout

No painel administrativo do Wagtail, ao criar uma nova página, selecione **ENAPLayout** para utilizar os templates e funcionalidades do módulo.

## Cache

Se estiver utilizando `wagtailcache`, certifique-se de configurar corretamente o cache, pois a função `cache_clear` ainda não tem suporte completo:

```python
WAGTAIL_CACHE_BACKEND = "default"
```

## Desenvolvimento

(OPCIONAL dev)
**Se estiver contribuindo para o desenvolvimento do módulo**, clone o repositório e instale no modo `editable`:

```bash
git clone https://github.com/seu-org/enap_designsystem.git
cd enap_designsystem
pip install -e .
```

Para rodar o ambiente de desenvolvimento:

```bash
python manage.py runserver
```

## Contribuindo

Pull requests são bem-vindos! Para sugestões e melhorias, abra uma issue no repositório oficial.

---

🏛️ **Desenvolvido por ENAP** 

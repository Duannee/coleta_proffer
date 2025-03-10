# **Coleta Proffer**
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/yuribodo/a-base-vem-forte/blob/main/LICENSE)

---

## Índice

- [Introdução](#introdução)
- [Arquitetura e Tecnologias Utilizadas](#arquitetura-tecnologias-utilizadas)
- [Instruções para Execução](#intruções-para-execução)
- [Coleta e Processamento dos Dados](#coleta-e-processamento-dos-dados)
- [Desafios Encontrados e Soluções](#desafios-encontrados-e-soluções)
- [Possíveis Melhorias Futuras](#possiveis-melhorias-futuras)
- [Contato](#contato)

---

## Introdução

**Coleta Proffer** é uma solução para coletar informações de preços de produtos do site Preço da Hora Bahia para as cidades de Salvador de Feira de Santana. 
[Preço da Hora Bahia](https://precodahora.ba.gov.br/)

---

## Arquitetura e Tecnologias Utilizadas 

### Arquitetura
O projeto utiliza um scraper baseado no `Selenium` para coletar dados de produtos disponíveis na plataforma `Preços da Hora - BA`. A coleta é realizada de forma paralela usando `ThreadPoolExecutor` para melhorar a eficiência.

### Tecnologias Utilizadas
#### Linguagem de Programação 
- **Python 3.8+** - Linguagem principal do projeto.

#### Manipulação de dados 
- **Pandas** - Para manipulação e exportação de dados
  
#### Web Scraping & Automação
- **Selenium** - Automação de navegadores para testes e scraping de páginas web.
- **ThreadPoolExecutor** - Execução concorrente para otimizar a coleta de dados.
- **2Captcha** - Integração com o serviço 2Captcha para resolver captchas automaticamente.

#### Comunicação Web
- **Requests** - Biblioteca popular para fazer requisições HTTP de forma simples.

#### Utilitários
- **Python-dotenv** - Gerenciamento de variáveis de ambiente a partir de arquivos `.env`.
- **Pytz** / **Tzdata** - Suporte a fusos horários para manipulação de datas e horários.

#### Observação
Além dessas, outras bibliotecas estão presentes para complementar funcionalidades específicas do projeto. Caso precise de mais detalhes sobre alguma tecnologia, consulte a documentação oficial.

---

## Instruções para Execução

### Pré-requisitos 
Antes de executar o código, certifique-se de ter instalado os seguintes componentes:
- Python 3.8+
- Google Chrome
- Chromedriver compatível com sua versão do Chrome
- Arquivos lista_eans.json e lista_descricao.json contendo os produtos a serem coletados

#### 1. Clone o repositório
```bash
git clone https://github.com/Duannee/coleta_proffer.git
```
#### 2. Instalação das Dependências
```
     python -m venv venv # Cria o ambiente virtual
     source venv/bin/activate  # Linux/Mac # Acessa o ambiente virtual
     venv\Scripts\activate  # Windows # # Acessa o ambiente virtual
     pip install -r requirements.txt
     cd src
```
#### 3. Configuração do Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API do 2Captcha:
```
API_KEY=SEU_TOKEN_AQUI
```
#### 4. Execução 
O código realizará a coleta de dados dos produtos especificados nos arquivos JSON.
```
python main.py
```

---

## Coleta e Processamento dos Dados

### Como os Dados são coletados?
1. O scraper acessa o site e insere o código EAN do produto na barra de pesquisa.
2. Se houver CAPTCHA, ele é resolvido automaticamente usando a API do `2Captcha`.
3. Os preços, estabelecimentos e CNPJ dos fornecedores são extraídos.
4. Para cada CNPJ encontrado, uma requisição é feita à API pública de CNPJ para obter mais detalhes sobre o estabelecimento.
5. Os dados são armazenados em um arquivo CSV (data_collected.csv).

### Estrutura dos Dados Extraídos
- EAN: Código do produto
- Descrição: Nome do produto
- Preço: Valor encontrado no site
- Estabelecimento: Nome da loja
- CNPJ: Número do CNPJ do estabelecimento
- Cidade, Bairro e Estado: Localização do estabelecimento
- Data de Coleta: Momento da extração


## Desafios Encontrados e Soluções
1. CAPTCHA e Restrições de Acesso
   - **Desafio**: Algumas pesquisas acionam CAPTCHA, impedindo o scraper de continuar.
   - **Solução**: Implementei a API do 2Captcha para resolver automaticamente os desafios reCAPTCHA.
2. Limitação de Consultas à API de CNPJ
   - **Desafio**: A API pública de CNPJ impõe um limite de requisições.
   - **Solução**: Implemei um controle de taxa (rate limit), limitando as requisições a 3 por minuto e utilizando um cache para evitar chamadas repetidas.
3. Elementos Dinâmicos no Site
   - **Desafio**: O site altera dinamicamente o DOM, tornando certos elementos inacessíveis.
   - **Solução**: Implementei WebDriverWait para aguardar os elementos estarem visíveis antes de interagir com eles.
4. Referências de Elementos Obsoletas
   - **Desafio**: O Selenium pode perder a referência de elementos no DOM quando a página é recarregada ou modificada dinamicamente, resultando em `StaleElementReferenceException`.
   - **Solução**: Criei uma classe `WebElementWrapper` que verifica se um elemento ainda é válido e o localiza novamente caso tenha se tornado obsoleto. Essa implementação garante que o scraper não falhe ao tentar acessar elementos que se tornaram obsoletos devido a mudanças na página.


## Possíveis Melhorias Futuras
- **Armazenamento em Banco de Dados**: Migrar a exportação de CSV para um banco SQL para melhor escalabilidade.
- **Criação de Branches Separadas para Cada Pull Request**: Adotar um fluxo de desenvolvimento mais organizado, garantindo que cada funcionalidade ou correção tenha seu próprio branch.
- **Desenvolvimento de Testes Automatizados**: Implementar testes para validar a funcionalidade do scraper e prevenir falhas antes da execução em produção.
  
---

## Contato
- Developer: Duanne Moraes
- LinkedIn: [Duanne Moraes](https://www.linkedin.com/in/duanne-moraes-7a0376278/)


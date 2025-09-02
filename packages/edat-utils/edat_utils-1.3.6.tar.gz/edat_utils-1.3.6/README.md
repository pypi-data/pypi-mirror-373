# Utilitarios EDAT
Classes utilitarias utilizadas pelo EDAT.


# Deploy 

### 🚀 Para realizar o deploy corretamente, deve-se seguir os passos abaixo:

- Necessário alterar a versão do projeto no arquivo [setup.py](./setup.py).
- Commitar as alterações
  - `git add .`
  - `commit -m "<mensagem_do_commit>"`
- Criar uma tag com a mesma versão inserida no arquivo [setup.py](./setup.py).
  - `git tag -a <versão> -m "<mensagem de criação da tag>"`
- Subir as aterações com o comando:
  - `git push --tags`


### Conferir no CI/CD se o pacote foi publicado corretamente.
- link da pipeline: [https://gitlab.unicamp.br/.../pipelines](https://gitlab.unicamp.br/cgu/dados/backend/publicados-pypi/edat_utils/-/pipelines)

# Testes 
### ✅ Procedimentos necessários antes de rodar a suite de testes:
- Criar o ambiente virtual:
  - `python3 -m .venv venv`
  - `source .venv/bin/activate`
  - `pip3 install -r requirements.txt`
- Criar um arquivo .env na raiz do projeto:
 - Copiar o conteúdo do arquivo `env.example` para o arquivo `.env`
 - Preencher com as variáveis necessárias
 


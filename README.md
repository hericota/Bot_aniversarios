
Bot de Aniversários — Discord.py

Este projeto implementa um bot para Discord capaz de registrar, gerenciar e notificar aniversários dentro de um servidor.
Ele utiliza comandos slash e um sistema automático diário para enviar mensagens de parabéns no canal configurado.

Funcionalidades

Registro individual de aniversário no formato DD/MM

Remoção de aniversário

Listagem completa de aniversários registrados no servidor

Identificação do próximo aniversariante

Definição do canal onde as notificações serão enviadas

Rotina automática diária para envio de mensagens

Compatível com Python 3.13+ através de um módulo substituto para audioop

Tecnologias Utilizadas

Python 3.10+

discord.py (comandos e app_commands)

JSON para armazenamento local

python-dotenv para gerenciamento de variáveis de ambiente

Instalação
1. Clonar o repositório
git clone https://github.com/SEU-USUARIO/SEU-REPO.git
cd SEU-REPO

2. Instalar dependências
pip install -r requirements.txt

3. Configurar o token

Crie um arquivo .env na raiz do projeto:

DISCORD_TOKEN=seu_token_aqui

Comandos Disponíveis
/aniver <DD/MM>

Registra o aniversário do usuário.

/listar_aniversarios

Lista todos os aniversários cadastrados no servidor.

/remover_aniver

Remove o aniversário do usuário.

/proximo_aniver

Mostra quem é o próximo a fazer aniversário.

/setar_canal_aniversario <canal>

Define o canal onde as mensagens automáticas serão enviadas (restrito a administradores).

Funcionamento da Tarefa Automática

O bot executa diariamente uma verificação que:

Compara a data atual com os aniversários cadastrados

Envia a notificação no canal configurado

Utiliza o system channel como fallback caso o canal principal não esteja disponível

Compatibilidade com Python 3.13+

Como o módulo audioop foi removido no Python 3.13, o projeto inclui um módulo falso para manter a compatibilidade com o discord.py:

import sys
import types

fake_audioop = types.ModuleType("audioop")
def _fake(*args, **kwargs): return None

fake_audioop.add = _fake
fake_audioop.mul = _fake
fake_audioop.avg = _fake
fake_audioop.max = _fake
fake_audioop.minmax = _fake
fake_audioop.tomono = _fake
fake_audioop.tostereo = _fake
fake_audioop.getsample = _fake
fake_audioop.bias = _fake

sys.modules["audioop"] = fake_audioop

Estrutura do Projeto
/aniversarios           # Dados salvos por servidor
bot_aniversario.py
.env
requirements.txt
README.md

Execução
python bot_aniversario.py

Contribuição

Contribuições são bem-vindas.
Para alterações significativas, recomenda-se abrir uma issue antes para discussão.

import sys
import types

# Cria um módulo falso chamado "audioop" para evitar erro no Python 3.13+
fake_audioop = types.ModuleType("audioop")

# Cria funções falsas que o discord.py pode tentar acessar
def _fake(*args, **kwargs):
    return None

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

import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime
import os
from dotenv import load_dotenv
# ----------------- CONFIGURAÇÃO -----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

PASTA = "aniversarios"
os.makedirs(PASTA, exist_ok=True)


# ----------------- FUNÇÕES AUXILIARES -----------------
def caminho_arquivo(guild_id):
    """Retorna o caminho do arquivo JSON do servidor"""
    return os.path.join(PASTA, f"{guild_id}.json")


def carregar_dados(guild_id):
    """Carrega aniversários e canal de um servidor"""
    arquivo = caminho_arquivo(guild_id)
    if not os.path.exists(arquivo):
        return {"aniversarios": {}, "canal": None}
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(guild_id, data):
    """Salva aniversários e canal de um servidor"""
    arquivo = caminho_arquivo(guild_id)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ----------------- COMANDO /ANIVER -----------------
@tree.command(name="aniver", description="Registra seu aniversário (formato: DD/MM)")
async def registrar_aniversario(interaction: discord.Interaction, data: str):
    try:
        datetime.strptime(data, "%d/%m")
    except ValueError:
        await interaction.response.send_message("❌ Use o formato **DD/MM** (ex: 14/10).", ephemeral=True)
        return

    guild_id = interaction.guild_id
    user_id = str(interaction.user.id)

    dados = carregar_dados(guild_id)
    dados["aniversarios"][user_id] = {"nome": interaction.user.name, "data": data}
    salvar_dados(guild_id, dados)

    await interaction.response.send_message(f"✅ Seu aniversário foi registrado como **{data}**!", ephemeral=True)


# ----------------- COMANDO /LISTAR_ANIVERSARIOS -----------------
@tree.command(name="listar_aniversarios", description="Mostra todos os aniversários cadastrados neste servidor")
async def listar_aniversarios_cmd(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    dados = carregar_dados(guild_id)
    aniversarios = dados["aniversarios"]

    if not aniversarios:
        await interaction.response.send_message("📭 Nenhum aniversário registrado neste servidor.", ephemeral=True)
        return

    mensagem = "🎂 **Lista de aniversários registrados:**\n\n"
    for info in aniversarios.values():
        mensagem += f"👤 **{info['nome']}** — 🎉 {info['data']}\n"

    await interaction.response.send_message(mensagem)


# ----------------- COMANDO /REMOVER_ANIVER -----------------
@tree.command(name="remover_aniver", description="Remove seu aniversário registrado")
async def remover_aniversario(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    dados = carregar_dados(guild_id)
    aniversarios = dados["aniversarios"]
    user_id = str(interaction.user.id)

    if user_id in aniversarios:
        del aniversarios[user_id]
        salvar_dados(guild_id, dados)
        await interaction.response.send_message("🗑️ Seu aniversário foi removido com sucesso.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Você ainda não registrou seu aniversário.", ephemeral=True)


# ----------------- COMANDO /PROXIMO_ANIVER -----------------
@tree.command(name="proximo_aniver", description="Mostra quem é o próximo a fazer aniversário neste servidor")
async def proximo_aniver(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    dados = carregar_dados(guild_id)
    aniversarios = dados["aniversarios"]

    if not aniversarios:
        await interaction.response.send_message("📭 Nenhum aniversário registrado ainda.", ephemeral=True)
        return

    hoje = datetime.now()
    proximos = []

    for info in aniversarios.values():
        dia, mes = map(int, info["data"].split("/"))
        data_aniver = datetime(hoje.year, mes, dia)
        if data_aniver < hoje:
            data_aniver = datetime(hoje.year + 1, mes, dia)
        diferenca = (data_aniver - hoje).days
        proximos.append((info["nome"], info["data"], diferenca))

    proximos.sort(key=lambda x: x[2])
    nome, data, dias = proximos[0]

    if dias == 0:
        msg = f"🎉 O próximo aniversário é **hoje**! Parabéns para **{nome}** 🎂"
    elif dias == 1:
        msg = f"⏰ O próximo aniversário é amanhã: **{nome}** ({data}) 🎉"
    else:
        msg = f"📅 O próximo aniversário é de **{nome}**, em **{dias} dias** ({data})."

    await interaction.response.send_message(msg)


# ----------------- COMANDO /SETAR_CANAL_ANIVERSARIO -----------------
@tree.command(name="setar_canal_aniversario", description="Define o canal onde as mensagens de aniversário serão enviadas (apenas para administradores).")
@app_commands.checks.has_permissions(administrator=True)
async def setar_canal(interaction: discord.Interaction, canal: discord.TextChannel):
    guild_id = interaction.guild_id
    dados = carregar_dados(guild_id)
    dados["canal"] = canal.id
    salvar_dados(guild_id, dados)

    await interaction.response.send_message(f"✅ Canal de aniversários definido para {canal.mention}", ephemeral=False)


@setar_canal.error
async def setar_canal_erro(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Apenas administradores podem usar este comando.", ephemeral=True)


# ----------------- TAREFA AUTOMÁTICA -----------------
@tasks.loop(hours=24)
async def verificar_aniversarios():
    hoje = datetime.now().strftime("%d/%m")
    for guild in bot.guilds:
        dados = carregar_dados(guild.id)
        aniversarios = dados["aniversarios"]
        canal_id = dados.get("canal")

        canal = None
        if canal_id:
            canal = guild.get_channel(canal_id)
        if not canal:
            canal = guild.system_channel or next(
                (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
                None
            )

        for user_id, info in aniversarios.items():
            if info["data"] == hoje and canal:
                await canal.send(f"🎉 @everyone hoje é aniversário de **{info['nome']}**! 🎂🎈")


# ----------------- EVENTO DE INICIALIZAÇÃO -----------------
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print("Erro ao sincronizar comandos:", e)
    verificar_aniversarios.start()


bot.run(TOKEN)

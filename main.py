import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import sqlite3 



# Cargar token y configurar bot
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# definicion del bot con su prefijo e intents :D 
bot = commands.Bot(command_prefix= "/" , intents = discord.Intents.all())

# Flujo general:
# 1) Administrador ejecuta comando `start` -> envía embed con `Request High Test` (crear_boton)
# 2) Usuario presiona el botón "Request High Test" -> callback `crear_ticket` se ejecuta
# 3) `crear_ticket` crea canal privado (ticket), envía embed inicial y adjunta vista con boton cerrar
# 4) Usuario o staff presiona "Cerrar Ticket" -> callback `cerrar_ticket` borra el canal
# 5) Comandos adicionales: `add_user` permite añadir permisos a un miembro en el canal
# (Los comentarios específicos de cada función detallan el flujo local sin modificar el código existente)

# definimos la funcion que crea el embed y lo retorna
def crear_embed_start():
    embed = discord.Embed(
        title="High Test Request",
        description="Bienvenido a los high test de Drakense, como requisito minimo debes ser LT3+ en alguna modalidad para abrir un high test",
        color= discord.Colour.blue()
    )
    return embed


# --- Flujo: cerrar ticket
# Este flujo es invocado por el botón de cerrar (vista persistente).
async def cerrar_ticket(interaction):
    user = interaction.user
    guild = interaction.guild 
    roles = [
        "Tester",
        "Staff Team"
    ]
    
    roles_for_close_ticket = []
    
    for rol in roles:
        rol_obj = discord.utils.get(guild.roles, name = rol)
    if rol_obj:
        roles_for_close_ticket.append(rol_obj)
    
    if any(rol in user.roles for rol in roles_for_close_ticket):
        channel = interaction.channel
        await channel.send("Cerrando ticket...")
        await channel.delete()
    else:
        await channel.send_message("no puedes cerrar ticket con tus permisos actuales papu", ephemeral = True)


def crear_boton_cerrar():
    # crear el boton de cerrar ticket
    boton = discord.ui.Button(
        label="Cerrar Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="cerrar_ticket_persistent"
    )
    
    # asignar la funcion que se ejecuta cuando se presiona el boton
    boton.callback = cerrar_ticket
    
    # crear una vista persistente (timeout=None hace que nunca expire)
    vista = discord.ui.View(timeout=None)
    # agregar el boton a la vista
    vista.add_item(boton)
    
    # devolver la vista completa
    return vista


# --- Flujo: crear ticket (invocado al pulsar "Request High Test")
# Este flujo:
# - recibe la interacción del usuario
# - determina roles y permisos
# - crea un canal de texto privado (ticket)
# - responde de forma efímera al usuario confirmando el ticket
# - envía un embed de bienvenida en el canal del ticket con la vista de cerrar
async def crear_ticket(interaction):
    guild = interaction.guild
    user = interaction.user
    
    roles = [
        "LT3〢NethPot",
        "HT3〢NethPot",
        "LT2〢NethPot",
        "HT2〢NethPot",
        "LT1 〢NethPot",
        "HT1〢NethPot",
        "LT3〢CrystalPvP",
        "HT3〢CrystalPvP",
        "LT2〢CrystalPvP",
        "HT2〢CrystalPvP",
        "LT1〢CrystalPvP",
        "HT1〢CrystalPvP",
        "LT3〢Sword",
        "HT3〢Sword",
        "LT2〢Sword",
        "HT2〢Sword",
        "LT1〢Sword",
        "HT1〢Sword",
        "LT3〢MacePvP",
        "HT3〢MacePvP",
        "LT2〢MacePvP",
        "HT2〢MacePvP",
        "LT1〢MacePvP",
        "HT1〢MacePvP"
    ]
    
    roles_para_abrir_high_test = []
    
    for rol in roles:
        role_obj = discord.utils.get(interaction.guild.roles, name=rol)
        if role_obj:
            roles_para_abrir_high_test.append(role_obj)
    
    
    if any(role in user.roles for role in roles_para_abrir_high_test):
        modal = discord.ui.Modal(title="Formulario de High Test")
        
        campo_ign = discord.ui.TextInput(
            label="nombre de MC",
            placeholder="ing",
            required=True,
            max_length=30
        )
        
        campo_modalidad = discord.ui.TextInput(
            label="Modalidad del test",
            placeholder="uhc : sword : netherite pots : cpvp ... ",
            required=True,
            max_length=30
        )
        
        modal.add_item(campo_ign)
        modal.add_item(campo_modalidad)
        
        async def on_submit(inter_modal : discord.Interaction):
            ign = campo_ign.value
            modalidad = campo_modalidad.value
            rol_tester = discord.utils.get(guild.roles , name = "Tester")
            rol_helper = discord.utils.get(guild.roles , name = "Helper")
            rol_tmod = discord.utils.get(guild.roles , name = "T-Mod")
            rol_mod = discord.utils.get(guild.roles , name = "Mod")
            rol_srmod = discord.utils.get(guild.roles , name = "Sr Mod")
            rol_regulador = discord.utils.get(guild.roles , name = "Regulator")
            rol_jradmin = discord.utils.get(guild.roles , name = "Jr Admin")
            rol_admin = discord.utils.get(guild.roles , name = "Admin")
            
            channel_overwrites = {
                guild.default_role : discord.PermissionOverwrite(read_messages=False), # usuarios comunes no pueden ver el canal
                user : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True), # creador del ticket puede ver y escribir
                rol_tester : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True), # aquellos con rol staff si pueden ver y escribir
                rol_helper : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_tmod : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_mod : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_srmod : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_regulador : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_jradmin : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True),
                rol_admin : discord.PermissionOverwrite(read_message_history= True, read_messages= True, send_messages= True)
            }
            
            # crear ticket porfin amigo
            ticket = await guild.create_text_channel(
                name = f"📂 {user.name}",
                overwrites = channel_overwrites
            )
            
            
            # responder al usuario con autismo para que se de cuenta que hizo un ticket por ahi es boludito
            await inter_modal.response.send_message(
                f" tu ticket ha sido creado {ticket.mention}",
                ephemeral = True
            )
            
            # definicion del embed para mandar
            embed = discord.Embed(
                title = f"{ticket.name}",
                description = "Bienvenido a los high test de Drakense, los testers estaran con usted cuando se encuentren con disponibilidad. Agradecemos la paciencia y porfavor evite el tag directo a miembros del staff o testers, los mismos reguladores le asignaran un tester en caso de no contar con disponibilidad suficiente",
                color = discord.Colour.blue()
            )
            embed.add_field(
                name="", value="----------------------",inline=False
            )
            embed.add_field(
                name="IGN", value=f"{ign}",inline=False
            )
            
            embed.add_field(
                name="Modalidad", value=f"{modalidad}",inline=False
            )
            vista_cerrar = crear_boton_cerrar()
            await ticket.send(
            embed = embed,
            view = vista_cerrar
            )
        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)
    else:
        await interaction.response.send_message(
            "No tienes los roles necesarios para solicitar un High Test.",
            ephemeral=True
        )



# --- Flujo: crear vista/botón principal que inicia la petición de high test
# El botón enlaza su callback a `crear_ticket` (cuando se pulse, se ejecuta el flujo anterior).
def crear_boton_request_high_test():
    boton = discord.ui.Button(
        label="Request High Test",
        style=discord.ButtonStyle.primary,
        custom_id="request_high_test"
    )

    boton.callback = crear_ticket
    
    vista = discord.ui.View(timeout=None)
    vista.add_item(boton)
    
    return vista


# --- Eventos y comandos
# on_ready registra las vistas persistentes para que los botones sigan funcionando.
@bot.event
async def on_ready():
    vista_request_high_test = crear_boton_request_high_test()
    vista_cerrar_high_test = crear_boton_cerrar()
    bot.add_view(vista_request_high_test)
    bot.add_view(vista_cerrar_high_test)
    boton_nethpot = crear_boton_waitlist_nethpot()
    boton_sword = crear_boton_waitlist_sword()
    boton_mace = crear_boton_waitlist_mace()
    boton_cristal = crear_boton_waitlist_cristal()
    vista_autorol = discord.ui.View(timeout=None)
    vista_autorol.add_item(boton_nethpot)
    vista_autorol.add_item(boton_sword)
    vista_autorol.add_item(boton_mace)
    vista_autorol.add_item(boton_cristal)
    
    bot.add_view(vista_autorol)

    print("support manager is online succesfully")

# ==================================
#   - Desplegar panel high test -
# ==================================
@bot.command()
@commands.has_permissions(administrator=True)
async def start_ht(ctx):
    embed = crear_embed_start()
    vista = crear_boton_request_high_test()
    
    await ctx.send(embed=embed, view=vista)
    
    await ctx.message.delete()

# ==================================
#           - Add User -
# ==================================
@bot.command()
async def add_user(ctx, usuario: discord.Member):
    overwrites = discord.PermissionOverwrite(view_channel=True, send_messages=True)
    await ctx.channel.set_permissions(usuario, overwrite=overwrites)
    await ctx.send(f"{usuario.mention} agregado al canal")


# ============================
#       - AUTO ROLES -
# ============================


def embed_autorol():
    embed = discord.Embed(
        title= "Auto Rol de Waitlist",
        description= "Presiona los botones para activar las notificaciones de cuando se abra waitlist en una modalidad",
        color= discord.Colour.pink()
    )
    return embed

# ==================================
#     - Desplegar Panel Autorol -
# ==================================
@bot.command()
async def start_autorol(ctx):
    embed = embed_autorol()
    boton_nethpot = crear_boton_waitlist_nethpot()
    boton_sword = crear_boton_waitlist_sword()
    boton_mace = crear_boton_waitlist_mace()
    boton_cristal = crear_boton_waitlist_cristal()
    vista_autorol = discord.ui.View(timeout=None)
    vista_autorol.add_item(boton_nethpot)
    vista_autorol.add_item(boton_sword)
    vista_autorol.add_item(boton_mace)
    vista_autorol.add_item(boton_cristal)


    await ctx.send(embed = embed, view = vista_autorol)


# ============================
# waitlist Nethpot
def crear_boton_waitlist_nethpot():
    boton = discord.ui.Button(
        label="Waitlist NethPot",
        style=discord.ButtonStyle.primary,
        custom_id="dar_rol_waitlist_nethpot"
    )
    boton.callback = dar_rol_waitlist_nethpot
    return boton


async def dar_rol_waitlist_nethpot(interaction):
    guild = interaction.guild 
    user = interaction.user
    rol_waitlist_nethpot = discord.utils.get(guild.roles , name = "Waitlist Nethpot")
    await user.add_roles(rol_waitlist_nethpot)
    await interaction.response.send_message("Ahora seras notificado cuando se abra la waitlist de NethPot", ephemeral = True)


# ============================
# waitlist Sword


def crear_boton_waitlist_sword():
    boton = discord.ui.Button(
        label="Waitlist Sword",
        style=discord.ButtonStyle.primary,
        custom_id="dar_rol_waitlist_sword"
    )

    boton.callback = dar_rol_waitlist_sword
    
    return boton


async def dar_rol_waitlist_sword(interaction):
    guild = interaction.guild 
    user = interaction.user
    rol_waitlist_sword = discord.utils.get(guild.roles , name = "Waitlist Sword")
    await user.add_roles(rol_waitlist_sword)
    await interaction.response.send_message("Ahora seras notificado cuando se abra la waitlist de Sword", ephemeral = True)
    
    
# ============================
# waitlist Mace


def crear_boton_waitlist_mace():
    boton = discord.ui.Button(
        label="Waitlist Mace",
        style=discord.ButtonStyle.primary,
        custom_id="dar_rol_waitlist_mace"
    )
    boton.callback = dar_rol_waitlist_mace
    return boton


async def dar_rol_waitlist_mace(interaction):
    guild = interaction.guild 
    user = interaction.user
    rol_waitlist_mace = discord.utils.get(guild.roles , name = "Waitlist Mace")
    await user.add_roles(rol_waitlist_mace)
    await interaction.response.send_message("Ahora seras notificado cuando se abra la waitlist de Mace", ephemeral = True)
    



# ============================
# waitlist Cristal

def crear_boton_waitlist_cristal():
    boton = discord.ui.Button(
        label="Waitlist Cristal",
        style=discord.ButtonStyle.primary,
        custom_id="dar_rol_waitlist_cristal"
    )
    boton.callback = dar_rol_waitlist_cristal
    return boton


async def dar_rol_waitlist_cristal(interaction):
    guild = interaction.guild 
    user = interaction.user
    rol_waitlist_cristal = discord.utils.get(guild.roles , name = "Waitlist Cristal")
    await user.add_roles(rol_waitlist_cristal)
    await interaction.response.send_message("Ahora seras notificado cuando se abra la waitlist de Cristal", ephemeral = True)

# Ejecutar bot
bot.run(TOKEN)
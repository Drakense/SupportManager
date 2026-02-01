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
            
    channel = interaction.channel
    
    if any(rol in user.roles for rol in roles_for_close_ticket):
        

        
        
        # conteo de id de los ticketsitos y esas cosas
        with open("id_logs_register.txt" , "r") as id_log:
            try:
                liniesitas = id_log.readlines()
                ultima_liniesita = int(liniesitas[-1].strip())
            except FileNotFoundError as e:
                print(f"/ the file dont exists / - {e}")
                
        with open("id_logs_register.txt" , "a") as id_log:
            ultima_liniesita = ultima_liniesita + 1
            id_log.write(f"{ultima_liniesita}\n")
        
        nombre_log = f"{ultima_liniesita}-{channel.name}.html"
        
        # inicializacion de estilos 
        with open(f"/home/pablo/td/drakensedsbot/transcripts/{nombre_log}", "a") as log:
            log.write('''
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Log</title>
    <style>
        body {
            background-color: #36393f;
            color: #dcddde;
            font-family: Whitney, "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .message {
            padding: 8px 16px;
            margin: 4px 0;
            border-left: 4px solid transparent;
        }
        .message:hover {
            background-color: #32353b;
            border-left-color: #5865f2;
        }
        .author {
            font-weight: 600;
            color: #fff;
            display: inline;
            margin-right: 8px;
        }
        .timestamp {
            font-size: 12px;
            color: #72767d;
            margin-left: 8px;
        }
        .content {
            color: #dcddde;
            margin-top: 4px;
            word-wrap: break-word;
        }
        .bot {
            background-color: #5865f2;
            color: white;
            font-size: 10px;
            padding: 2px 4px;
            border-radius: 3px;
            margin-left: 6px;
            vertical-align: middle;
        }
        h1 {
            color: #fff;
            border-bottom: 2px solid #5865f2;
            padding-bottom: 10px;
        }
    </style>
</head>

''')
        
        # contenido del ticket con los mensajes
        with open(f"/home/pablo/td/drakensedsbot/transcripts/{nombre_log}","a") as log:
            messages_iterator = channel.history(limit=None, oldest_first=True)
            message_list = []
            async for message in messages_iterator:
                message_list.append(message)
            for msg in message_list:
                log.write(f'''
    <div class="message">
        <span class="author">{msg.author}</span>
        <span class="timestamp">({message.created_at.strftime('%d-%m-%y %H:%M:%S')}</span>
        <div class="content">{msg.content}</div>
    </div>
''')
        with open(f"/home/pablo/td/drakensedsbot/transcripts/{nombre_log}","a") as log:
            log.write(f'''
</body>
</html>
''')

        channel_ticket = interaction.channel
        log_embed = discord.Embed(
            title=f"{channel_ticket.name}",
            description="Log creado, visite el siguiente link para poder ver la transcripcion",
            color= discord.Colour.purple()
        )
        
        log_embed.add_field(
            name= "Link del transcript",
            value=f"[transcript](https://transcripts.pablorelojerio.online/{nombre_log})"
        )
        
        logs_channel = bot.get_channel(1466112270705885462)
        await logs_channel.send(embed=log_embed)
        
        await interaction.response.defer(ephemeral = True)
        # aca se cierra el tickesito
        try:
            await channel.delete()
        except discord.errors.NotFound:
            pass
    else:
        await channel.send("no puedes cerrar ticket con tus permisos actuales papu")
            
            


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
    
    # roles 
    roles = [
        # nethpot
        1405251979210395700,
        1405251857080647731,
        1405251743821987993,
        1405251920897114202,
        1405251793427894343,
        1405251665619058698,
        # sword
        1409331647752700114,
        1409332005211996322,
        1409332180488032276,
        1409331897590349824,
        1409332092348928020,
        1409332272313794650,
        # crystalpvp
        1409325012778745926,
        1409328227541057576,
        1409328769411317781,
        1409327273391292466,
        1409328574162272336,
        1409328943051309086,
        # mace
        1411862768625389709,
        1411862274775318598,
        1411861984139542568,
        1411862839177646140,
        1411862068663160913,
        1410441285109678312
    ]

    roles_para_abrir_high_test = []
    
    for rol in roles:
        role_obj = discord.utils.get(interaction.guild.roles, id = rol)
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
            placeholder="NethPot | Sword | Cpvp | Mace",
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
            categoria = discord.Object(id = 1464649713377607680)
            # crear ticket porfin amigo
            ticket = await guild.create_text_channel(
                name = f"📂 {user.name}",
                overwrites = channel_overwrites,
                category = categoria
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
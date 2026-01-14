import asyncio


# ejemplo de tareas sincronas sin concurrencia real 
async def saludar(nombre, segundos):
    print(f"hola {nombre}")
    await asyncio.sleep(segundos)
    print(f"chau {nombre}")

async def main():
    await saludar("maria", 10)
    await saludar("jose", 2)

# asyncio.run(main())

# ejemplo de tareas asincronas con concurrencia 

async def cocinar(nombre, segundos):
    print(f"empezando a cocinar {nombre}")
    await asyncio.sleep(segundos)
    print(f"{nombre} termino de cocinarse")

async def cocinar_todo():
    tarea1 = asyncio.create_task(cocinar("filete", 10))
    tarea2 = asyncio.create_task(cocinar("pancito", 3))
    tarea3 = asyncio.create_task(cocinar("ensalada", 7))

    await tarea1
    await tarea2
    await tarea3

# asyncio.run(cocinar_todo())



# defonir funcion asincrona con gunther

async def cocinar(nombre, segundos):
    print(f"empezando a cocinar {nombre}")
    await asyncio.sleep(segundos)
    print(f"{nombre} termino de cocinarse")

async def cocinar_todo():
    tareas = [
        cocinar("filete", 10),
        cocinar("pancito", 3),
        cocinar("ensalada", 7)
    ]

    await asyncio.gather(*tareas)
asyncio.run(cocinar_todo())
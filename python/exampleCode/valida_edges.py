import os
import pandas as pd
import ollama

import pandas as pd
import ollama

def checkRelation(relacionStr):
    prompt = f"""Te voy a pasar una afirmación en el dominio médico de la forma 'sujeto','relacion','predicado',´fuerza´. 
                 La afirmación puede tener una parte en inglés y otra en español. Tienes que responder en español. La 
                 fuerza es un número entre 0 y 1 que indica cómo de segura o confiable es la relación. Si está cerca
                 de 1 es que la afirmación ocurre siempre y es muy confiable. Si está cerca de 0, es que la afirmación
                 ocurre pocas veces. Tienes que contestar 'VEREDICTO: OK' o VEREDICTO: 'INCORRECTO'. En el caso de OK,
                 únicamente tienes que decir 'VEREDICTO: OK'. Si es incorrecto, entonces tienes que justificar por qué
                 piensas que es incorrecto. Ésta es la afirmación: f{relacionStr}"""
    res = ollama.chat(
        #model="deepseek-r1:70b",
        model="deepseek-r1:7b",
        messages=[{"role": "user", "content": prompt}],
        keep_alive="12h",  # keep the model resident
#        options = {
#            "num_thread": 12,
#            "num_ctx": 4096,
#            "temperature": 0.2,
#            "seed": 42,
#            "main_gpu": 0,
#            "num_gpu": 1,
#        }
    )
    response = res["message"]["content"]
    print(response)
    if "VEREDICTO: OK" in response:
        return (True, "")
    else:
        return (False, response)

entities = pd.read_excel("COpenMed_20250829.xlsx","entidades")
entities = entities.set_index("IdEntidad")["Entidad"].to_dict()

relaciones = pd.read_excel("COpenMed_20250829.xlsx","relaciones")
relaciones = relaciones.sort_values(by="IdAsociacion").reset_index(drop=True)

fnAux = "valida_edges_aux.txt"
if os.path.exists(fnAux):
    with open(fnAux,"r") as fh:
        lastIdAsociacion=int(fh.readline().strip())
else:
    lastIdAsociacion = -1

iterSave = 0
fnIncorrect = "valida_edges_incorrect.txt"
fhIncorrect = open(fnIncorrect,"a")
for row in relaciones.itertuples(index=False):
    idAsociacion = row.IdAsociacion
    if idAsociacion>lastIdAsociacion:
        if row.TipoAsociacion=="Disease has standard Code" or \
           row.TipoAsociacion=="The prevalence of this Disease in this Population is ...":
            continue
        #try:
        relacionStr = f'"{entities[row.IdEntidad1]}","{row.TipoAsociacion}","{entities[row.IdEntidad2]}" fuerza={row.Nivel}'
        if not pd.isna(row.Descripcion):
            relacionStr+=f' Comentario: {row.Descripcion}'
        print(idAsociacion,relacionStr)
        ok, response = checkRelation(relacionStr)
        if not ok:
            fhIncorrect.write(f"idAsoc={idAsociacion}: {relacionStr}\n")
            fhIncorrect.write(response+"\n\n")

        lastIdAsociacion = idAsociacion
        iterSave+=1
        #except:
        #    pass
    
        if iterSave%100==0:
            with open(fnAux, "w") as fh:
                fh.write(f"{lastIdAsociacion}\n")
            fhIncorrect.flush()

fhIncorrect.close()

import sys
from pandas import read_excel


if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 showEdges.py <excelfile>")
        print("   <excelfile> must contain the Excel sheets of COpenMed")
        sys.exit(1)
    
    fnExcel=sys.argv[1]

    df_Entidades = read_excel(fnExcel, sheet_name="entidades")
    df_relaciones = read_excel(fnExcel, sheet_name="relaciones")
    df_relaciones = df_relaciones.sort_values(by='IdAsociacion')
    
    entidades = df_Entidades.set_index('IdEntidad')['Entidad'].to_dict()
            
    minId = 1
    fh=open('allrelations.txt','w',encoding='utf-8')
    for index, row in df_relaciones.iterrows():
        idAsociacion = row['IdAsociacion']
        if (idAsociacion>=minId):
            fh.write("%d: (%s,%s,%s)\n"%(idAsociacion,
                                     entidades[row['IdEntidad1']],
                                     row['TipoAsociacion'],
                                     entidades[row['IdEntidad2']]))
    fh.close()

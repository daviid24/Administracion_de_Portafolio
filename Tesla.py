import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import datetime
import os

class Accion:

    def __init__(self,datos):
        tabla = pd.read_csv(datos,header = 0)
        self.__precios = tabla.loc[:,["Date","Price"]].copy()

        try:
            if self.__precios.loc[:,'Price'].dtype == 'object':
                self.__precios.loc[:,'Price'] = self.__precios.loc[:,'Price'].apply(lambda x: x.replace(',',''))
                self.__precios.loc[:,'Price'] = pd.to_numeric(self.__precios.loc[:,'Price'])
        except:
            print('error al crear portafolio')

    def getDatos(self):
        return self.__precios


class Portafolio:

    def __init__(self):
        self.__precios = None
        self.__nombreAcciones = ['Fecha']
        self.setPortafolio()

    def getMatriz(self):
            return self.__precios

    def setPortafolio(self):

        acciones = []
        doc = [doc for doc in os.listdir('Historicos') if doc.endswith('.csv')]

        for i in range(0,len(doc)):
            acciones.append(Accion('Historicos/' + doc[i]))
            splitDoc = doc[i].split()
            self.__nombreAcciones.append(splitDoc[0])

        self.__precios = acciones[0].getDatos()

        for a in range(1,len(acciones)):
            self.__precios = pd.merge(self.__precios,acciones[a].getDatos(),on='Date')

        self.__precios.columns = self.__nombreAcciones
        self.__precios['Fecha'] = pd.to_datetime(self.__precios['Fecha'])

    def retornos(self):

        for i in [col for col in self.__precios.columns if col in self.__nombreAcciones and col != 'Fecha']:
            nuevo = [n for n in self.__precios[i]]
            anterior = [a for a in self.__precios.loc[1:,i]]

            ret = list(map(lambda nuevo,anterior:math.log(nuevo/anterior),nuevo,anterior))
            ret.append(0)

            self.__precios['Retornos '+ i] = ret

    def variacion(self):

        for i in [col for col in self.__precios.columns if col in self.__nombreAcciones and col != 'Fecha']:
            nuevo = [n for n in self.__precios[i]]
            anterior = [a for a in self.__precios.loc[1:,i]]

            var = list(map(lambda nuevo,anterior:(nuevo/anterior)-1,nuevo,anterior))
            var.append(0)

            self.__precios['Variacion '+ i] = var

    def covar(self):
        a = np.array(list(self.__precios.iloc[:,1]))
        b = np.array(list(self.__precios.iloc[:,2]))
        #c = np.array(list(self.__matriz.iloc[:,6]))

        d = np.vstack((a,b))
        cov = np.cov(d)
        print(cov)

    def guardar(self,nombre):
        self.__precios.to_excel('{}.xlsx'.format(nombre),index=0)
        
    def medias(self,valor,accion):
        return list(map(lambda x:self.__matriz.iloc[x:valor + x,accion].mean(),list(range(0,len(self.__matriz)-valor))))

    def analisis(self):
        m10 = self.medias(10,1)
        m20 = self.medias(20,1)

        for i in range(0,len(m20)):
            if m10[i] > m20[i]:
                print('Vender')
            else:
                print('Comprar')

    def grafico_individual(self,accion,guardar = False,meses = None): #Muestra el gráfico de solo una acción
        datos = self.getMatriz().copy()

        #Definir dimensión del gráfico
        plt.figure(figsize=(8,4),dpi=100,facecolor='gray'
                   ,tight_layout=True) #Ajustar gráfico

        #Datos del gráfico

        if meses == None:
            plt.plot(datos['Fecha'],     #Fecha(Eje x)
                     datos[accion],      #Accion(Eje Y)
                     color = 'b',                   #color = blue
                     label = accion)                #Nombre línea
        else:
            fecha_maxima = datetime.datetime.strptime(str(datos['Fecha'].max()), '%Y-%m-%d %H:%M:%S')
            meses_diferencia = fecha_maxima - datetime.timedelta(days=30 * meses)

            datos = datos[datos['Fecha']> pd.to_datetime(str(meses_diferencia))]

            plt.plot(datos['Fecha'],     #Fecha(Eje x)
                     datos[accion],      #Accion(Eje Y)
                     color = 'b',                   #color = blue
                     label = accion)                #Nombre línea


        #Propiedades del gráfico
        plt.title('Precios de la acción {} ({} - {})'.format(accion,datos['Fecha'].min().year,datos['Fecha'].max().year),
                  fontdict={'fontname':'Arial','fontweight':'bold','fontsize':20,'color':'white'})
        
        plt.ylabel('Precio {}'.format(accion),
                   fontdict={'fontname':'Arial','fontweight':'bold','fontsize':12,'color':'white'})
        plt.xlabel('Fecha',
                   fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 12, 'color': 'white'},
                    labelpad=5)
        
        #Propiedades de los ejes
        plt.xticks(rotation= 45) #Rotación diagonal (45 grados)

        #Mostrar leyenda
        plt.legend(shadow=True)

        #Guardar gráfico
        if guardar:
            plt.savefig('Gráfico_{}.png'.format(accion),facecolor = 'gray')
            print('Gráfico guardado con éxito')

        plt.show()

    def grafico_comparativo(self,accion_1,accion_2,guardar = False): #Agrega 2 o más acciones en un gráfico
        datos = self.getMatriz().copy()

        #Definir dimensión del gráfico
        plt.figure(figsize=(8,4),dpi=100,facecolor='gray'
                   ,tight_layout=True) #Ajustar gráfico

        #Gráfico de la primera acción (gráfico y propiedades)
        plt.plot(datos['Fecha'], datos[accion_1],
                 color='r',
                 label = accion_1)

        plt.ylabel('Precio {}'.format(accion_1),
                   fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 12, 'color': 'white'})

        plt.title('{} vs {} ({} - {})'.format(accion_1,accion_2, datos['Fecha'].min().year, datos['Fecha'].max().year),
            fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 20, 'color': 'white'})

        plt.xlabel('Fecha',
                   fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 12, 'color': 'white'},
                   labelpad=5)
        plt.xticks(rotation = 45) #rotación diagonal (45 grados)

        #Inserta segundo gráfico
        acc2 = plt.twinx()
        acc2.plot(datos['Fecha'], datos[accion_2],
                  color = 'b',
                  label = accion_2)
        acc2.set_ylabel('Precio {}'.format(accion_2),
                   fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 12, 'color': 'white'})

        #leyenda
        plt.plot(np.nan,'r', label = accion_1)
        plt.legend(shadow = True)

        #Guardar gráfico (opcional)
        if guardar:
            plt.savefig('Gráfico_{}_vs_{}.png'.format(accion_1,accion_2),facecolor = 'gray')
            print('Gráfico guardado con éxito')

        plt.show()

    def grafico_total(self,guardar = False): #Gráfico con todas las acciones por separado
        datos = self.getMatriz().copy()

        #Asignación de filas y columnas del subplot
        fila = 1
        columna = 1
        n_graficos = len(self.__nombreAcciones) -1
        if n_graficos <= 4:
            fila = n_graficos
        elif (n_graficos > 4) and (n_graficos < 7):
            fila = 3
            columna = 2
        elif n_graficos >= 7:
            fila = 4
            columna = 2

        # #Propiedades de cada gráfico
        fig = plt.figure(figsize=(12, 7),
                         dpi=100,
                         facecolor='gray')
        fig.suptitle('Precios del portafolio ({} - {})'.format(datos['Fecha'].min().year, datos['Fecha'].max().year),
                     fontdict={'fontname': 'Arial', 'color': 'white'},
                     fontsize = 20,fontweight = 'bold')

        grid = plt.GridSpec(fila, columna,
                            wspace=0,
                            hspace=0)

        #Crear lista de propiedades del gráfico
        pos = []
        for m in range(0,fila):
            for n in range(0,columna):
                pos.append((m,n))

        #Crear cada subgrafico
        for l in range(0,n_graficos):
            try:

                sp = fig.add_subplot(grid[pos[l]])
                sp.plot(datos['Fecha'], datos[self.__nombreAcciones[l+1]])
                if l%2 != 0:
                    sp.yaxis.tick_right()
                    sp.yaxis.set_label_position("right")

                sp.set_ylabel('Precio {}'.format(self.__nombreAcciones[l+1]))
                if l >n_graficos:
                    sp.set_xlabel('Fecha')

            except:
                None
                #sp.tick_params(labelrotation=45)
                # sp.set_xticklabels('Fecha', rotation=45)
                #grafico[m][n].xticks(rotation = 45) #rotación diagonal (45 grados)

        #guardar gráfico
        if guardar:
            plt.savefig('Gráfico del portafolio.png')
            print('Gráfico guardado con éxito')

        plt.show()

    def pruebas(self):
        meses = 5
        #fecha_minima = datetime.datetime.strptime(str(self.getMatriz()['Fecha'].min()),'%Y-%m-%d %H:%M:%S')
        fecha_maxima = datetime.datetime.strptime(str(self.getMatriz()['Fecha'].max()),'%Y-%m-%d %H:%M:%S')

        restar_meses = datetime.timedelta(days=30*meses)
        diferencia = fecha_maxima- restar_meses


        print(self.getMatriz()[self.getMatriz()['Fecha']> pd.to_datetime(str(diferencia))].shape[0])
        print(fecha_maxima)
        print(fecha_maxima - restar_meses)


accion1 = Portafolio()
#accion1.setAccion()
#accion1.retornos()
#accion1.variacion()
#print(list(accion1.getMatriz()['Tesla']))
#print(accion1.medias(20,1))
#print(accion1.medias(10,1))

#accion1.covar()

#print(accion1.getMatriz().tail(10))
#accion1.guardar('ejemplo_portafolio')

#accion1.grafico_individual('ECO',guardar = False,meses=2)
#accion1.analisis()
#accion1.pruebas()
accion1.grafico_total()
#accion1.grafico_comparativo('DAX','AMZN',True)

#PENDIENTES
#grafico total - quitar eje x, poner solo al último gráfico

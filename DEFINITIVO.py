import pandas as pd
from pandas import Series
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes
import weibull
from scipy import integrate

def validar(I,Dir,Q,Spd,Q1):
    data['Error']=0
    data.loc[((Dir==999) | (Spd==999.9) | (I==9) | (Q==9) | (Q1==9)),'Error']=1

def check_inval(check):
    data_inval = data[check!=0]
    return data_inval

def check_val(check):
    data_val = data[check==0]
    return data_val

def cantidad(x):
    x = pd.pivot_table(x,values='Spd',index=['Año','Mes'],aggfunc=[Series.count])
    return x

def velocidad(x,ind,a,s,m):
    if ((a!=0)&(s=='0')&(m==0)):
        x=x[(x['Año']==a)]
    if ((a!=0)&(s=='0')&(m!=0)):
        x=x[(x['Año']==a)&(x['Mes']==m)]
    if ((a!=0)&(s!='0')&(m==0)):
        x=x[(x['Año']==a)&(x['Season']==s)]
    if ((a==0)&(s=='0')&(m==0)):
        x=x[(x['Mes']==m)]
    if ((a==0)&(s!='0')&(m==0)):
        x=x[(x['Season']==s)]
    x = pd.pivot_table(x,values='Spd',index=ind,aggfunc=[Series.count,Series.mean,Series.max,Series.min,Series.median])
    print(x)
        
def data_rosa(x,ind,a,s,m):
    ind.append('Dir')
    if ((a!=0)&(s=='0')&(m==0)):
        x=x[(x['Año']==a)]
    if ((a!=0)&(s=='0')&(m!=0)):
        x=x[(x['Año']==a)&(x['Mes']==m)]
    if ((a!=0)&(s!='0')&(m==0)):
        x=x[(x['Año']==a)&(x['Season']==s)]
    if ((a==0)&(s=='0')&(m==0)):
        x=x[(x['Mes']==m)]
    if ((a==0)&(s!='0')&(m==0)):
        x=x[(x['Season']==s)]   
    x = pd.pivot_table(x,values='Spd',index=ind,aggfunc={'Spd':[Series.count,Series.mean,Series.max]})
    print(x)
        
def rosa(x):
    ax1 = WindroseAxes.from_ax()
    ax1.bar(x['Dir'],x['Spd'], normed=True, opening=0.8, edgecolor='white')
    ax1.set_legend()
    frecuencia(ax1)

def frecuencia(ax1):
    table = ax1._info['table']
    wd_freq = np.sum(table, axis=0)
   
def estacion(mes, dia):
    data['Season']='Invierno'
    data.loc[(((mes>=3) & (dia>19)) | (mes>3)),'Season']='Primavera'
    data.loc[(((mes>=6) & (dia>20)) | (mes>6)),'Season']='Verano'
    data.loc[(((mes>=9) & (dia>22)) | (mes>9)),'Season']='Otoño'
    data.loc[((mes>=12) & (dia>20)),'Season']='Invierno'
      
def epoch():
    data.loc[:,'Año']=data.loc[:,'Date']//10000
    data.loc[:,'Mes']=data.loc[:,'Date']%10000//100
    data.loc[:,'Dia']=data.loc[:,'Date']%10000%100
    
def weib(x):
    plt.figure()
    data_weib=weibull.Analysis(x['Spd'],unit='m/s')
    data_weib.fit()
    data_weib.pdf(False)
    plt.hist(x['Spd'],density=True)
    #Utiliza de forma estandar 
    print('Scale: {} \n Shape: {} \n'.format(data_weib.beta,data_weib.eta))
    return data_weib.beta,data_weib.eta

def weib_dens(x,n,a):
     return (a / n) * (x / n)**(a - 1) * np.exp(-(x / n)**a)

def dens_energ(x,scale,shape):
    x.loc[:,'Spd^3']=pow(x.loc[:,'Spd'],3)
    x.loc[:,'f(u)']=weib_dens(x['Spd'],shape,scale)
    x.loc[:,'u^3*f(u)']=x.loc[:,'Spd^3']*x.loc[:,'f(u)']
    y = pd.pivot_table(x,values='f(u)',index=['Spd','Spd^3','u^3*f(u)'],aggfunc=[Series.mean])
#    for i in range(y['mean']['f(u)'].count()):
    u=y['mean']['f(u)'].index.get_level_values('Spd').tolist()
    u3=[]
    for i in u:
        u3.append(i**3)
    j=u3*weib_dens(u,shape,scale)
    #Regla de cuadratura comun
    media_num=integrate.simps(j,u)
    j=weib_dens(u,shape,scale)
    DEN=integrate.simps(j,u)
    MEDIA = 0.5*1.225*(media_num/DEN)
    u4=[]
    for i in u:
        u4.append((i**3-(media_num/DEN))*(i**3-(media_num/DEN)))
    j= u4*weib_dens(u,shape,scale)
    desv_num=integrate.simps(j,u)
    DESVIACION = pow(pow(0.5*1.225,2)*(desv_num/DEN),0.5)
    print(MEDIA, '\n', DESVIACION,'\n')


def main(data, data_val, busqueda, index, a, s, m):
    velocidad(data_val, index, a, s, m)
    #Informacion detallada de la velocidad del viento en funcion del año, mes y direccion
    data_rosa(data_val,index, a, s, m)
    #Tabla completa de la velocidad segun meses y direcciones
    rosa(busqueda)
    #Poner año y mes que se desea o quitar lo que se quiera
    scale, shape = weib(busqueda)
    #Calcula las constantes de la distribucion de Weibul y genera las gráficas
    dens_energ(busqueda,scale,shape)
    #Calcula la media y la desviacion tipica de la densidad de energia

def validar_freq(i, data_año):    
    for j in list(range(data_año['Mes'].min(),data_año['Mes'].max()+1)):
        if (data_año[data_año['Mes']==j].count()[0]<720):
            data.loc[(data['Año']==i)&(data['Mes']==j),'Error']=1
   
        

data_brute1 = pd.read_csv('C:\Master\Fuentes de Energía\Ejercicio_Eolica\Destinos\Burgos\DataModif.txt', sep=",", header=None)
data_brute2=data_brute1.iloc[:,0:13]
data_brute2.columns = ['Name','USAF','NCDC','Date','HrMn','I','Type','QCP','Dir','Q','I1','Spd','Q1']
data=data_brute2.loc[:,['Date','HrMn','I','Dir','Q','Spd','Q1']]

validar(data['I'],data['Dir'],data['Q'],data['Spd'],data['Q1'])
#Crea una fila donde determina si la medida tiene un valor erroneo
epoch()
#Crea la columna de mes y año para todos los datos
estacion(data['Mes'],data['Dia'])
#Clasifica todas las medidas en funcion de la estacion
    
data_cant=cantidad(data)
#Crea tabla con número de medidas por año y por mesç

for i in list(range(data['Año'].min(),data['Año'].max()+1)):
    validar_freq(i, data[data['Año']==i])

data_inval=check_inval(data['Error'])
#Clasifica los datos en aquellos que tienen error
cantidad(data_inval)
#Crea tabla con número de medidas por año y por mes NO validas
    
data_val=check_val(data['Error'])
#Clasifica los datos en aquellos que no tiene error
data_cant_val=cantidad(data_val)
#Crea tabla con número de medidas por año y por mes SI validas

print('Escribe el año donde desea buscar (si solo desea meses o estaciones escriba 0):')
a=int(input())
print('Escriba la estacion que quieres buscar o 0 si quieres Meses:')
s=input()
m=0
#De base
if (s=='0'):
    print('Escribe el mes donde desea buscar (si solo desea años escriba 0):')
    m=int(input())   

if ((a!=0) & (s!='0')):
    busqueda=data_val[(data_val['Año']==a)&(data_val['Season']==s)]
    index=['Año','Season']
if ((a!=0) & (s=='0') & (m!=0)):
    busqueda=data_val[(data_val['Año']==a)&(data_val['Mes']==m)]
    index=['Año','Mes']
if ((a!=0) & (s=='0') & (m==0)):
    busqueda=data_val[(data_val['Año']==a)]
    index=['Año']    
if ((a==0) & (s=='0') & (m!=0)):
    busqueda=data_val[(data_val['Mes']==m)]
    index=['Mes']
if ((a==0) & (s!='0') & (m==0)):
    busqueda=data_val[(data_val['Season']==s)]
    index=['Season']


main(data, data_val, busqueda, index, a, s, m)







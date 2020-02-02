import csv
import os
from datetime import timedelta, date
import datetime
import time
import operator

#global
diccHorasTrabajadas = {}

def process_shifts(path_to_csv):
    """

    :param path_to_csv: The path to the work_shift.csv
    :type string:
    :return: A dictionary with time as key (string) with format %H:%M
        (e.g. "18:00") and cost as value (Number)
    For example, it should be something like :
    {
        "17:00": 50,
        "22:00: 40,
    }
    In other words, for the hour beginning at 17:00, labour cost was
    50 pounds
    :rtype dict:
    """


    if os.path.exists(path_to_csv):

        fichero = csv.DictReader(open(path_to_csv))
        #["fichero" = obj 'DictReader']

        # new array to save data from .csv
        workers = []

        #counter
        i=0

        # data from .csv
        for row in fichero:
            i+=1
            
            valores = list(row.values())
            claves = list(row.keys())

            # x es un diccionario con cada trabajador como keys y values
            x = dict(zip(claves, valores))
            workers.append(x)
           
            # creo variables para guardar lo que me saca del excel:
                ### por cada fila ( = por cada trabajdor )
            breakNotes = workers[i-1]['break_notes']
            end=formateoHora(workers[i-1]['end_time'])
            payRate = float(workers[i-1]['pay_rate'])
            init = formateoHora(workers[i-1]['start_time'])

            # format of variables:
            ### BREAKTIME: creo un array con dos valores, el inicio[0] y el fin[1]
            a = breakNotes.replace(" ", "")
            b = a.split("-")

            ### BREAKTIME#2: formateo para que me devuelva la hora "00:00:00"
            b0 = formateoHora(b[0])
            b1 = formateoHora(b[1])

            # format of data OK, now analysis:
            generarHorasTrabajadas(init, b0, b1, end, payRate)

    return diccHorasTrabajadas


def formateoHora(hora):              
    # recibe hora en tipo string
    hora = hora.replace(".",":")       
    # de 3.10PM a 3:10PM
    if("PM" in hora and ":" in hora):   
    # 3:10PM
        formato = "%I:%M%p"
    elif("PM" in hora):                
    # 4PM
        formato = "%I%p"
    elif(":" in hora):                  
    # 20:30
        formato = "%H:%M"
    else:                              
    # 15
        formato = "%H"

    # transformar objecto datetime
    formato_datetime = datetime.datetime.strptime(hora, formato)
    #print("formato_datetime: ", formato_datetime)
    formato_time = formato_datetime.time()

    return formato_time


def formato2decimales(numero):
    numFormateado = round(numero,2)
    return numFormateado


def generarHorasTrabajadas(inicioTrabajo, inicioBreak, finBreak, finTrabajo, rate):

    hInit=inicioTrabajo.hour

    hStarBreak=inicioBreak.hour
    mStarBreak=inicioBreak.minute

    hEndBreak=finBreak.hour
    mEndBreak=finBreak.minute

    hFin=finTrabajo.hour

    #verify if the breaktime is between working hours
    if not (hInit <= hStarBreak and hStarBreak <= hFin):
        hStarBreak += 12
        inicioBreak = datetime.time(hStarBreak, mStarBreak)
    if not (hInit <= hEndBreak and hEndBreak <= hFin and hEndBreak >= hStarBreak):
        hEndBreak += 12
        finBreak = datetime.time(hEndBreak, mEndBreak)
    
    excluirBreakTime(inicioTrabajo, inicioBreak, finBreak, finTrabajo, rate)


def excluirBreakTime(t1, t2, t3, t4, rate):
    #write on a global variable all paid hours
    paidHours(t1, t2, rate)
    paidHours(t3, t4, rate)

def paidHours(startT, endT, rate):
# checks the difference with the next hour and end_time. Depending on the difference it will add a full pay_rate, or it will calculate a percentage of worked_time(minutes)

    while(startT<endT):
        hora=startT.hour
        keyHora = (str(hora) +":00")
        diferencia = calcular_diferencia(datetime.time(hora+1), startT)
        diferencia_hasta_fin = calcular_diferencia(endT, startT)

        if(diferencia < 60 or diferencia_hasta_fin < 60):
            difencia_menor=buscarMenor(diferencia,diferencia_hasta_fin)
        
            if(keyHora in diccHorasTrabajadas):
                diccHorasTrabajadas[keyHora]+=formato2decimales((rate/60)*difencia_menor)
            else:
                diccHorasTrabajadas[keyHora]=formato2decimales((rate/60)*difencia_menor)
        else:
            if(keyHora in diccHorasTrabajadas):
                diccHorasTrabajadas[keyHora]+=formato2decimales(rate)
            else:
                diccHorasTrabajadas[keyHora]=formato2decimales(rate)
        startT=datetime.time(hora+1)

    
def buscarMenor(numero1, numero2):
    if(numero1 < numero2):
        return numero1
    else:
        return numero2
    
def calcular_diferencia(hora1, hora2):
    diferencia_objeto = datetime.datetime.combine(date.today(), hora1) - datetime.datetime.combine(date.today(), hora2)
    segundos = diferencia_objeto.total_seconds()
    return segundos // 60 # = minutes


def process_sales(path_to_csv):
    """

    :param path_to_csv: The path to the transactions.csv
        :type string:

    :return: A dictionary with time (string) with format %H:%M as key and
    sales as value (string),
    and corresponding value with format %H:%M (e.g. "18:00"),
    and type float)
    For example, it should be something like :
    {
        "17:00": 250,
        "22:00": 0,
    },
    This means, for the hour beginning at 17:00, the sales were 250 dollars
    and for the hour beginning at 22:00, the sales were 0.

    :rtype dict:
    """
    if os.path.exists(path_to_csv):
        #cargo con DictReader(lo separa por Keys)
        #[ahora "fichero" es un objeto tipo 'DictReader']
        fichero = csv.DictReader(open(path_to_csv))

        #counter
        i=0

        #new variable to save data from .csv
        dicTransactions = {}

        for row in fichero:
            i+=1
            valores = list(row.values())

            hora = (valores[1][0:2]+":00")
            amount = valores[0]

            if(hora in dicTransactions):
                dicTransactions[hora]+=float(amount)
                dicTransactions[hora] = formato2decimales(dicTransactions[hora])
                
            else:
                dicTransactions[hora] = float(amount) 
                #[1]es el time
                #[0]es el amount

    return dicTransactions


def compute_percentage(shifts, sales):
    """

    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """

    #print("\nHour","\t","Sales","\t","Labour"," ","%")

    # analisis will have data from both .csv: {time: labour_cost}
    analisis = {}

    for k, v in sorted(shifts.items(),key=lambda item:item[0]):
        
        if(k in sales):
            hr = formato2decimales((v*100)/sales[k])
            
        else:
            sales[k]=0.00
            hr = -v

        analisis[k]=hr
        
        #print('{}\t {}\t {}\t {}'.format(k, sales[k], v, hr))

    return analisis

def best_and_worst_hour(percentages):
    """

    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """
    #position [0] returns: profit = 0, and [1] returns time
    hora = 1

    # Calculate the best and worst hour:
    bestHour = max(zip(percentages.values(), percentages.keys()))
    worstHour = min(zip(percentages.values(), percentages.keys()))

    return [bestHour[hora], worstHour[hora]]

def main(path_to_shifts, path_to_sales):

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "transactions.csv"
    path_to_shifts = "work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)
    print("Best HH: ", best_hour, " and the worst Hour: ", worst_hour)

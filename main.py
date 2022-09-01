import requests, json
import pandas as pd  
import time  
import configparser   
from rich.console import Console  
from rich import print

console = Console()

config = configparser.ConfigParser()
config.read('config.ini', "utf8")  
ruta = config['DEFAULT']['ruta'] 
s_proxy = config['DEFAULT']['proxy'] 

lista1 = config['SUCURSALES']['LISTA1'].split(',') 
lista2 = config['SUCURSALES']['LISTA2'].split(',') 
lista3 = config['SUCURSALES']['LISTA3'].split(',') 
lista4 = config['SUCURSALES']['LISTA4'].split(',')
sucursal = lista1 + lista2 + lista3 + lista4

extension_sucursales = []
 
precio_lista = [] 
precio_promocion = [] 
stock = [] 
nombre = [] 
enlace = [] 
categoria = [] 
descripcion = [] 
sku = []     

count = 0 
error_url = 0 


class crawler():
    

    def __init__(self): 
        for z in range(1,17):   
            extension = f"&ft&sc={z}"  
            
            if z == 5:
                continue 
            extension_sucursales.append(extension)  

    
    def extraer_links(self, extension):  
        start = time.time()
        desde = 0 
        hasta = 23  
        global error_url 
        global count 

        precio_lista.clear()
        precio_promocion.clear()
        stock.clear()
        nombre.clear() 
        enlace.clear()
        categoria.clear() 
        descripcion.clear()
        sku.clear()  
        console.print(f"[bold][red]\nExtrayendo productos de la sucursal de: [white]{sucursal[count]}.\n")
        try:
            for n in range(0, 2000):  
                
                url = f"https://www.hiperlibertad.com.ar/api/catalog_system/pub/products/search/api?O=OrderByTopSaleDESC&_from={desde}&_to={hasta}{extension}"  
                
                proxy = { url: s_proxy } 
                
                
                api = requests.get(url, proxies=proxy) 
                texto = api.text 
                if len(texto) <= 1000: 
                    break
                desde+=24
                hasta+=24
                
                df = pd.DataFrame(crawler.extraer_data(self, texto))  
        except:  
            error_url+=1
            console.print(f"[bold][red]No se puede extraer datos de esta url:[white] {url}.") 
            console.print(f"[bold][red]Cantidad de urls que no se pudieron extraer:[white] {error_url}.")
             
        
        if len(ruta) == 0:  
            df.to_csv(f"{sucursal[count]}.csv", index=False)
        else: 
            df.to_csv(rf"{config['DEFAULT']['ruta']}\{sucursal[count]}.csv", index=False)

         
        end = time.time() 
        resultado = end - start 
        min = (resultado/60) 
        float_min = ("{:.2f}".format(min)) 
        console.print(f"[bold][green]\nTiempo final de extraccion: [white]{float_min}.") 
        rows = len(df.index)      
        console.print(f"[bold][green]Total de productos extraidos: [white]{rows}.") 
        console.print(f"[bold][green]Nombre del archivo csv: [white]{sucursal[count]}.") 
        console.print(f"[bold][green]Guardado en: [white]{config['DEFAULT']['ruta']}\n")   
        count+=1   


    def extraer_data(self, texto): 
        i = 0    
        error = 0
        try:
            while True: 
            
                data = json.loads(texto)
                data = data[i]  
                
                
                enlace.append(data["link"]) 
                sku.append(data["productReferenceCode"]) 
                descripcion.append(data["description"]) 
                categoria.append(data["categories"][0])  
                

                anidado1 = data["items"]
                anidado2 = []
                for elem in anidado1:     
                    for k,v in elem.items():       
                        if k == "sellers": 
                            anidado2.append(v)  
                        if k == "nameComplete":  
                            nombre.append(v)

                anidado3 = anidado2[0] 
                anidado4 = []
                for elem in anidado3:     
                    for k,v in elem.items():       
                        if k == "commertialOffer": 
                            anidado4.append(v) 

                
                for elem in anidado4:     
                    for k,v in elem.items():         
                        if k == "ListPrice": 
                            precio_lista.append(v)   
                        if k == "Price": 
                            precio_promocion.append(v)   
                        if k == "AvailableQuantity": 
                            stock.append(v)
                
                i+=1 
                if i == 24:  
                    datos = { 
                        "Nombre del producto": nombre, 
                        "Descripcion": descripcion, 
                        "Categoria": categoria, 
                        "Precio de lista": precio_lista, 
                        "Precio con descuento": precio_promocion, 
                        "Link del producto": enlace, 
                        "Stock": stock, 
                        "Sku (codigo de referencia)": sku
                    } 
                    break   
            
            return datos 
        except:  
            error+=1
            console.print(f"[bold][red]No se pudieron extraer los productos de esta pagina.") 
            console.print(f"[bold][red]Cantidad de errores en esta sucursal: {error}.")


if __name__ == "__main__": 
    console.print(f"[bold][red]\nChallenge - Autoscraping.\n")
    inn = crawler() 
    
    for n in extension_sucursales:
        inn.extraer_links(n)
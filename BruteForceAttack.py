
key = "antonio"

file = open("passwd.txt", "w")
lista_solo_key = list()
for i in range(0, len(key)):
    for j in range(0, len(key) + 1):
        temp = key[0:i] + key[i:i + j].upper() + key[i + j:len(key)]
        lista_solo_key.append(temp)

lista_solo_key = list(dict.fromkeys(lista_solo_key))
for i in lista_solo_key:
    file.write(i)
    file.write("\n")


for i in range(0,len(lista_solo_key)):
    for j in range(0,10000):
        temp = lista_solo_key[i] + str(j).zfill(4)
        file.write(temp)
        file.write("\n")

for i in range(0,len(lista_solo_key)):
    for j in range(0,10000):
        temp = str(j).zfill(4) + lista_solo_key[i]
        file.write(temp)
        file.write("\n")
file.close()
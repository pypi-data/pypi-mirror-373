'''
Created on 21 Mar 2024

@author: jacklok
'''

import random
import csv

prefix = '8810001'
start_number = 80001
end_number =   90001

def calc_checkbit(number):
  return str((10 - sum((3, 1)[i % 2] * int(n) for i, n in enumerate(reversed(number)))) % 10)

fptr = open('/Users/jacklok/tmp/hnl-cards-80001-90000.csv','w+')
writer= csv.writer(fptr)
writer.writerow(['qr_number_print_on_card', 'qr_code', 'pin'])

#cardnumbers = []
for i in range(start_number,end_number):
  tempstr = prefix + str(i)
  ean13 = tempstr + calc_checkbit(tempstr)
  pin = ''.join(random.choice('0123456789') for _ in range(6))
  textoncard = ean13[0:3] + ' ' + ean13[3:6] + ' ' + ean13[6:] 
  #cardnumbers.append((ean13, pin))
  writer.writerow([textoncard, ean13, pin])

fptr.close()


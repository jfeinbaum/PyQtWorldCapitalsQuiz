data = {}

fp = open('countriescapitals.txt', 'r')
for line in fp.readlines():
        country, capitals = line.split(': ')
        data[country] = capitals
fp.close()

fp = open('countriescapitals.txt', 'w')
fp.write(str(data))
fp.close()
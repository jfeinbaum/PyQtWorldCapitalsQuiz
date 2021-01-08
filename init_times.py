countries = []

fp = open('countriescapitals.txt', 'r')
for line in fp.readlines():
        country, capitals = line.split(': ')
        countries.append(country)
fp.close()

fp = open('countrytimes.txt', 'w')
for country in countries:
    fp.write(country + ': 0\n')
fp.close()
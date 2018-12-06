from __future__ import print_function
import csv

total = 0
recent_sales = []
with open('data/home_values.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        year = row.get('Closed Roll Year')
        if not year:
            continue

        year = int(year)
        if year < 2016:
            continue

        sales_date = row.get('Current Sales Date')
        if sales_date > '2016':
            recent_sales.append(row)
            print(sales_date)

print('total', total)
print('recent', len(recent_sales))


def dump_csv(filename, rows):
    with open(filename, 'w') as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

dump_csv('generated/recent_sales.csv', recent_sales)

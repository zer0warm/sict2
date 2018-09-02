import urllib.request as urlreq
import json
import shutil
from datetime import datetime
import textwrap
import sys

# Description size must be dynamic because of different dishes, but other columns are stable
def drawAsciiTable(entries, descriptionSize, sdate=''):
    tableWidth = 21 + 2 + descriptionSize
    windowSize = shutil.get_terminal_size()[0]
    if tableWidth > windowSize:
        descriptionSize = windowSize - 21 - 2
    if descriptionSize <= 0:
        sys.exit("Min width must be 24")
    
    table = []
    line = '+---+' + '-' * (descriptionSize + 2) + '+------+-------+\n'
    table.append(line)
    
    for row in entries:
        wrappedDescription = textwrap.wrap(row[1], width=descriptionSize)
        row[3] = row[3].replace(' ', '')
        
        table.append("| {} |".format(row[0]))
        table.append(" {}".format(wrappedDescription.pop(0)).ljust(descriptionSize + 2))
        table.append("| {} | {} |\n".format(row[2], row[3].center(5)))
        
        # If the description is wrapped, it is displayed here
        while wrappedDescription:
            table.append("|   |")
            table.append(" {}".format(wrappedDescription.pop(0)).ljust(descriptionSize + 2))
            table.append("|      |       |\n")
           
        table.append(line)
    
    print('Lunch menu as of ' + (sdate if sdate else 'today'))
    print(*table, sep='', end='')
    print('G: Gluton free, L: Lactose free, M: Milk free')
    
def getDescriptionSize(menu):
    return max([len(section['title_en']) for section in menu])
    
def requestMenuData(sdate=''):
    baseUrl = 'https://www.sodexo.fi/ruokalistat/output/daily_json/54/'
    requestDate = datetime.today() if not sdate else datetime(*map(int, sdate.split('/')))
    requestUrlPattern = datetime.strftime(requestDate, '%Y/%m/%d') + '/en'
    try:
        urlHandler = urlreq.urlopen(baseUrl + requestUrlPattern)
        jsonResult = json.loads(urlHandler.read())
        return jsonResult['courses'], datetime.strftime(requestDate, '%d/%m/%Y')
    except:
        sys.exit("Error occurred. Check your Internet connection.")
    finally:
        urlHandler.close()
    
def processLunchMenu(menu):
    descriptionSize = 0
    entries = [['#', 'Dish', 'Cost', 'Notes']]
    order = 1
    if menu:
        descriptionSize = getDescriptionSize(menu)
        for section in menu:
            title = section['title_en'].strip()
            title = title[0].upper() + title[1:]

            entries.append([
                str(order),
                title,
                section['price'].split('/')[0].strip(),
                section['properties'] if 'properties' in section else '     '
            ])
            order += 1
    else:
        sys.exit("No data was retrieved. The cantin might not open on the specified day.")
        
    return entries, descriptionSize

def main(signal):
    if signal:
        jsonResult, date = requestMenuData(signal)
        drawAsciiTable(*processLunchMenu(jsonResult), date)
    else:
        jsonResult, date = requestMenuData()
        drawAsciiTable(*processLunchMenu(jsonResult))
    
def parseCmdArgs():
    if len(sys.argv) == 1:
        return None
    elif len(sys.argv) == 3 and sys.argv[1] == '-s':
        return sys.argv[2]
    else:
        sys.exit("Usage: [python] sict2[.py] [-s <YYYY>/<MM>/<DD>]")

if __name__ == '__main__':
    main(parseCmdArgs())

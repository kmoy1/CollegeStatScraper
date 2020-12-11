import os
import io
import csv   
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

def toCm(fi):
    """Convert height in FEET-INCHES string to centimeters"""
    import re
    feet, inches = re.match(r'(\d)-(\d)', fi).groups()
    return round((12 * int(feet) + int(inches)) * 2.54, 0)

def toKg(lb):
    """Convert pounds to kg."""
    return round(int(lb) * 0.453592, 0)

def draft_url(year):
    url = "https://basketball.realgm.com/nba/draft/past_drafts/{yr}".format(yr=year)
    return url

def collegeStats(player_soup):
    """Given player soup, get PPG in college OR overseas OR wherever the fuck else."""
    try:
        stats = player_soup.find('td', string='NCAA DI').parent.find_all('td')
        return [s.text for s in stats]
    except:
        return None

def internationalStats(player_soup):
    """Given player page, get international stats of the LAST year played."""
    try:
        stat_rows = player_soup.find('td', id='teamLineinternational_reg_Per_Game_1').parent.parent.find_all('tr')
        year_stats = [r for r in stat_rows if r.find('td',string='All Teams')]
        last_year_stats = year_stats[-1].find_all('td')
        return [s.text for s in last_year_stats]
    except:
        return None

def internationalStatsTry2(player_soup):
    """Given player page, get international stats of the LAST year played."""
    try:
        stat_rows = player_soup.find('td', id='teamLineinternational_reg_Per_Game_1').parent.parent.find_all('tr')[-1]
        return [s.text for s in stat_rows.find_all('td')]
    except:
        return None

def gleagueStats(player_soup):
    try:
        stat_rows = player_soup.find('td', id='teamLinedleague_reg_Per_Game_1').parent.parent.parent.find('tfoot').find('tr').find_all('td')
        return [s.text for s in stat_rows]
    except:
        return None


test = io.open('absolutelyfinalhoopers.csv', mode='w', encoding='utf-8', newline='')
out = csv.writer(test)
out.writerow(['Name', 'Pick', 'Draft Year', 'Position', 'Draft Height', 'Draft Weight', 'Draft Age', 'College', 'Useless1', 'Useless2', 'useless3', 
'GP','GS', 'MIN', 'FGM','FGA', 'FG%', '3PM', '3PA', '3P%','FTM', 'FTA', 'FT%', 'OFF', 'DEF', 'TRB', 'AST', 'STL', 'BLK', 'PF', 'TOV', 'PTS'])


years = list(range(2010, 2020))
for year in years:
    draft_soup = BeautifulSoup(urlopen(draft_url(year)), 'html.parser') #Soup for draft page.
    draft_rows = draft_soup.find_all('table')
    FR = draft_rows[0] #First round
    SR = draft_rows[1] #Second r
    first_round_rows = FR.find('tbody').find_all('tr')
    second_round_rows = SR.find('tbody').find_all('tr')

    for row in first_round_rows + second_round_rows:
        #Get name, pick, draft year.
        info = row.find_all('td')
        pick = int(info[0].text)
        name = info[1].text
        position = info[4].text
        draft_height = toCm(info[5].text)
        draft_weight = toKg(info[6].text)
        draft_age = info[7].text
        college = info[9].text
        yr = year
        player_href = row.find('a')['href']
        player_url = "https://basketball.realgm.com" + player_href
        player_soup = BeautifulSoup(urlopen(player_url), 'html.parser') #Soup for draft page.
        #Look for college stats first. 
        found_stats = False
        print("Searching stats for", name)
        stats = collegeStats(player_soup)
        
        if not stats:
        #Search International (Multiple teams).
            stats = internationalStats(player_soup)
        if not stats:
        #Search International, (single team)
            stats = internationalStatsTry2(player_soup)
        if not stats:
        #Search G-League.
            stats = gleagueStats(player_soup)
        if stats:
            out.writerow([name,pick, year, position, draft_height, draft_weight, draft_age, college] + stats)
        else:
            print(name,"did not play in college/internationally/gleague")
            out.writerow([name,pick, year, position, draft_height, draft_weight, draft_age, college] + [None for i in range(25)])

#player_href = draft_soup.find('table').find('tbody').find('a')['href']


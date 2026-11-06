import sys, re, html, urllib.request, time, json
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
out = {}
for z in sys.argv[1:]:
    t = urllib.request.urlopen(urllib.request.Request(f"https://www.house.gov/htbin/findrep?ZIP={z}", headers={'User-Agent': UA}), timeout=60).read().decode('utf-8', 'replace')
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    i = t.find('Your Possible Representatives'); i = i if i >= 0 else t.find('Your Representative')
    seg = t[i:t.find('U.S. House of Representatives Washington', i)] if i >= 0 else ''
    out[z] = re.findall(r"([A-Z][\w.'\- ]+?) (?:Republican|Democrat|Democratic|Independent) ([A-Z][a-z]+(?: [A-Z][a-z]+)*) District (\w+(?: \w+)?)", seg) or ('NO-MATCH: ' + seg[:150] if seg else 'NO-SEGMENT')
    print(z, out[z]); time.sleep(1)

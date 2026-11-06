import json, sys, collections
FIPS = {'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE','11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY','60':'AS','66':'GU','69':'MP','72':'PR','78':'VI'}
def load(p):
    d = json.load(open(p))["data"]
    m = collections.defaultdict(set)
    for r in d["results"]:
        m[r["zip"]].add(r["geoid"])
    return d["year"], d["quarter"], m
qs = [load(p) for p in sys.argv[1:]]
for (y, q, m) in qs:
    st = collections.Counter(g[:2] for s in m.values() for g in s)
    cds = {g for s in m.values() for g in s}
    print(f"{y}Q{q}: zips={len(m)} distinct CDs={len(cds)} multi={sum(len(s)>1 for s in m.values())} crossstate={sum(len({g[:2] for g in s})>1 for s in m.values())} odd={sorted(g for g in cds if g[:2] not in FIPS or g[2:] in ('98','99','ZZ'))[:10]}")
for a, b in zip(qs, qs[1:]):
    (y1,q1,m1),(y2,q2,m2) = a, b
    ch = collections.Counter(); tot = collections.Counter()
    for z in set(m1) & set(m2):
        s = next(iter(m2[z]))[:2]; tot[s] += 1
        if m1[z] != m2[z]: ch[s] += 1
    big = [(FIPS.get(s,s), c, tot[s]) for s, c in ch.most_common() if c >= 5]
    print(f"{y1}Q{q1} -> {y2}Q{q2}: changed zips={sum(ch.values())}; by state (>=5): {big[:15]}")

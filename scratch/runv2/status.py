import json, subprocess, shutil
uip=shutil.which("uip"); FK="ecd0827e-fc8c-49b7-953d-3f05c1661066"
def run(*a):
    p=subprocess.run([uip,*a,"--output","json"],capture_output=True,text=True); d=json.loads(p.stdout)
    if "Data" not in d: raise SystemExit(f"{a[:3]} -> {d}")
    return d
started={s['ticket']:s['resp']['Data']['Jobs'][0]['Key'] for s in json.load(open('started.json'))}
inst={i['InstanceId']:i for i in run("maestro","flow","instance","list","-f",FK,"--package-id","TicketTriage_TEAMjohannes-reitermayer.6.flow.TriageTicketV2","--from-date","2026-09-13T12:30:00Z","--limit","50")['Data']}
tasks=[t for t in run("tasks","list","--folder-key",FK)['Data'] if not t['IsCompleted'] and not t['IsDeleted']]
done=0
for tk,jk in started.items():
    i=inst.get(jk); st=i['LatestRunStatus'] if i else 'no-instance'
    ts=[t for t in tasks if t.get('CreatorJobKey')==jk]
    tdesc=", ".join(f"{t['Title']} [{t['Priority']}, {t['Status']}, id {t['Id']}]" for t in ts)
    ok = st=='Completed' or bool(ts)
    done+=ok
    inc=len(i['Incidents']) if i and i.get('Incidents') else 0
    print(f"{tk}  job {jk}  instance={st}  incidents={inc}  task={tdesc or '-'}  {'OK' if ok else 'WAIT'}")
print(f"{done}/{len(started)} settled")

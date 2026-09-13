import json, subprocess, shutil
uip=shutil.which("uip"); FK="f19c7f55-614a-4d7e-9d9e-b1461b8f4e11"
def run(*a):
    p=subprocess.run([uip,*a,"--output","json"],capture_output=True,text=True)
    try: d=json.loads(p.stdout)
    except Exception: raise SystemExit(f"{a[:3]} -> {p.stdout} {p.stderr}")
    if "Data" not in d: raise SystemExit(f"{a[:3]} -> {d}")
    return d['Data']
started={s['ticket']:s['resp']['Data']['Jobs'][0]['Key'] for s in json.load(open('started.json'))}
tasks=run("tasks","list","--folder-key",FK)
tasks=tasks.get('Items',tasks) if isinstance(tasks,dict) else tasks
tasks=[t for t in tasks if not t.get('IsDeleted')]
rows=[];done=0
for tk,jk in started.items():
    j=run("or","jobs","get",jk)
    ts=[t for t in tasks if (t.get('CreatorJobKey') or '').lower()==jk.lower()]
    st=j.get('State'); settled = st in ('Successful','Faulted','Stopped') or (st=='Suspended' and ts)
    done+=bool(settled)
    oa=j.get('OutputArguments')
    try: oa=json.loads(oa) if isinstance(oa,str) and oa else oa
    except Exception: pass
    rows.append({"ticket":tk,"job":jk,"state":st,"out":oa,"tasks":[{k:t.get(k) for k in ('Id','Title','Priority','Status','IsCompleted','Type','AssignedToUser')} for t in ts],"info":j.get('Info')})
    print(f"{tk} {st:10} tasks={[ (t['Id'],t['Priority'],t['Status']) for t in ts]} out={json.dumps(oa)[:160] if oa else '-'}")
print(f"{done}/{len(started)} settled")
json.dump(rows,open('status.json','w'),indent=2)

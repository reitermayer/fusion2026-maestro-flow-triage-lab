import json, subprocess, shutil, glob
uip=shutil.which("uip")
def run(*a):
    p=subprocess.run([uip,*a,"--output","json"],capture_output=True,text=True,encoding="utf-8")
    try: d=json.loads(p.stdout)
    except Exception: return {"_err":p.stdout+p.stderr}
    return d
FOLDERS={"A":"f15d2bb8-1c03-4408-a5d2-2a9c2b244ed9","B":"ecd0827e-fc8c-49b7-953d-3f05c1661066","C":"f19c7f55-614a-4d7e-9d9e-b1461b8f4e11"}
out={}
for b,fk in FOLDERS.items():
    t=run("tasks","list","--folder-key",fk)
    data=t.get("Data",t)
    items=data.get("Items",data) if isinstance(data,dict) else data
    tasks=[]
    for x in items if isinstance(items,list) else []:
        if x.get("IsDeleted"): continue
        d=run("tasks","data","get",str(x["Id"]),"--folder-key",fk).get("Data",{})
        fd=d.get("Data",{}) if isinstance(d,dict) else {}
        fd={k.lower():v for k,v in (fd or {}).items()}
        tasks.append({k:x.get(k) for k in ("Id","Title","Priority","Status","Action","CreatorJobKey","CreatedTime","CompletedTime")}|{"ticket":fd.get("ticketid"),"category":fd.get("category"),"priority_field":fd.get("priority"),"confidence":fd.get("confidence"),"note":fd.get("reviewernote")})
    out[b]={"tasks":tasks,"err":t.get("_err")}
jobs={}
for b,f in (("B","runv2/started.json"),("C","ch11/started.json")):
    for s in json.load(open(f)):
        jk=s["resp"]["Data"]["Jobs"][0]["Key"]
        j=run("or","jobs","get",jk).get("Data",{})
        oa=j.get("OutputArguments")
        try: oa=json.loads(oa) if isinstance(oa,str) and oa else oa
        except Exception: pass
        jobs.setdefault(b,[]).append({"ticket":s["ticket"],"job":jk,"state":j.get("State"),"start":j.get("StartTime"),"end":j.get("EndTime"),"out":oa})
# Batch A jobs by CreatorJobKey
for t in out["A"]["tasks"]:
    j=run("or","jobs","get",t["CreatorJobKey"]).get("Data",{})
    oa=j.get("OutputArguments")
    try: oa=json.loads(oa) if isinstance(oa,str) and oa else oa
    except Exception: pass
    jobs.setdefault("A",[]).append({"ticket":t["ticket"],"job":t["CreatorJobKey"],"state":j.get("State"),"start":j.get("StartTime"),"end":j.get("EndTime"),"out":oa})
out["jobs"]=jobs
json.dump(out,open("ch12/live.json","w"),indent=1,ensure_ascii=False)
for b in "ABC":
    print("== Batch",b, out[b]["err"] or "")
    for t in sorted(out[b]["tasks"],key=lambda t:t["ticket"] or ""): print(" task",t["Id"],t["ticket"],t["Priority"],t["Status"],t["Action"],t["category"],t["priority_field"],t["confidence"])
    for j in sorted(jobs.get(b,[]),key=lambda j:j["ticket"] or ""):
        o=j["out"] or {}
        print(" job ",j["ticket"],j["state"],o.get("decision"),o.get("category"),o.get("priority"),o.get("kbCovered"),o.get("kbSources"),j["start"],j["end"])

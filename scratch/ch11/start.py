import json, subprocess, shutil
uip=shutil.which("uip"); FK="f19c7f55-614a-4d7e-9d9e-b1461b8f4e11"; REL="0064213f-3561-4017-8bbb-72ce78422088"
items=sorted(json.load(open('tickets.json'))['Data']['Items'],key=lambda r:r['TicketId'])
out=[]
for r in items:
    args={"ticketId":r['TicketId'],"subject":r['Subject'],"body":r['Body'],"customerName":r['CustomerName']}
    p=subprocess.run([uip,"or","jobs","start",REL,"--folder-key",FK,"--input-arguments",json.dumps(args),"--output","json"],capture_output=True,text=True)
    try: d=json.loads(p.stdout)
    except Exception: d={"raw":p.stdout,"err":p.stderr}
    out.append({"ticket":r['TicketId'],"resp":d})
    j=(d.get('Data') or {}).get('Jobs',[{}])[0]
    print(r['TicketId'], d.get('Result'), j.get('Key'), j.get('State'), j.get('CreationTime'), d.get('Message',''))
json.dump(out,open('started.json','w'),indent=2)

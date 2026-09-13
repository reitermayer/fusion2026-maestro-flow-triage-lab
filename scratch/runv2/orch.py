import json, os, sys, urllib.request, urllib.parse
def auth():
    d={}
    for l in open(os.path.expanduser("~/.uipath/.auth")):
        if "=" in l:
            k,v=l.strip().split("=",1); d[k]=v
    return d
A=auth()
BASE=f"{A['UIPATH_URL']}/{A['UIPATH_ORGANIZATION_NAME']}/{A['UIPATH_TENANT_NAME']}/orchestrator_"
def req(method, path, folder_key=None, body=None):
    h={"Authorization":"Bearer "+A["UIPATH_ACCESS_TOKEN"],"Content-Type":"application/json","User-Agent":"uip-cli-helper/1.0"}
    if folder_key: h["X-UIPATH-FolderKey"]=folder_key
    data=json.dumps(body).encode() if body is not None else None
    r=urllib.request.Request(BASE+path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            t=resp.read().decode(); return resp.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
if __name__=="__main__":
    m,p=sys.argv[1],sys.argv[2]; fk=sys.argv[3] if len(sys.argv)>3 else None
    b=json.loads(sys.argv[4]) if len(sys.argv)>4 else None
    s,o=req(m,p,fk,b); print(s); print(json.dumps(o,indent=2) if not isinstance(o,str) else o)

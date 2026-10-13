#!/usr/bin/env python3
"""Turn a page tree edit into minimal set_props operations.
usage: diffops.py old_tree.json new_tree.json > ops.json
Use the ops with sites_apply_operations in place of replace_tree on big pages."""
import json,sys
def idx(t):
    d={}
    def w(n,par=None,i=0):
        d[n['id']]=(n,par,i)
        for j,c in enumerate(n.get('children',[])): w(c,n['id'],j)
    w(t['root']);return d
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]))
A=idx(a);B=idx(b);ops=[];struct=[]
for k,(n,p,i) in B.items():
    if k not in A: struct.append(('new',k,p,i));continue
    o=A[k][0]
    if o['type']!=n['type'] or A[k][1]!=p or A[k][2]!=i: struct.append(('moved/type',k))
    sp={x:v for x,v in n.get('props',{}).items() if o.get('props',{}).get(x)!=v and x!='doc'}
    un=[x for x in o.get('props',{}) if x not in n.get('props',{}) and x!='doc']
    if sp or un:
        op={"op":"node.set_props","nodeId":k}
        if sp: op['set']=sp
        if un: op['unset']=un
        ops.append(op)
    if o.get('style')!=n.get('style'): ops.append({"op":"node.set_style","nodeId":k,"style":n.get('style')})
for k in A:
    if k not in B: struct.append(('removed',k))
if a.get('meta')!=b.get('meta'): ops.append(dict(op="page.set_meta",**b['meta']))
print(json.dumps(struct))
print(json.dumps(ops,ensure_ascii=False))

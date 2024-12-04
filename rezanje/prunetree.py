#!/usr/bin/env python3

import copy
import json
import pathlib
import functools as ft
import argparse as ap
import tkinter as tk
from tkinter import ttk
import graphviz as gv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import pandas as pd
import random
import sys
import os
from pathlib import Path

def gen_ex():
    names = "ABCDEFGHIJKLMNOPQR"
    # number of attributes
    na = random.randint(3,4)
    # attribute values
    av = [['abcdefghijklmnopqr'[r] for r in range(random.randint(2,3))] for i in range(na)]
    # max tree depth
    mtd = random.randint(2,na)-1
    # number of "test" values
    ntv = random.randint(10,15)
    # create "test" values
    tv = list(zip(*[random.choices(av[i], k=ntv) for i in range(na)]))
    test = pd.DataFrame(tv,columns=list(names[:na]))
    #test = test.rename(lambda x: x+' - class' if x==names[na-1] else x, axis='columns')
    dtree = dict()
    def gen_dtree(st,attr,arr,d,ats):
        if ats!=[]:
            rats = random.randint(0,len(ats)-1)
            sattr = ats[rats]
            #print(sattr,ats,names[sattr])
            ats=copy.deepcopy(ats)
            ats.pop(rats)
        else:
            rats, sattr = -1,-1
            #print(sattr,ats,names[sattr])
        st['attribute']=names[sattr]
        st['arrow']=arr
        st['classification']=random.choice(av[attr])
        st['subtrees']=[]
        if d<mtd and 0!=random.randint(0,9):
            for i in av[sattr]:
                st['subtrees']+=[dict()]
                gen_dtree(st['subtrees'][-1],sattr,i,d+1,ats)
        else:
            st['attribute']=''
    gen_dtree(dtree,random.randint(0,na-2),'',0,list(range(0,na-1)))
    if args.mep and not args.laplace:
        pa = dict()
        ns = [0]+[random.uniform(0,1) for i in range(len(av[na-1])-1)]+[1]
        ns.sort()
        for i in range(len(av[na-1])):
            pa['abcdefghijklmnopqr'[i]]=ns[i+1]-ns[i]
        dtree["pa"]=pa
        dtree['m']=random.randint(1,5)
    return dtree,test,names[na-1]

# preprocess step where classifications all calculated from table
# PRE: dtree is a valid decision tree, tbl is a table, valid attribute attr
# POST: returns dtree with correctly defined classification, classification#, focus, cut for each tree
def preprocess(dtree,tbl,attr):
    # get all classifications and remove duplicates
    vals = list(dict.fromkeys(tbl[attr]))
    def pp(dtree,tbl):
        # traverse tree
        for i,st in enumerate(dtree['subtrees']):
            dtree['subtrees'][i]=pp(st,tbl[tbl[dtree['attribute']]==st['arrow']])
        # calculate classification#
        if dtree['subtrees']==[]:
            # leaf
            dtree['classification#']=dict()
            for v in vals:
                dtree['classification#'][v]=len(tbl[tbl[attr]==v])
        else:
            # node
            nums=dict()
            # calculate classification from subtrees
            for st in dtree['subtrees']:
                for k,v in st['classification#'].items():
                    if k not in nums.keys():
                        nums[k]=0
                    nums[k]+=v
            dtree['classification#']=nums
        # set default values for cut, focus
        dtree['cut']='false'
        dtree['focus']='false'
        return dtree
    return pp(dtree,tbl)

# creates a trace of the REP method for tree dtree, prunning set test for attribute attr
# PRE: inputs are valid
# POST: returns trace of the REP prunning of the dtree
def rep(dtree):
    # traced REP method
    # PRE: gets valid decision tree with classification, classification#, cut, focus defined
    # POST: returns REP trace
    def repsub(dtree):
        r=[] # trace
        # create REP trace
        # PRE: empty trace r defined, dtree valid
        # POST: r is the REP trace of dtree
        def rs(st):
            nonlocal r
            # calculates the number of wrongly classified elements (by looking at classification#)
            # PRE: tree is valid decision tree (with classification, classification#)
            # POST: returns the number of (locally) wrongly classified elements
            def wrong(tree):
                r=0
                for key, value in tree['classification#'].items():
                    if key!=tree['classification']:
                        r+=value
                #print(tree['classification'],tree['classification#'],r)
                return r
            # traverse tree
            for sst in st['subtrees']:
                rs(sst)
            if st['subtrees']!=[]:
                # node
                st['focus']='true'
                calc=[]
                # calculate wrong
                # PRE: empty sum trace calc defined, st valid decision tree
                # POST: returns number of wrongly classified elements and calc is the trace by subtree
                def sub_scor(st):
                    nonlocal calc
                    r=0
                    for sst in st['subtrees']:
                        r+=wrong(sst)
                        calc+=[wrong(sst)]
                    return r
                # store number of wrongly classified elements in scor
                scor=sub_scor(st)
                # mark tree for prunning (if needed)
                nwcn=wrong(st)
                #for key, value in st['classification#'].items():
                #    if key!=st['classification']:
                #        nwcn+=value
                if nwcn<=scor:
                    for sst in st['subtrees']:
                        sst['cut']='true'
                # copy marked tree
                rst=copy.deepcopy(dtree)
                # set formulas
                rst['formulas']=[['(Number of wrong categorizations on current node) $=$',
                                  ' $=$ (Number of non-'+str(st['classification'])+') $='+str(nwcn)+'$'],
                                 ['(Number of wrong categorizations on subtrees) $=$',
                                  ' $='+ft.reduce(lambda x,y:str(x)+'+'+str(y),calc)+'='+str(scor)+'$'],
                                 ['$'+str(nwcn)+'\leq'+str(scor)+'$'if nwcn<=scor else'$'+str(nwcn)+'>'+str(scor)+'$'],
                                 ['PRUNE TREE'if nwcn<=scor else 'KEEP TREE']]
                # add marked decision tree with formulas to trace r
                r+=[rst]
                # prune tree (if needed)
                if nwcn<=scor:
                    st['subtrees']=[]
                # unfocus
                st['focus']='false'
        # execut
        rs(dtree)
        # set formulas for the "resulting" tree
        dtree['formulas']=[]
        # add "resulting" tree
        r+=[dtree]
        # add meta-information of the trace
        res=dict()
        res['trace']=r
        res['method']='REP'
        return res
    return repsub(dtree)

def mep(dtree, attr, pa=dict(), m=1, ca=False, lapl=False):
    # criteria for choosing "best" estimate
    better = max if ca else min
    # calculcates traced classification/static estimates on leafs
    # PRE: dtree is a valid decision tree, attr is a valid attribute; ca, pa, lapl defined
    # POST: returns traced classification estimate
    def est(dtree, attr):
        # calculate n, N, k
        n=dtree['classification#'][attr]
        N=0
        for _,v in dtree['classification#'].items():
            N+=v
        k=len(dtree['classification#'].keys())
        if lapl:
            if ca:
                e = (n+1)/(N+k)
                return e, "$=\\frac{n+1}{N+k}=\\frac{%d+1}{%d+%d}=%f$"%(n,N,k,e)
            else:
                e = 1-(n+1)/(N+k)
                return e, "$=1-\\frac{n+1}{N+k}=1-\\frac{%d+1}{%d+%d}=%f$"%(n,N,k,e)
        else:
            if ca:
                e = (n+pa[attr]*m)/(N+m)
                return e, "$=\\frac{n+p_a(%s)\\cdot m}{N+m}=\\frac{%d+%f\\cdot %f}{%d+%d}=%f$"%(attr,n,pa[attr],m,N,m,e)
            else:
                e = 1-(n+pa[attr]*m)/(N+m)
                return e, "$=1-\\frac{n+p_a(%s)\\cdot m}{N+m}=1-\\frac{%d+%f\\cdot %f}{%d+%d}=%f$"%(attr,n,pa[attr],m,N,m,e)
    # calculate static estimates on nodes/leafs
    # PRE: st valid decision tree
    # POST: st has traced static estimates per attribute and the "best" estimate
    def stat_est(st):
        frm=[]
        best=float('-inf') if ca else float('inf')
        st['static estimate#']=dict()
        i=1
        for k, _ in st['classification#'].items():
            st['static estimate#'][k],f=est(st,k)
            frm+=['p(%s$%s$%s$|$current node) ='%(attr,'='if ca else '\\neq ',k),f]
            i+=1
            best=better(best,st['static estimate#'][k])
        frm+=["Static estimate (%s): %f"%(better.__name__,best)]
        st['static estimate']=best
        return frm

    # implements traced MEP on preprocessed decision trees
    # PRE: dtree valid decision tree
    # POST: return MEP trace
    def mepsub(dtree):
        r = []
        # calculate partial MEP trace
        # PRE: st valid decision tree, r empty trace
        # POST: r MEP trace
        def ms(st):
            nonlocal r
            for sst in st['subtrees']:
                ms(sst)
            if st['subtrees']==[]:
                # leaf
                # calculate traced static estimates
                frm=stat_est(st)
                # on leafs classification estimate is the static one
                st['classification estimate']=st['static estimate']
                st['focus']='true'
                rst=copy.deepcopy(dtree)
                rst['formulas']=[frm]
                # record trace
                r+=[rst]
                st['focus']='false'
            else:
                # node
                # calculate traced static estimates
                stat_frm=stat_est(st)
                rev_est=0
                #frm='(Reverse estimate) $='
                frm=''
                # calculate traced reverse estimates
                cnum=0
                for _, v in st['classification#'].items():
                    cnum+=v
                for sst in st['subtrees']:
                    num=0
                    for _, v in sst['classification#'].items():
                        num+=v
                    if cnum!=0:
                        rev_est+=(num/cnum)*sst['static estimate']
                        frm+="\\frac{%d}{%d}\\cdot %f+"%(num,cnum,sst['static estimate'])
                    else:
                        rev_est+=0
                        frm+='0+'
                st['reverse estimate']=rev_est
                # calculate classification estimate
                st['classification estimate']=better(st['reverse estimate'],st['static estimate'])
                st['focus']='true'
                do_cut = rev_est <= st['static estimate'] if ca else rev_est >= st['static estimate']
                if do_cut:
                    for sst in st['subtrees']:
                        sst['cut']='true'
                rst=copy.deepcopy(dtree)
                # add formulas
                rst['formulas']=[stat_frm,['(Reverse estimate) $=$','$='+frm[:-1]+'=$',"= $%f$"%(rev_est)]]
                if do_cut:
                    rst['formulas']+=[["reverse estimate $%s$ static estimate"%('\\leq' if ca else '\\geq'),"CUT SUBTREES"]]
                else:
                    rst['formulas']+=[["reverse estimate $%s$ static estimate"%('>' if ca else '<'),"KEEP SUBTREES"]]
                # record trace
                r+=[rst]
                st['focus']='false'
                # prune if needed
                if do_cut:
                    st['subtrees']=[]
        ms(dtree)
        res = dict()
        # add meta-information
        dtree['formulas']=[]
        res['trace']=r+[dtree]
        res['method']='MEP'
        return res
    return mepsub(dtree)

def create_graph(tree, method, preprocessed=True):
    def trav_rep(dot, tree, ph='root'):
        atr = tree['attribute']
        #ph = str(hash(json.dumps(tree)))+'1'
        for st in tree['subtrees']:
            nattrs=''
            for key, value in st['classification#'].items():
                nattrs=nattrs+"|"+('['+str(key)+']'if key==st['classification']else str(key))+': '+str(value)
            label = "{"+str(st['classification'])+nattrs+"|"+str(st['attribute'])+"}"
            sh = str(hash(json.dumps(st)))+ph
            if st['focus']=='true':
                dot.node(sh,label,shape='record',color='blue')
            else:
                dot.node(sh,label, shape='record')
            if st['cut']=='true':
                dot.edge(ph,sh,label=st['arrow'],color='red',style='dashed',fontcolor='red')
            else:
                dot.edge(ph,sh,label=st['arrow'])
            trav_rep(dot, st,ph=sh)
        return dot
    if method=="REP":
        dot = gv.Digraph('decision-tree')
        dot.attr(margin='0,0')
        #ph = str(hash(json.dumps(tree)))+'1'
        ph = 'root'
        nattrs=''
        for key, value in tree['classification#'].items():
            nattrs=nattrs+"|"+str(key)+': '+str(value)
        label = "{"+str(tree['classification'])+nattrs+"|"+str(tree['attribute'])+"}"
        if tree['focus']=='true':
            dot.node(ph,label,shape='record',color='blue')
        else:
            dot.node(ph,label, shape='record')
    if method=="MEP":
        dot = gv.Digraph('decision-tree')
        dot.attr(margin='0,0')
        #ph = str(hash(json.dumps(tree)))
        ph = 'root'
        nattrs=''
        for key, value in tree['classification#'].items():
            nattrs=nattrs+"|"+str(key)+': '+str(value)
        label = "{"+str(tree['classification'])+nattrs+"|"+str(tree['attribute'])+"}"
        if tree['focus']=='true':
            dot.node(ph,label,shape='record',color='blue')
        else:
            dot.node(ph,label, shape='record')
    return trav_rep(dot,tree)

def render_trace(trace,font_size=13):
    trees, fms = [], []
    gr = create_graph(trace['original'],trace['method'])
    pathlib.Path('temp.gv').write_text(gr.source)
    trees+=[plt.imread(gv.render('dot',outfile='temp.png'))]
    fig = plt.figure()
    ax = fig.add_axes((0,0,1,1))
    ax.axis('off')
    #ax.annotate(str(trace['table']),xy=(0,0.1))
    tbl = copy.deepcopy(trace['table'])
    #tbl.insert(len(tbl.columns),'$p_a$',list(tbl[tbl.columns[-1]].apply(lambda x: pa[x])),True)
    tbl.insert(0,'',list(tbl.index),True)
    tbl = tbl.rename(lambda x: x+' - class' if x==trace['table'].columns[-1] else x, axis='columns')
    tbl.index.name=''
    tblp=pd.plotting.table(ax,tbl,loc='center',cellLoc='center',colColours=['gainsboro']*len(tbl))
    #,bbox=[0,0.1,winw*0.5/len(list(trace['table'].columns)),winh*10/len(trace['table'])])
    tblp.auto_set_font_size(False)
    tblp.set_fontsize(font_size*0.8)
    if args.mep:
        if not args.laplace:
            ax.annotate('$p_a$:',xy=(0,0.92),fontsize=font_size)
            for i,(k,v) in enumerate(pa.items()):
                ax.annotate(f'{k}: {v}',xy=(0.1,0.8+i*font_size/220),fontsize=font_size)
    fms+=[fig]
    for tree in trace['trace']:
        gr = create_graph(tree,trace['method'])
        pathlib.Path('temp.gv').write_text(gr.source)
        trees+=[plt.imread(gv.render('dot',outfile='temp.png'))]
        plt.rc('text',usetex=True)
        fig = plt.figure()
        ax = fig.add_axes((0,0,1,1))
        ax.axis('off')
        x, y = 0, 0.9
        for fm in tree['formulas']:
            for f in fm:
                ax.annotate(f,xy=(x,y),fontsize=font_size)
                y-=font_size/200
            y-=(font_size)/200
        fms+=[fig]
    return trees, fms

args = None
#def read_cut(    atree,     amep,    arep,    aattr,         atable,    alaplace,    asep,    aca,    aerr,    ano_preprocess):
#trace = read_cut(args.tree, args.mep,args.rep,args.attribute,args.table,args.laplace,args.sep,args.ca,args.err,args.no_preprocess)
def read_cut(use=None):
    global dtree,test,attr,args,pa
    # generate/import
    if args.tree is None:
        if use is None:
            dtree,test,args.attribute = gen_ex()
            attr = test.columns[-1]
            if not args.laplace:
                pa = dtree['pa']
                args.m = dtree['m']
        else:
            dtree,test,attr=use['original'],use['table'],use['attribute']
            if not args.laplace:
                pa = dtree['pa']
                args.m = dtree['m']
    else:
        attr = args.attribute
        if args.rep:
            dtree = json.load(args.table)
        if args.mep:
            jstree = json.load(args.table)
            dtree = jstree['tree']
            if not args.laplace:
                pa = jstree['pa']
                args.m = dtree['m']

    # REP input
    if not args.table:
        if args.rep and args.tree is not None:
            raise Exception('Trying to use REP without test file')
    else:
        if args.sep is None:
            test = pd.read_csv(args.table)
        else:
            test = pd.read_csv(args.table,sep=args.sep)

    if not args.laplace:
        m = 1 if args.m is None else float(args.m)
        dtree['m'] = m
    # cut tree
    if args.mep:
        ca = args.ca
        if args.err:
            ca = False
        if args.no_preprocess:
            orig = copy.deepcopy(dtree)
            trace = mep(dtree, attr, pa=pa,ca=ca, m=dtree['m'], lapl=args.laplace)
        else:
            dtree = preprocess(dtree, test, attr)
            orig = copy.deepcopy(dtree)
            trace = mep(dtree, attr, pa=pa,ca=ca, m=dtree['m'], lapl=args.laplace)
    if args.rep:
        if args.no_preprocess:
            orig = copy.deepcopy(dtree)
            trace = rep(dtree)
        else:
            dtree = preprocess(dtree, test, attr)
            orig = copy.deepcopy(dtree)
            trace = rep(dtree)
    #print(trace)
    trace['original'] = orig
    trace['table'] = test
    trace['attribute']=attr
    return trace

def save_json(filename, trace):
    t=copy.deepcopy(trace['table'])
    trace['table']=trace['table'].to_json()
    json.dump(trace,filename)
    trace['table']=t

def save_html(f, trace, trees, fms, render):
    dname = Path(f.name).stem
    os.mkdir(dname)
    f.write('<!DOCTYPE html>')
    f.write('<html>')
    f.write('<head></head>')
    f.write('<body>')
    f.write('<h1>Input</h1>')
    plt.clf()
    plt.imshow(trees[0])
    plt.axis('off')
    plt.savefig(f'{dname}/input_tree.png')
    f.write(f'<img src="{dname}/input_tree.png">')
    f.write(trace['table'].to_html())
    if trace['method']=='MEP':
        out_tbl = trace['original']['pa']
        f.write(pd.DataFrame(columns=out_tbl.keys(),
                             data=[out_tbl.values()],
                             index=['pa']).to_html())
        if not args.laplace:
            f.write(f'm = {trace["original"]["m"]}')
    f.write(f'<h1>Steps in {trace["method"]}</h1>')
    for i,(tree,fm) in enumerate(zip(trees[1:],fms[1:])):
        f.write(f'<h2>Step {i}</h2>')
        plt.clf()
        plt.imshow(tree)
        plt.axis('off')
        plt.savefig(f'{dname}/tree{i}.png')
        f.write(f'<img src="{dname}/tree{i}.png">')
        if i!=len(trees)-2:
            fm.savefig(f'{dname}/formula{i}.png')
            f.write(f'<img src="{dname}/formula{i}.png">')
    f.write('</body>')
    f.write('</html>')
    f.close()
    render()

# TODO: počasno
def gui(trace,trees,fms):
    matplotlib.use('Agg')
    # if last image
    last = False
    # current step
    cur_step = 0
    # root GUI element
    root = tk.Tk()
    window = ttk.Frame(root, relief=tk.RAISED)
    vis = ttk.Frame(window, relief=tk.RIDGE)
    winw,winh = 1000,535
    font_size = winh/100
    root.geometry(str(winw)+'x'+str(winh))
    def donothing(): return ""
    # resizing window
    def resize(*xs):#event):
        nonlocal winh, winw,cur_step
        #winh, winw = root.winfo_height(), root.winfo_width()
        #winh, winw = event.height, event.width
        #print(winh,winw)
        #window.rowconfigure(0,minsize=winh*0.9,weight=15)
        #window.rowconfigure(1,minsize=winh*0.1,weight=1)
        #vis.columnconfigure(0, minsize=winw*0.6, weight=1)
        #vis.columnconfigure(1, minsize=winw*0.4, weight=1)
        #root.grid_propagate()
        #window.grid_propagate()
        #vis.grid_propagate()
        #root.update()
        #root.update_idletasks()
        #window.update()
        #window.update_idletasks()
        #vis.update()
        #vis.update_idletasks()
        #plt.clf()
        #plt.axis('off')
        #canvas = FigureCanvasTkAgg(plt.gcf(), master=window)
        #canvas.draw_idle()
        #canvas_widget = canvas.get_tk_widget()
        #canvas_widget.grid(row=0, column=0, sticky="nsew")
        #window.grid_slaves(row=0,column=0)[0].destroy()
        #cur_step=len(fms)-1
        #render()
        #cur_step=0
        render()
    #root.bind('<Configure>',resize)
    # function used to show current step
    def render():
        nonlocal vis, last
        #resize()
        if cur_step==len(fms)-1:
            plt.clf()
            plt.imshow(trees[cur_step])
            plt.axis('off')
            canvas = FigureCanvasTkAgg(plt.gcf(), master=window)
            canvas.draw_idle()
            canvas_widget = canvas.get_tk_widget()
            last = True
            canvas_widget.grid(row=0, column=0, sticky="nsew")
            return
        if last:
            window.grid_slaves(row=0,column=0)[0].destroy()
            last = False
        # render and display it
        plt.clf()
        plt.imshow(trees[cur_step])
        plt.axis('off')
        canvas = FigureCanvasTkAgg(plt.gcf(), master=vis)
        canvas.draw_idle()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        # display formulas
        fig = fms[cur_step]
        formulas = FigureCanvasTkAgg(fig, master=vis)
        formulas.draw_idle()
        formulas_widget = formulas.get_tk_widget()
        formulas_widget.grid(row=0, column=1, sticky="nsew")
    root.title("Decision tree pruning visualizer")
    # menu
    menu = tk.Menu(root)
    mnu_file = tk.Menu(menu, tearoff=0)
    # settings button
    sett = tk.Toplevel()
    sett.grid_rowconfigure(5)
    sett.grid_columnconfigure(2)
    sett.geometry("370x160")
    settw = sett#ttk.Frame(sett, relief=tk.RAISED)
    def updmeth(event):
        if setmethv.get()=='REP':
            args.rep,args.mep=True,False
        else:
            args.rep,args.mep=False,True
        if not args.mep:
            setla.configure(state='disabled')
            setca.configure(state='disabled')
            setm.configure(state='disabled')
        else:
            setla.configure(state='enabled')
            setca.configure(state='enabled')
            setm.configure(state='normal')
    tk.Label(settw,text='Pruning method:').grid(row=0,column=0)
    setmethv = tk.StringVar()
    methops = ['REP','MEP']
    setmeth = ttk.OptionMenu(settw,setmethv,methops[0 if args.rep else 1],*methops,command=updmeth)
    setmeth.grid(row=0,column=1)
    tk.Label(settw,text='Metric:').grid(row=1,column=0)
    def updca(event):
        if setcav.get()==caops[0]:
            args.ca,args.err=True,False
        else:
            args.ca,args.err=False,True
    setcav = tk.StringVar()
    caops = ['Classification accuraccy','Classification error']
    setca = ttk.OptionMenu(settw,setcav,caops[0 if args.ca else 1],*caops,command=updca)
    if not args.mep:
        setca.configure(state='disabled')
    setca.grid(row=1,column=1)
    tk.Label(settw,text='Estimate used for MEP:').grid(row=2,column=0)
    def updla(event):
        args.laplace = setlav.get()==laops[0]
        if args.laplace:
            setm.configure(state='disabled')
        else:
            setm.configure(state='normal')
    setlav = tk.StringVar()
    laops = ['Laplace estimate','M-estimate']
    setla = ttk.OptionMenu(settw,setlav,laops[0 if args.laplace else 1],*laops,command=updla)
    if not args.mep:
        setla.configure(state='disabled')
    setla.grid(row=2,column=1)
    tk.Label(settw,text='Classification attribute:').grid(row=3,column=0)
    def updarg(a,b,c):
        args.attribute = setargv.get()
    setargv = tk.StringVar()
    setargv.set(args.attribute)
    setarg = tk.Entry(settw,textvariable=setargv)
    setargv.trace_add('write',updarg)
    setarg.grid(row=3,column=1)

    tk.Label(settw,text='m:').grid(row=4,column=0)
    def updm(a,b,c):
        args.m = setmv.get()
    setmv = tk.StringVar()
    setmv.set(args.m)
    setm = tk.Entry(settw,textvariable=setmv)
    setmv.trace_add('write',updm)
    setm.grid(row=4,column=1)

    def updtree():
        filename = tk.filedialog.askopenfile(filetypes=[('JSON','*.json')])
        if filename is None:
            return
        args.tree = filename.name
        filename.close()
    settree = tk.Button(settw,text='Select tree',command=updtree)
    settree.grid(row=5,column=0)
    def updtable():
        filename = tk.filedialog.askopenfile(filetypes=[('CSV','*.csv')])
        if filename is None:
            return
        args.tree = filename.name
        filename.close()
    settable = tk.Button(settw,text='Select table',command=updtable)
    settable.grid(row=5,column=1)
    def updgen():
        nonlocal trees,fms,cur_step,trace
        trace = read_cut()
        trees,fms = render_trace(trace)
        cur_step,last = 0,False
        btn_left['state'],btn_right['state']='disabled','enabled'
        setargv.set(args.attribute)
        plt.close('all')
        render()
    def onclose():
        nonlocal trees,fms,cur_step,trace
        trace = read_cut(trace)
        trees,fms = render_trace(trace)
        cur_step,last = 0,False
        btn_left['state'],btn_right['state']='disabled','enabled'
        plt.close('all')
        render()
        sett.withdraw()
    sett.withdraw()
    sett.protocol('WM_DELETE_WINDOW',onclose)
    menu.add_command(label="Settings",command=sett.deiconify)
    # export button
    def exp_win(*xs):
       filename = tk.filedialog.asksaveasfile(filetypes=[('HTML','*.html'),('JSON','*.json')])
       if filename is None:
           return
       if filename.name.endswith('.html'):
           save_html(filename,trace,trees,fms,render)
       else:
           if filename.name.endswith('.json'):
               save_json(filename,trace)
           else:
               raise ValueError('Invalid file name.')
    menu.add_command(label="Export", command=exp_win)
    root.bind('<Control-s>', exp_win)
    menu.add_command(label='Regenerate tree and table', command=updgen)
    # help button
    #menu.add_command(label="Help", command=donothing)
    root.config(menu=menu)
    # main part of the window
    root.grid_rowconfigure(0,weight=1)
    root.grid_columnconfigure(0,weight=1)
    window.grid(row=0, column=0, sticky="nsew")
    window.columnconfigure(0,weight=1)
    window.rowconfigure(0,minsize=winh*0.9,weight=15)
    window.rowconfigure(1,minsize=winh*0.1,weight=1)
    # part for visualisations
    vis.grid(row=0, column=0, sticky="nsew")
    vis.columnconfigure(0, minsize=winw*0.6, weight=1)
    vis.columnconfigure(1, minsize=winw*0.4, weight=1)
    # separator
    sep = ttk.Separator(vis, orient=tk.VERTICAL)
    sep.grid(column=0, row=0)
    form = ttk.Frame(vis, relief=tk.RIDGE)
    form.grid(row=0,column=0)
    form.columnconfigure(0,weight=1)
    # buttons
    btn_frame = ttk.Frame(window, relief=tk.RAISED)
    btn_frame.grid(row=1, column=0, sticky="nsew")
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)
    btn_frame.rowconfigure(0, minsize=50, weight=1)
    btn_left = ttk.Button(btn_frame, text='<--')
    def previous_step(*xs):
        nonlocal cur_step, trace
        if 0<cur_step<len(trees):
            cur_step-=1
            render()
        btn_left['state']='disabled' if cur_step==0 else 'enabled'
        btn_right['state']='disabled' if cur_step==len(trees)-1 else 'enabled'
        #print(cur_step)
    btn_left['command']=previous_step
    btn_left['state']='disabled'
    btn_right = ttk.Button(btn_frame, text='-->')
    def next_step(*xs):
        nonlocal cur_step, trace
        if 0<=cur_step<len(trees)-1:
            cur_step+=1
            render()
        btn_right['state']='disabled' if cur_step==len(trees)-1 else 'enabled'
        btn_left['state']='disabled' if cur_step==0 else 'enabled'
        #print(cur_step)
    btn_right['command']=next_step
    btn_right['state']='disabled' if cur_step==len(trace['trace'])-1 else 'enabled'
    btn_left.grid(row=0, column=0, sticky="nsew")
    btn_right.grid(row=0, column=1, sticky="nsew")
    # first step
    render()
    root.bind('<Left>',previous_step)
    root.bind('<Right>',next_step)
    root.protocol("WM_DELETE_WINDOW",sys.exit)
    resize()
    root.mainloop()

class FileTypeWithExtensionCheck(ap.FileType):
    def __init__(self, mode='r', valid_extensions=None, **kwargs):
        super().__init__(mode, **kwargs)
        self.valid_extensions = valid_extensions

    def __call__(self, string):
        if self.valid_extensions:
            if not string.endswith(self.valid_extensions):
                raise ap.ArgumentTypeError('Not a valid filename extension')
        return super().__call__(string)

if __name__ == "__main__":
    # define cmd arguments
    parser = ap.ArgumentParser(prog='dtreecut', description='A visualizer for learning REP, MEP methods for decision tree prunning.')
    parser.add_argument('--rep', help='use REP method', action='store_true')
    parser.add_argument('--mep', help='use MEP method by minimizing error', action='store_true')
    parser.add_argument('--cli', help='do not display the graphical user interface', action='store_true')
    parser.add_argument('--version', help='display version of this program', action='version', version='%(prog) 0.1')
    parser.add_argument('--tree', help='import tree from file', type=FileTypeWithExtensionCheck('r',valid_extensions=('.json')))
    parser.add_argument('--no-preprocess', help='do not preprocess the given tree', action='store_true')
    parser.add_argument('--table', help='import a table (test table for REP method or data table for MEP)', type=FileTypeWithExtensionCheck('r',valid_extensions=('.csv')))
    parser.add_argument('--sep', '--separator', help='set separator for reading csv files')
    parser.add_argument('-a', '--attribute', help='main classification attribute')
    parser.add_argument('-o', '--output', help='export the solving process to json, html', type=FileTypeWithExtensionCheck('w',valid_extensions=('.json','.html')))
    parser.add_argument('--ca', help='use MEP method by maximizing accuracy', action='store_true')
    parser.add_argument('--err', help='use MEP method by minimizing error', action='store_true')
    parser.add_argument('--laplace', help='when using the MEP method use laplace\'s probability estimation (otherwise use the m-estimate)', action='store_true')
    parser.add_argument('-m',help='set m-estimate values',type=int)

    # ocena verjetnosti
    #parser.add_arguments('--quiz')
    args = parser.parse_args()

    # catch other input errors
    #if ars.i!=: fail
    #laplace in rep
    # generate in tabela
    # no trace
    # attribute
    if not args.rep and not args.mep:
        args.rep = True
    if not args.ca and not args.err:
        args.ca = True

    trace = read_cut()

    if args.output is not None or not args.cli:
        trees,fms = render_trace(trace)
    # save to file if needed
    if args.output is not None:
        if args.output.name.endswith('.json'):
            save_json(args.output,trace)
        if args.output.name.endswith('.html'):
            save_html(args.output,trace,trees,fms,lambda x:x)

    # show GUI if needed
    if not args.cli:
        gui(trace,trees,fms)

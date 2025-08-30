from radboy.DB.db import *
from radboy.FB.FormBuilder import FormBuilder
from copy import deepcopy as copy
class OrderedAndRecieved(BASE,Template):
    '''
    select an order date by name and date , and at a later date 
    set the rx datetime
    '''
    __tablename__='OrderedAnsRxd'
    Name=Column(String,default=None)
    ForWhom=Column(String,default=None)
    Description=Column(String,default=None)
    oarid=Column(Integer,primary_key=True)
    dtoe=Column(DateTime,default=datetime.now())
    
    order_dt=Column(DateTime,default=datetime.now())
    rx_dt=Column(DateTime,default=datetime.today()+timedelta(days=1))
    comment=Column(String,default='')
    
    def __init__(self,*args,**kwargs):
        for k in kwargs:
            if k in [i.name for i in self.__table__.columns]:
                setattr(self,k,kwargs[k])
try:
    OrderedAndRecieved.metadata.create_all(ENGINE)
except Exception as e:
    OrderedAndRecieved.__table__.drop(ENGINE)
    OrderedAndRecieved.metadata.create_all(ENGINE) 
 
class OrderAndRxdUi():

    #where cmds are stored
    cmds={}
    #registered cmds
    registry=[]
    def filter(self,src_dict):
        filte=[]
        for k in src_dict:
            if src_dict[k] is not None:
                if isinstance(src_dict[k],str):
                    filte.append(getattr(OrderedAndRecieved,k).icontains(src_dict[k]))
                elif isinstance(src_dict[k],datetime):
                    if k == 'rx_dtoe':
                        pass
                    elif k == 'dtoe':
                        pass
                    elif k == 'order_dt':
                        pass
                else:
                    filte.append(getattr(OrderedAndRecieved,k)==src_dict[k])
        return and_(*filte)

    def OrderedAndRecieved_as(self,_exlcudes=[],as_=None):
        excludes=['oarid',]
        for i in _exlcudes:
            if i not in excludes:
                excludes.append(i)
        fields=None
        if as_ is None:
            fields={i.name:
            {
                'default':None,
                'type':str(i.type).lower()

            } for i in OrderedAndRecieved.__table__.columns if i.name not in excludes}
        elif as_ == "default":
            with Session(ENGINE) as session:
                tmp=OrderedAndRecieved()
                session.add(tmp)
                session.commit()
                fields={i.name:
                {
                    'default':getattr(tmp,i.name),
                    'type':str(i.type).lower()

                } for i in OrderedAndRecieved.__table__.columns if i.name not in excludes}
                session.delete(tmp)
                session.commit()
        else:
            raise Exception(f"Not a registered as_('{as_}')")
        if fields is not None:
            fd=FormBuilder(data=fields)
            return fd,fields

    def search(self,selector=False,menu=False):
        terms,z=self.OrderedAndRecieved_as(as_=None)
        terms=self.filter(terms)
        if terms is not None:
            with Session(ENGINE) as session:
                query=session.query(OrderedAndRecieved).filter(*terms)
                query=orderQuery(query,OrderedAndRecieved.dtoe)
                results=query.all()
                ct=len(results)
                plural=''
                if ct > 1:
                    plural="s"
                print(f"{ct} result{plural}!")
                if not selector:
                    for num,i in enumerate(results):
                        print(std_colorize(i,num,ct))

                if selector:
                    #for returning a list of OrderedAndRecieved
                    htext=[]
                    for num,i in enumerate(results):
                        print(std_colorize(i,num,ct))
                    pass
                if menu:
                    #for paged edit/delete of OrderedAndRecieved and returns None
                    htext=[]
                    for num,i in enumerate(results):
                        print(std_colorize(i,num,ct))
                    pass


    def __init__(self,*args,**kwargs):
        self.cmds[uuid1()]={
            'cmds':generate_cmds(startcmd=['add','a'],endCmd=['no lu']),
            'desc':'add OrderedAndRecieved without lookup',
            'exec':self.addRecordNoLookup
        }
        self.cmds[uuid1()]={
            'cmds':generate_cmds(startcmd=['oar','OrderedAndRecieved'],endCmd=['fb None']),
            'desc':'test generate OrderedAndRecieved without lookup and fields to be used as None',
            'exec':lambda self=self:print(self.OrderedAndRecieved_as(as_=None))
        }
        self.cmds[uuid1()]={
            'cmds':generate_cmds(startcmd=['oar','OrderedAndRecieved'],endCmd=['fb dflt']),
            'desc':'test generate OrderedAndRecieved without lookup and fields to be used as default',
            'exec':lambda self=self:print(self.OrderedAndRecieved_as(as_="default"))
        }
        self.cmds[uuid1()]={
            'cmds':generate_cmds(startcmd=['sch','s','search'],endCmd=['', ' ']),
            'desc':'search for OrderedAndRecieved',
            'exec':lambda self=self:self.search()
        }
        
        #add cmds above
        
        for x,cmd in enumerate(self.cmds):
            if str(x) not in self.cmds[cmd]['cmds']:
                self.cmds[cmd]['cmds'].append(str(x))
        htext=[]
        cmdCopy=self.cmds
        ct=len(cmdCopy)
        for xnum,cmd in enumerate(cmdCopy):
            for num,i in enumerate(cmdCopy[cmd]['cmds']):

                if i not in self.registry:
                    self.registry.append(i)
                elif i in self.registry:
                    self.cmds[cmd]['cmds'].pop(self.cmds[cmd]['cmds'].index(i))
            htext.append(std_colorize(f"{self.cmds[cmd]['cmds']} - {self.cmds[cmd]['desc']}",xnum,ct))
        htext=''.join(htext)

        while True:
            print(htext)
            doWhat=Control(func=FormBuilderMkText,ptext=f"{self.__class__.__name__}:Do What what",helpText=htext,data="string")
            if doWhat is None:
                return
            elif doWhat in ['d','']:
                continue
            for cmd in self.cmds:
                if doWhat.lower() in self.cmds[cmd]['cmds'] and callable(self.cmds[cmd]['exec']):
                    try:
                        self.cmds[cmd]['exec']()
                    except Exception as e:
                        print(e)
                    break
        
    def addRecordNoLookup(self):
        with Session(ENGINE) as session:
            t=OrderedAndRxd()
            session.add(t)
            session.commit()
            data={
            i.name:{
            'default':getattr(t,i.name),
            'type':str(i.type).lower()} for i in t.__table__.columns
            }
            fd=FormBuilder(data=data)
            if fd is None:
                session.delete(t)
                session.commit()
            else:
                for k in fd:
                    setattr(t,k,fd[k])
                session.commit()
            session.refresh(t)
        
            print(t)
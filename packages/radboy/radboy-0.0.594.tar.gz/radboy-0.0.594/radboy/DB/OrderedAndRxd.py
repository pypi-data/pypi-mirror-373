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
    def __init__(self,*args,**kwargs):
        self.cmds[uuid1()]={
            'cmds':generate_cmds(startcmd=['add','a'],endCmd=['no lu']),
            'desc':'add OrderedAndRecieved without lookup',
            'exe':self.addRecordNoLookup
        }
        
        #add cmds above
        
        for x,cmd in enumerate(self.cmds):
            if str(x) not in self.cmds[cmd]['cmds']:
                self.cmds[cmd]['cmds'].append(x)
        htext=[]
        cmdCopy=self.cmds
        ct=len(cmdCopy)
        for cmd in cmdCopy:
            for num,i in enumerate(cmdCopy[cmd]['cmds']):

                if i not in self.registry:
                    self.registry.append(i)
                elif i in self.registry:
                    self.cmds[cmd]['cmds'].pop(self.cmds[cmd]['cmds'].index(i))
            htext.append(std_colorize(f"{self.cmds[cmd]['cmds']} - {self.cmds[cmd]['desc']}",num,ct))
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
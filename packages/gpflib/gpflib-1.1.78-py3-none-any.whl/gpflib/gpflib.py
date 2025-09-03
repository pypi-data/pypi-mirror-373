import json
from ctypes import *
import platform
import os
import re
import struct
import requests
import threading
from wordcloud import WordCloud
import chardet

def detect_file_encoding(file_path, sample_size=1024*1024):
    with open(file_path, 'rb') as f:
        raw = f.read(4)  # 读取前4个字节检测BOM
    
    # UTF-8 with BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    # UTF-16, big-endian
    elif raw.startswith(b'\xfe\xff'):
        return 'utf-16-be'
    # UTF-16, little-endian
    elif raw.startswith(b'\xff\xfe'):
        return 'utf-16-le'
    # UTF-32, big-endian
    elif raw.startswith(b'\x00\x00\xfe\xff'):
        return 'utf-32-be'
    # UTF-32, little-endian
    elif raw.startswith(b'\xff\xfe\x00\x00'):
        return 'utf-32-le'
    
    # 如果没有BOM标记，使用chardet检测
    with open(file_path, 'rb') as f:
        raw_sample = f.read(sample_size)
    
    result = chardet.detect(raw_sample)
    confidence = result['confidence']
    encoding = result['encoding']
    
    # 处理chardet可能的误判
    if encoding is None:
        return 'ascii'  # 默认为ASCII
    elif encoding.lower() == 'gb2312':
        return 'gbk'  # GBK是GB2312的超集
    else:
        return encoding

OS = platform.system()
if OS == "Windows":
    import win32api


IsCRFInit =0
IsPOSInit =0
IsBCCInit =0
IsGPFInit =0
lock = threading.Lock()


class GPF:
    def __init__(self, dataPath="./data"):
        dataPath=dataPath.replace("\\","/")
        if dataPath[len(dataPath)-1]=="/":
            dataPath=dataPath[0:len(dataPath)-1]
        if dataPath.find("./") != 0:
            dataPath="./"+dataPath

        if dataPath.find(".") != 0:
            dataPath="."+dataPath

        dll_name_gpf = ''
        dll_name_bcc = ''
        self.g_IdxLog="IdxLog.txt"
        self.hHandleGPF=0
        self.hHandleCRFPOS=0
        self.DotServiceURL=""
        if OS == "Windows":
            dll_name_gpf = 'gpflib.dll'
            dll_name_bcc = 'bcclib.dll'
        else:
            dll_name_gpf = 'libgpflib.so'
            dll_name_bcc = 'libbcclib.so'

        self.buf_max_size = 2048*1024*10
        self.CRFModel="Segment.dat"
        self.CRFTag=""
        self.POSData="idxPOS.dat"

        dll_file_gpf = os.path.join(os.path.dirname(os.path.abspath(__file__)), dll_name_gpf)
        dll_file_bcc = os.path.join(os.path.dirname(os.path.abspath(__file__)), dll_name_bcc)
        cfg_file_gpf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GPFconfig.txt')
        cfg_file_bcc = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BCCconfig.txt')
        cfg_file_parser= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Parser.lua')
        cfg_file_CRFModel= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Segment.dat')
        cfg_file_POSData=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'idxPOS.dat')

        self.library_gpf = cdll.LoadLibrary(dll_file_gpf)
        self.library_bcc = cdll.LoadLibrary(dll_file_bcc)

        self.ParserBCC=cfg_file_parser
        self.ConfigGPF= cfg_file_gpf
        self.ConfigBCC= cfg_file_bcc
        self.dataPath= dataPath
        self.buf_max_size = 1024*10000
        self.CRFModel=cfg_file_CRFModel
        self.POSData=cfg_file_POSData
        self.CRFTag=""
        self.RetBuff =create_string_buffer(''.encode(), self.buf_max_size)

        self.library_gpf.GPF_LatticeInit.argtypes = []
        self.library_gpf.GPF_LatticeInit.restype  = c_void_p  
        self.hHandleGPF=self.library_gpf.GPF_LatticeInit();

        self.library_gpf.GPF_CRFPOSInit.argtypes = []
        self.library_gpf.GPF_CRFPOSInit.restype  = c_void_p
        self.hHandleCRFPOS =self.library_gpf.GPF_CRFPOSInit()

        # https://stackoom.com/question/1VWM
        if OS == "Windows":
            self.dll_close = win32api.FreeLibrary
            cfg_file_DOTExe=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Graph/dot.exe')
        elif OS == "Linux":
            try:
                stdlib = CDLL("")
            except OSError:
                stdlib = CDLL("libc.so")
            self.dll_close = stdlib.dlclose
            self.dll_close.argtypes = [c_void_p]
            cfg_file_DOTExe=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Graph/dot')
        self.DotExe=cfg_file_DOTExe
        self.InitGPF(dataPath)

    def __del__(self):
        return  
        self.dll_close(self.library_gpf._handle)
        self.dll_close(self.library_bcc._handle)
        self.library_gpf.GPF_POSExit();
        self.library_bcc.BCC_Exit();
        self.library_gpf.GPF_CRFExit()
        self.library_gpf.GPF_Term(c_void_p(self.hHandleGPF))
        self.library_gpf.GPF_CRFPOSExit(c_void_p(self.hHandleCRFPOS))


    def SetGridText(self, text):
        self.GPFInit()
        return self.SetText(text)
    
    def SetText(self, text):
        self.library_gpf.GPF_SetText.argtypes = [c_void_p, c_char_p]
        self.library_gpf.GPF_SetText.restype  = c_int
        ret = self.library_gpf.GPF_SetText(self.hHandleGPF, text.encode())
        return ret


    def AddGridJS(self, json_str):
        self.GPFInit()
        Struct=json.loads(json_str)
        if isinstance(Struct,dict) and Struct.get("Type"):
            self.library_gpf.GPF_AddStructure.argtypes = [c_void_p, c_char_p]
            self.library_gpf.GPF_AddStructure.restype  = c_int
            ret = self.library_gpf.GPF_AddStructure(self.hHandleGPF, json_str.encode())
            return ret
        Type=self.GetShowStructType(json_str)
        if Type == "Graph":
            self.AddGraph(json_str)
        elif  Type == "Seq":
            self.AddSeq(json_str)
        elif  Type == "Tree":
            DotInfo=self.AddTree(json_str)

    def AddGrid(self, json_str):
        self.AddGridJS(json_str)

    def AddStructure(self, json_str):
        self.AddGridJS(json_str)

    def CallService(self, sentence, name):
        self.GPFInit()
        self.library_gpf.GPF_CallService.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_CallService.restype  = c_int
        str_len = self.library_gpf.GPF_CallService(self.hHandleGPF, name.encode(), sentence.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def Dot2Img(self, Dot, name):
        self.GPFInit()
        self.library_gpf.GPF_CallDot.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_CallDot.restype  = c_int
        str_len = self.library_gpf.GPF_CallDot(self.hHandleGPF, name.encode(), Dot.encode(), self.RetBuff, self.buf_max_size)
        return string_at(self.RetBuff, str_len)
    
    def DotFile(self, dot_filename, img_filename): 
        self.GPFInit()
        self.library_gpf.GPF_GetServiceURL.argtypes = [c_char_p, c_char_p]
        self.library_gpf.GPF_GetServiceURL.restype  = c_int  
        strlen=self.library_gpf.GPF_GetServiceURL('Dot'.encode(),self.RetBuff)
        self.DotServiceURL=string_at(self.RetBuff,strlen).decode()
        f = open(dot_filename,encoding="utf-8")
        dot_data = ''
        for each in f:
            dot_data += each
        f.close()
        query_json = {'data': dot_data}
        print(query_json)
        r = requests.post(self.DotServiceURL, data=json.dumps(query_json))
        if r.status_code == 200:
            f = open(img_filename, 'wb')
            f.write(r.content)
            f.close()
            return True
    
        return False

    def DotBuff(self, dot_data, img_filename): 
        self.GPFInit()
        self.library_gpf.GPF_GetServiceURL.argtypes = [c_char_p, c_char_p]
        self.library_gpf.GPF_GetServiceURL.restype  = c_int  
        strlen=self.library_gpf.GPF_GetServiceURL('Dot'.encode(),self.RetBuff)
        self.DotServiceURL=string_at(self.RetBuff,strlen).decode()

        query_json = {'data': dot_data}
        r = requests.post(self.DotServiceURL, data=json.dumps(query_json))
        if r.status_code == 200:
            f = open(img_filename, 'wb')
            f.write(r.content)
            f.close()
            return True
    
        return False


    def SetTable(self, tableName):
        self.GPFInit()                
        self.library_gpf.GPF_SetLexicon.argtypes = [c_void_p, c_char_p]
        self.library_gpf.GPF_SetLexicon.restype  = c_int
        ret = self.library_gpf.GPF_SetLexicon(self.hHandleGPF, tableName.encode())
        return ret

    def CallTable(self, tableName,Mode=0):
        self.GPFInit()
        self.library_gpf.GPF_AppLexicon.argtypes = [c_void_p, c_char_p]
        self.library_gpf.GPF_AppLexicon.restype  = c_int
        self.library_gpf.GPF_AppLexicon(self.hHandleGPF, tableName.encode())
        self.library_gpf.GPF_SetLexicon.argtypes = [c_void_p, c_char_p]
        self.library_gpf.GPF_SetLexicon.restype  = c_int
        ret = self.library_gpf.GPF_SetLexicon(self.hHandleGPF, tableName.encode())
        return ret

    def GetSuffix(self, tableName, sentence):
        self.GPFInit()        
        self.library_gpf.GPF_GetSuffix.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetSuffix.restype  = c_int
        str_len = self.library_gpf.GPF_GetSuffix(self.hHandleGPF, tableName.encode(), sentence.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()
    
    def GetPrefix(self, tableName, sentence):
        self.GPFInit()                
        self.library_gpf.GPF_GetPrefix.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetPrefix.restype  = c_int
        str_len = self.library_gpf.GPF_GetPrefix(self.hHandleGPF, tableName.encode(), sentence.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def GetWord(self, UnitNo):
        
        self.library_gpf.GPF_GetWord.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetWord.restype  = c_int
        str_len = self.library_gpf.GPF_GetWord(self.hHandleGPF, UnitNo.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def RunFSA(self, fsaName, param=""):
        return self.CallFSA(fsaName, param)

    def CallFSA(self, fsaName, **Others):
        Param=""
        for K,V in Others.items():
            if len(Param) != 0:
                Param=Param+";"+K+"="+V
            else:
                Param=K+"="+V
        self.GPFInit()                
        self.library_gpf.GPF_RunFSA.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_RunFSA.restype  = c_int

        self.library_gpf.GPF_SetFSAPath.argtypes = [c_void_p, c_char_p, c_int]
        self.library_gpf.GPF_SetFSAPath.restype  = c_int

        len = self.library_gpf.GPF_RunFSA(self.hHandleGPF, fsaName.encode(), Param.encode(),self.RetBuff,self.buf_max_size)

        TotalNum=struct.unpack("i",self.RetBuff[0:4])
        offset=4
        for i in range(TotalNum[0]):
            OperationLen=struct.unpack("i",self.RetBuff[offset:offset+4])
            offset+=4
            code=self.RetBuff[offset:offset+OperationLen[0]]
            offset+=OperationLen[0]
            MatchPathLen=struct.unpack("i",self.RetBuff[offset:offset+4])
            offset+=4
            self.library_gpf.GPF_SetFSAPath(self.hHandleGPF, self.RetBuff[offset:offset+MatchPathLen[0]],MatchPathLen[0])
            offset+=MatchPathLen[0]
            exec(code.decode())

        return len

    def GetParam(self, key):
        return self.GetFSAParam(key)

    def GetFSAParam(self, key):
        
        self.library_gpf.GPF_GetParam.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetParam.restype  = c_int
        str_len = self.library_gpf.GPF_GetParam(self.hHandleGPF, key.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()
    
    def GetStructure(self):
        return self.GetGrid()

    def GetGrid(self):
        
        self.library_gpf.GPF_GetGrid.argtypes = [c_void_p, c_char_p, c_int]
        self.library_gpf.GPF_GetGrid.restype  = c_int
        str_len = self.library_gpf.GPF_GetGrid(self.hHandleGPF, self.RetBuff, self.buf_max_size)
        if str_len != 0:
            str_ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(str_ret.decode())
            return json_data
        return json.loads("{}")

    def GetGridText(self, begin=0, end=-1):
        return self.GetText(begin, end)

    def GetText(self, begin=0, end=-1):
        self.library_gpf.GPF_GetTextByRange.argtypes = [c_void_p, c_int, c_int, c_char_p, c_int]
        self.library_gpf.GPF_GetTextByRange.restype  = c_int
        str_len = self.library_gpf.GPF_GetTextByRange(self.hHandleGPF, begin, end, self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def GetTextKV(self, key=""):
        return self.GetGridKVs(key)

    def GetGridKV(self, key=""):
        return self.GetGridKVs(key)

    def GetGridKVs(self, key=""):
        self.library_gpf.GPF_GetGridKVs.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetGridKVs.restype  = c_int
        str_len = self.library_gpf.GPF_GetGridKVs(self.hHandleGPF, key.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("{}")

    
    def GetFSAUnit(self, pathNo):
        self.library_gpf.GPF_GetUnitByInt.argtypes = [c_void_p, c_int, c_char_p, c_int]
        self.library_gpf.GPF_GetUnitByInt.restype  = c_int
        str_len = self.library_gpf.GPF_GetUnitByInt(self.hHandleGPF, pathNo, self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def GetUnit(self, kv,UnitNo="",UExpress=""):
        if isinstance(kv,int):
            return self.GetFSAUnit(kv)
        return self.GetUnits(kv,UnitNo,UExpress)

    def GetUnits(self, kv,UnitNo="",UExpress=""):
        self.library_gpf.GPF_GetUnitsByKV.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetUnitsByKV.restype  = c_int

        self.library_gpf.GPF_GetUnitsByNo.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetUnitsByNo.restype  = c_int

        if UnitNo == "":
            str_len = self.library_gpf.GPF_GetUnitsByKV(self.hHandleGPF, kv.encode(), self.RetBuff, self.buf_max_size)
        else:
            str_len = self.library_gpf.GPF_GetUnitsByNo(self.hHandleGPF, UnitNo.encode(),UExpress.encode(),kv.encode(), self.RetBuff, self.buf_max_size)

        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return 0
   
    def GetUnitKV(self, unitNo, key=""):
        return self.GetUnitKVs(unitNo, key)

    def GetUnitKVs(self, unitNo, key=""):
        self.library_gpf.GPF_GetUnitKVs.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetUnitKVs.restype  = c_int
        str_len = self.library_gpf.GPF_GetUnitKVs(self.hHandleGPF, unitNo.encode(), key.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            if key == "Word" or key == "HeadWord":
                return  json_data[0]

            if key == "From" or key == "To":
                return  int(json_data[0])

            return json_data
        if key == "Word" or key == "HeadWord":
            return  ""

        if key == "From" or key == "To":
            return  -1
        return json.loads("{}")

    def GetRelation(self, kv=""):
        return self.GetRelations(kv)

    def GetRelations(self, kv=""):
        self.library_gpf.GPF_GetRelations.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetRelations.restype  = c_int
        str_len = self.library_gpf.GPF_GetRelations(self.hHandleGPF, kv.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("[]")

    def GetRelationKV(self, unitNo1, unitNo2, role, key=""):
        return self.GetRelationKVs( unitNo1, unitNo2, role, key)

    def GetRelationKVs(self, unitNo1, unitNo2, role, key=""):
        self.library_gpf.GPF_GetRelationKVs.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetRelationKVs.restype  = c_int
        str_len = self.library_gpf.GPF_GetRelationKVs(self.hHandleGPF, unitNo1.encode(), unitNo2.encode(), role.encode(), key.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("{}")

    def GetItem(self, tableName="", kv=""):
        return self.GetTableItem(tableName, kv)

    def GetTableItem(self, tableName="", kv=""):
        self.GPFInit()              
        if tableName=="":
            return self.GetTable()
        return self.GetTableItems(tableName, kv)

    def GetTableItems(self, tableName, kv=""):
        self.GPFInit()                
        self.library_gpf.GPF_GetTableItems.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetTableItems.restype  = c_int
        str_len = self.library_gpf.GPF_GetTableItems(self.hHandleGPF, tableName.encode(), kv.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("{}")
    
    def GetItemKV(self, tableName, item="", key=""):
        return self.GetTableItemKV(tableName, item, key)

    def GetTableItemKV(self, tableName, item="", key=""):
        self.GPFInit()                
        return self.GetTableItemKVs(tableName, item, key)

    def GetTableItemKVs(self, tableName, item="", key=""):
        self.GPFInit()                
        self.library_gpf.GPF_GetTableItemKVs.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetTableItemKVs.restype  = c_int
        str_len = self.library_gpf.GPF_GetTableItemKVs(self.hHandleGPF, tableName.encode(), item.encode(), key.encode(), self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("{}")

    def GetFSANode(self, tag="-1"):
        self.library_gpf.GPF_GetFSANodeByTag.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_GetFSANodeByTag.restype  = c_int
        PathNo = self.library_gpf.GPF_GetFSANodeByTag(self.hHandleGPF, tag.encode(), self.RetBuff, self.buf_max_size)
        return PathNo

    def GetNode(self, tag):
        if isinstance(tag,int):
            return self.GetFSANode(str(tag))
        return self.GetFSANode(tag)

    def AddUnit(self,text, colNo=-1):
        self.library_gpf.GPF_AddUnit.argtypes = [c_void_p, c_int, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_AddUnit.restype  = c_int
        if colNo == -1:
            colNo=self.GetText().find(text)+len(text)-1
            if colNo == -1:
                colNo=0

        str_len = self.library_gpf.GPF_AddUnit(self.hHandleGPF, colNo, text.encode(), self.RetBuff, self.buf_max_size)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def AddUnitKV(self, unitNo, key,val):
        self.library_gpf.GPF_AddUnitKV.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        self.library_gpf.GPF_AddUnitKV.restype  = c_int
        Values=re.split(r"[ ;,\t]",val)
        for Value in Values:
            self.library_gpf.GPF_AddUnitKV(self.hHandleGPF, unitNo.encode(), key.encode(), Value.encode())
        return 1

    def AddTextKV(self, key,val):
        return self.AddGridKV(key,val)

    def AddGridKV(self, key,val):
        self.library_gpf.GPF_AddGridKV.argtypes = [c_void_p, c_char_p, c_char_p]
        self.library_gpf.GPF_AddGridKV.restype  = c_int
        Values=re.split(r"[ ;,\t]",val)
        for Value in Values:
            self.library_gpf.GPF_AddGridKV(self.hHandleGPF, key.encode(),Value.encode())
        return 0
    
    def AddRelation(self, unitNo1, unitNo2, role):
        self.library_gpf.GPF_AddRelation.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        self.library_gpf.GPF_AddRelation.restype  = c_int
        self.library_gpf.GPF_AddRelation(self.hHandleGPF, unitNo1.encode(), unitNo2.encode(), role.encode())
        return 1

    def AddRelationKV(self, unitNo1, unitNo2, role, key, val):
        self.library_gpf.GPF_AddRelationKV.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_AddRelationKV.restype  = c_int
        Values=re.split(r"[ ;,\t]",val)
        for Value in Values:
            self.library_gpf.GPF_AddRelationKV(self.hHandleGPF, unitNo1.encode(), unitNo2.encode(), role.encode(), key.encode(), Value.encode(), self.RetBuff, self.buf_max_size)
        return 1

    def IsUnit(self, unitNo, kv):
        self.library_gpf.GPF_IsUnit.argtypes = [c_void_p, c_char_p, c_char_p]
        self.library_gpf.GPF_IsUnit.restype  = c_int
        ret = self.library_gpf.GPF_IsUnit(self.hHandleGPF, unitNo.encode(), kv.encode())
        return ret

    def IsRelation(self, unitNo1, unitNo2, role, kv=""):
        self.library_gpf.GPF_IsRelation.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.library_gpf.GPF_IsRelation.restype  = c_int
        ret = self.library_gpf.GPF_IsRelation(self.hHandleGPF, unitNo1.encode(), unitNo2.encode(), role.encode(), kv.encode())
        return ret

    def IsTable(self, tableName, item="", kv=""):
        self.library_gpf.GPF_IsTable.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        self.library_gpf.GPF_IsTable.restype  = c_int
        ret = self.library_gpf.GPF_IsTable(self.hHandleGPF, tableName.encode(), item.encode(), kv.encode())
        return ret

   
    def IndexFSA(self, rule_filename):
        self.library_gpf.GPF_MakeRule.argtypes = [c_char_p]
        self.library_gpf.GPF_MakeRule.restype  = c_int
        rule_filename=rule_filename.replace("\\","/")
        ret = self.library_gpf.GPF_MakeRule(rule_filename.encode())
        self.library_gpf.GPF_ReLoad.argtypes = [c_char_p]
        self.library_gpf.GPF_ReLoad.restype  = c_int
        self.library_gpf.GPF_ReLoad(self.ConfigGPF.encode())
        return ret
    
    def Write2File(self, json_data,Idx2):
        RetInf=0
        Out=open(Idx2,"w",encoding="utf8")
        for Table in json_data:
            Items=self.GetTableItems(Table)
            for Item in Items:
                Colls=self.GetTableItemKVs(Table,Item,"Coll")
                for Coll in Colls:
                    CollItems=self.GetTableItemKVs(Table,Item,Coll)
                    if len(CollItems)>0:
                        self.WriteColl2File(Item,Coll,CollItems,Out)
                        RetInf=1
        Out.close()
        return RetInf

    def WriteColl2File(self, Item,Coll,CollItems,Out):
        Line="Table "+Coll+"_"+Item
        print(Line,file=Out)
        for Item in CollItems:
            print(Item,file=Out)
        
    def IndexTable(self, table_filename):
        self.GPFInit()
        self.library_gpf.GPF_MakeTable.argtypes = [c_char_p, c_char_p, c_int]
        self.library_gpf.GPF_MakeTable.restype  = c_int
        str_len = self.library_gpf.GPF_MakeTable(table_filename.encode(),self.RetBuff,self.buf_max_size)
        self.library_gpf.GPF_ReLoad.argtypes = [c_char_p]
        self.library_gpf.GPF_ReLoad.restype  = c_int
        self.library_gpf.GPF_ReLoad(self.ConfigGPF.encode())
        if str_len != 0 :
            str_ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(str_ret.decode())
            Idx2=os.path.dirname(table_filename)+"/Coll_"+os.path.basename(table_filename)
            if self.Write2File(json_data,Idx2):
                self.IndexTable(Idx2)
            os.remove(Idx2)
            self.library_gpf.GPF_ReLoad.argtypes = [c_char_p]
            self.library_gpf.GPF_ReLoad.restype  = c_int
            self.library_gpf.GPF_ReLoad(self.ConfigGPF.encode())
            return json_data
        return 0

    def GetLog(self):
        
        self.library_gpf.GPF_GetLog.argtypes = [c_void_p, c_char_p, c_int]
        self.library_gpf.GPF_GetLog.restype  = c_int
        str_len=self.library_gpf.GPF_GetLog(self.hHandleGPF,self.RetBuff,self.buf_max_size)
        if str_len != 0:
            str_ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(str_ret.decode())
            return json_data
        return json.loads("{}")

    def Reduce(self,From=0,To=-1,Head=-1):
        
        self.library_gpf.GPF_Reduce.argtypes = [c_void_p, c_int,c_int,c_char_p, c_int]
        self.library_gpf.GPF_Reduce.restype  = c_int
        str_len=self.library_gpf.GPF_Reduce(self.hHandleGPF,From,To,self.RetBuff,self.buf_max_size)
        HeadUnit=self.GetUnit(Head)
        self.library_gpf.GPF_SetHead.argtypes = [c_void_p, c_char_p, c_char_p]
        self.library_gpf.GPF_SetHead.restype  = c_int
        self.library_gpf.GPF_SetHead(self.hHandleGPF,self.RetBuff,HeadUnit)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()
    def IsFileList(self,filelistname):
        In=open(filelistname,"r")
        IsFile=True
        IsPossible=True
        for Line in In:
            if not os.path.isfile(Line.strip()):
                IsFile=False
            if Line.find("\\") == -1 and Line.find("/") ==-1:
                IsPossible=False
        In.close()
        if IsFile or IsPossible:
            return True
        return False

    def IsRaw(self,File):
        encoding = detect_file_encoding(File)
        In=open(File,"r",encoding=encoding)
        No=0
        Lines=[]
        try:
            for Line in In:
                Lines.append(Line.strip())
                No+=1
                if No >10:
                    break
        except:
            print("",end="")
        In.close()
        if len(Lines) < 1:
            return False
        return self.CheckLines(Lines)

    def CheckLines(self,Lines):
        if Lines[0].find("Table ") == 0 or  Lines[0].find("Doc ") == 0:
            return False
        AllWords=[]
        for i in range(0,len(Lines)):
            Words=Lines[i].split(" ")
            for j in range(len(Words)):
                AllWords.append(Words[j])
        return self.CheckWords(AllWords)
    
    def CheckWords(self,AllWords):
        if len(AllWords) == 0:
            return False
        Num1=0
        Num2=0
        Num3=0
        Len=0
        for Word in AllWords:
            if Word.find("/") != -1:
               Num1+=1
            if Word.find("(") != -1 or Word.find(")") != -1:
               Num2+=1
            Len+=len(Word)
        AvgLen=int(Len/len(AllWords))
        if Num1 == len(AllWords):
            return False

        if AvgLen <= 4:
            return False

        if Num2>0 and Num2 > int(len(AllWords)*0.8):
            return False
        return True
        
    def ProcessFile(self,File,FileTmp,Cmd):
        print("Processing {}".format(File))
        encoding = detect_file_encoding(File)
        In=open(File,"r",encoding=encoding)
        Out=open(FileTmp,"w")
        print("Doc {}".format(File),file=Out)
        Ret=""
        for Line in In:
            Line=Line.strip()
            Sent=Line.split("。")
            for s in  Sent:
                s=s[0:512]
                Ret=self.Parse(s,Structure="POS")
                Ret=json.loads(Ret)
                print("Item:"+" ".join(Ret),file=Out)
        In.close()
        Out.close()
        
    def File2Corpus(self,filelist,filelistEx,Cmd):
        encoding = detect_file_encoding(filelist)
        InList=open(filelist,"r",encoding=encoding)
        OutList=open(filelistEx,"w")
        No=0
        FileTmp=""
        for File in InList:
            File=File.strip()
            if self.IsRaw(File):
                FileTmp=os.path.join(self.dataPath,os.path.basename(File))
                self.ProcessFile(File,"{}{}".format(FileTmp,No),Cmd)
                print("{}{}".format(FileTmp,No),file=OutList)
                No+=1
            else:
                print(File,file=OutList)
        OutList.close()
        InList.close()

    def Corpus(self,PathIn,filelistNames):
        for File in os.listdir(PathIn):
            AbsFile = os.path.join(PathIn, File)
            if os.path.isdir(AbsFile):
                self.Corpus(AbsFile,filelistNames)
            else:
                filelistNames.append(AbsFile)
    #Other
    #Structure="HZ/Segment/POS/Tree"
    def IndexBCC(self,filelistname,**Others):
        ret=0
        if not os.path.exists(self.dataPath):
            os.mkdir(os.path.abspath(self.dataPath))
        Param=[]
        self.GetIndexBCCInfo(Others,Param)
        self.library_bcc.BCC_IndexBCC.argtypes = [c_char_p, c_char_p, c_char_p]
        self.library_bcc.BCC_IndexBCC.restype  = c_int
        filelist=os.path.join(self.dataPath,"indexlist.tmp")
        if isinstance(filelistname,str):
            if os.path.isdir(filelistname):
                filelistNames=[]
                self.Corpus(filelistname,filelistNames)
                Out=open(filelist,"w")
                for File in filelistNames:
                    print(File,file=Out) 
                Out.close()
            else:
                if self.IsFileList(filelistname):
                    filelist=filelistname
                else:
                    Out=open(filelist,"w")
                    print(filelistname,file=Out) 
                    Out.close()
        else:
            Out=open(filelist,"w")
            for File in filelistname:
                print(File,file=Out)    
            Out.close()
        filelistEx=os.path.join(self.dataPath,"indexlistEx.tmp")
        self.File2Corpus(filelist,filelistEx,Param[0])
        ret = self.library_bcc.BCC_IndexBCC(self.ConfigBCC.encode(),filelistEx.encode('gbk', errors='strict'),self.dataPath.encode('gbk', errors='strict'))
        os.remove(filelistEx)
        if filelist.find("indexlist.tmp") != -1:
            os.remove(filelist)
        
        return ret

    def CallBCC(self, query,Service=""):
        global IsBCCInit
        if Service != "":
            return self.CallService(query,Service)
        lock.acquire()
        if IsBCCInit == 0:
            self.library_bcc.BCC_Init.argtypes = [c_char_p]
            self.library_bcc.BCC_Init.restype  = c_int 
            IsBCCInit=self.library_bcc.BCC_Init(self.dataPath.encode('gbk', errors='strict'))
        lock.release()

        if IsBCCInit == 0 and query.find("Lua") == -1:
            return json.loads("{}")
        self.library_bcc.BCC_RunBCC.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.library_bcc.BCC_RunBCC.restype  = c_int
        str_len = self.library_bcc.BCC_RunBCC(self.ParserBCC.encode(),self.dataPath.encode('gbk', errors='strict'),query.encode(),self.RetBuff)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()

    def AddBCCKV(self, Key,Val,Server=""):
        Values=re.split(r"[ ;,\t]",Val)
        Val=";".join(Values)
        Query="AddKV({},{})".format(Key,Val)
        return self.CallBCC(Query,Server)

    def GetBCCKV(self, Key="",Server=""):
        if Key=="":
            Query="GetKV()"
        else:
            Query="GetKV({})".format(Key)
        return self.CallBCC(Query,Server)

    def GetBCCKVs(self, Key="",Server=""):
        if Key=="":
            Query="GetKV()"
        else:
            Query="GetKV({})".format(Key)
        return self.CallBCC(Query,Server)

    def ClearBCCKV(self, Key="",Server=""):
        Query="ClearKV()"
        return self.CallBCC(Query,Server)

    def Segment(self,text,table=""):
        global IsCRFInit
        lock.acquire()
        if IsCRFInit ==0:
            self.library_gpf.GPF_CRFInit.argtypes = [c_char_p,c_char_p]
            self.library_gpf.GPF_CRFInit.restype  = c_int
            IsCRFInit = self.library_gpf.GPF_CRFInit(self.CRFModel.encode(),self.CRFTag.encode())
        lock.release()
        if IsCRFInit == 0:
            return ""                
        ret=""
        if table == "":
            self.library_gpf.GPF_Seg.argtypes = [c_void_p, c_char_p, c_char_p]
            self.library_gpf.GPF_Seg.restype  = c_int
            str_len=self.library_gpf.GPF_Seg(self.hHandleCRFPOS,text.encode(),self.RetBuff,1)
            ret = string_at(self.RetBuff, str_len)
        else:
            self.SetGridText(text)
            self.library_gpf.GPF_GridSegUser.argtypes = [c_void_p, c_char_p, c_char_p,c_int]
            self.library_gpf.GPF_GridSegUser.restype  = c_int
            str_len=self.library_gpf.GPF_GridSegUser(self.hHandleGPF,table.encode(),self.RetBuff,1)
            ret = string_at(self.RetBuff, str_len)
        return ret.decode()  

    def POS(self,text,table=""):
        global IsPOSInit
        lock.acquire()
        if IsPOSInit ==0:
            self.library_gpf.GPF_POSInit.argtypes = [c_char_p]
            self.library_gpf.GPF_POSInit.restype  = c_int
            IsPOSInit = self.library_gpf.GPF_POSInit(self.POSData.encode())
        lock.release()

        if IsPOSInit == 0:
            return ""
        Ret=self.Segment(text,table)
        self.library_gpf.GPF_POS.argtypes = [c_void_p, c_char_p, c_char_p,c_int]
        self.library_gpf.GPF_POS.restype  = c_int
        str_len=self.library_gpf.GPF_POS(self.hHandleCRFPOS,Ret.encode(),self.RetBuff,1)
        ret = string_at(self.RetBuff, str_len)
        return ret.decode()
    #
    # Others:
    # Command="Context"/"Freq"
    # Number=1000/-1
    # Target="$Q"
    # Service=""
    # WinSize=20
    # Print="Lua"
    # Speedup=1
    def BCC(self,Query,**Others):
        Param=[]
        self.GetBCCQueryInfo(Others,Query,Param)
        return self.CallBCC(Param[0],Param[1])

    #
    # Others:
    # Web="Off"/"On"
    #  Structure=""/POS/Segment/Tree/Dependecy/Chunk
    # Table=""
    def Parse(self,text,**Others):
        Param=[]
        self.GetParseInfo(Others,Param)
        Structure=Param[0]
        IsWeb=Param[1]
        table=Param[2]
        if Structure == "Segment" and IsWeb == False:
            Ret=self.Segment(text,table)
            Words=Ret.split(" ")
            return json.dumps(Words,ensure_ascii=False)
        if Structure == "POS" and IsWeb == False:
            Ret=self.POS(text,table)
            Ret=Ret.strip(" ")
            Items=Ret.split(" ")
            return json.dumps(Items,ensure_ascii=False)
        JS=self.CallService(text,Structure)
        Ret=json.loads(JS)
        if isinstance(Ret,dict) and (Ret["ST"] == "Segment" or Ret["ST"] == "POS"or Ret["ST"] == "Chunk" ):
            RetEx=[]
            for i in range(len(Ret["Units"])):
                RetEx.append(Ret["Units"][i]+"/"+Ret["POS"][i])
            return json.dumps(RetEx,ensure_ascii=False)
        return JS

    def GetTable(self):
        self.GPFInit()                
        self.library_gpf.GPF_GetTable.argtypes = [c_void_p, c_char_p, c_int]
        self.library_gpf.GPF_GetTable.restype  = c_int
        str_len = self.library_gpf.GPF_GetTable(self.hHandleGPF, self.RetBuff, self.buf_max_size)
        if str_len != 0:
            ret = string_at(self.RetBuff, str_len)
            json_data = json.loads(ret.decode())
            return json_data
        return json.loads("{}")

    def GetIndexBCCInfo(self,Others,Param):
        Command="HZ"
        if "Structure" in Others:
            Command=Others["Structure"]
        Param.append(Command)

    def GetBCCQueryInfo(self,Others,Query,Param):
        Command=""
        if Query.find("\n") != -1:
            BCCQuery=Query
        else:
            Command="Freq"
        if "Command" in Others:
            Command=Others["Command"]

        Number=1000  
        if "Number" in Others:
            Number=Others["Number"]
        Target="$Q"
        if "Target" in Others:
            Target=Others["Target"]
        WinSize=20
        if "WinSize" in Others:
            WinSize=Others["WinSize"]
        Print=""
        if "Print" in Others:
            if Others["Print"] =="Lua":
                Print=Others["Print"]
            elif Others["Print"] =="Freq":
                Command="Freq"
            elif Others["Print"] =="Context":
                Command="Context"
            else:
                Command="Freq"
                Target=Others["Print"]

        if "Output" in Others:
            if Others["Output"] =="Lua":
                Print=Others["Output"]
            elif Others["Output"] =="Freq":
                Command="Freq"
            elif Others["Output"] =="Context":
                Command="Context"
            else:
                Command="Freq"
                Target=Others["Output"]

        Speedup=1
        if "Speedup" in Others:
            Speedup=Others["Speedup"]
        ContextNum=0
        if "ContextNum" in Others:
            ContextNum=Others["ContextNum"]

        if Command=="Context":
            if Query.find("{") != -1:
                BCCQuery="{}Context({},{},0)".format(Query,Number,WinSize)
            else:
                BCCQuery="{}{{}}Context({},{},0)".format(Query,Number,WinSize)
        if Command=="Freq":
            if Query.find("{") != -1:
                BCCQuery='{}Freq({},{},{})'.format(Query,Number,Target,ContextNum)
            else:
                BCCQuery='{}{{}}Freq({},{},{})'.format(Query,Number,Target,ContextNum)
            
        if Print=="Lua":
            BCCQuery+=Print
        if Speedup !=1:
            SpeedupCmd="Speedup({})".format(Speedup)
            BCCQuery+=SpeedupCmd
        Param.append(BCCQuery)
        Service=""
        if "Service" in Others:
            Service=Others["Service"]
        Param.append(Service)

    def GetParseInfo(self,Others,Parm):
        IsWeb=False
        if "IsWeb" in Others:
            IsWeb=Others["IsWeb"]
        if "Web" in Others:
            IsWeb=Others["Web"]
        
        table=""
        if "Table" in Others:
            table=Others["Table"]
        Structure="POS"        
        if "Structure" in Others:
            Structure=Others["Structure"]
        Parm.append(Structure)
        Parm.append(IsWeb)
        Parm.append(table)

    def GPFInit(self):
        global IsGPFInit
        lock.acquire()
        if IsGPFInit ==0:
            self.library_gpf.GPF_LatticeInit.argtypes = [c_void_p, c_char_p]
            self.library_gpf.GPF_LatticeInit.restype  = c_int
            IsGPFInit=self.library_gpf.GPF_DataInit(self.ConfigGPF.encode(), self.dataPath.encode('gbk', errors='strict'));
        lock.release()

        
    def ShowUnit(self,Unit,CheckDep):           
        DoctInfo=""
        V=self.GetUnitKVs(Unit,"USub")
        if len(V) == 0:
            return ""
        for i in range(len(V)):
            R=" ".join(self.GetUnitKV(V[i],Unit))
            Edge=self.GetWord(Unit)+" -> "+self.GetWord(V[i])+' [label="'+R+"\", color=blue]\n"
            if Edge not in CheckDep:
                DoctInfo+=Edge
                CheckDep[Edge]=1
            DoctInfo+=self.ShowUnit(V[i],CheckDep)
        return DoctInfo

    def GetShowStructType(self,Json):

        Struct=json.loads(Json)
        if isinstance(Struct,dict) and Struct.get("ST"):
            return "GPFStruct"
        Type="Tree"
        if isinstance(Struct,list) and len(Struct) >1 :
            if isinstance(Struct[0],list) and len(Struct[0]) == 3:
                Type="Graph"
            if isinstance(Struct[0],str) or isinstance(Struct[0],dict):
                Type="Seq"
        if isinstance(Struct,dict):
            if len(Struct) >1:
                for K,V in Struct.items():
                    if isinstance(V,int):
                        Type="Set"
                    else:
                        Type="Graph"
                    break
            else:    
                for K,V in Struct.items():
                    if isinstance(V,list) and len(V) >0 and isinstance(V[0],list):
                        Type="Graph"
                        break
        return Type

    def ShowStructure(self,Json="",Img="./gpf.png"):
        DotInfo=""
        Type=self.GetShowStructType(Json)
        if Type == "GPFStruct":
            self.AddStructure(Json)
            self.ShowGrid(Img,True,False)
            return
        if Type == "Graph":
            DotInfo=self.ShowGraph(Json)
        elif  Type == "Set":
            DotInfo=self.ShowCloud(Json,Img)
            return
        elif  Type == "Seq":
            DotInfo=self.ShowSeq(Json)
        elif  Type == "Tree":
            DotInfo=self.ShowTree(Json)

        Out=open("./tmp.dot","w",encoding="utf-8")
        print(DotInfo,file=Out)
        Out.close()
        Cmd=self.DotExe+" -Tpng "+" ./tmp.dot -o "+Img
        os.system(Cmd)
        os.remove("./tmp.dot")

    def UnitInfo(self,Unit):
        Ret=Unit
        Ret=Ret.replace("(","U")
        Ret=Ret.replace(")","")
        Ret=Ret.replace(",","_")
        Ret=Ret.replace("-","_")
        return Ret

    def ShowUnit(self,Unit,Img="./gpf.png"):
        Heade='''
    digraph Grid_modules{
     node [ fontname = "fangsong", fontsize = 12]; 
     fontname = "fangsong"
     '''
        if self.GetUnitKV(Unit,"Word") == 0:
            return
        Script=Heade+"\n"
        Script+=self.UnitInfo(Unit)+'[shape="egg",style="filled",label=" '+Unit+self.GetUnitKV(Unit,"Word")+' "]'+"\n"
        Atts=self.GetUnitKV(Unit)
        for K,Vs in Atts.items():
            if (K[0] == "U" or K[0] == "R") and len(K) > 5:
                continue    
            V=" ".join(Vs)            
            Script+=self.UnitInfo(K)+'[label=" '+V+' "]'+"\n"
            Script+=self.UnitInfo(Unit)+"->"+self.UnitInfo(K)+'[ label=" '+K+' "]'+"\n"

        Script+='}'+"\n"
        Out=open("./tmp.dot","w",encoding="utf-8")
        print(Script,file=Out)
        Out.close()
        Cmd=self.DotExe+" -Tpng "+" ./tmp.dot -o "+Img
        os.system(Cmd)
        os.remove("./tmp.dot")

    def ShowRelation(self,Img="./gpf.png"):
        self.ShowGrid(Img,True,True)

    def ShowGrid(self,Img="./gpf.png",IsShowRel=False,IsShowGrid=True):
        Heade='''
    digraph Grid_modules{
     node [ fontname = "fangsong", fontsize = 12]; 
     fontname = "fangsong"
     '''
        Script=Heade+"\n"
        Grid=self.GetGrid()
        ID=0
        for Col in Grid:
            ColHead='''
    subgraph cluster_Graph{}{{
     label=" {}: {} ";
      '''
            ColHead=ColHead.format(ID,ID,self.GetUnitKV(Col[0],"Word"))
            ColInfo=[]
            Script+=ColHead+"\n"
            for U in Col:
                if self.IsUnit(U,"Type=Char"):
                    Script+=self.UnitInfo(U)+'[style="filled", fillcolor="gray",label=" '+U+self.GetUnitKV(U,"Word")+' "]'+"\n"

                if self.IsUnit(U,"Type=Word"):
                    Script+=self.UnitInfo(U)+'[style="filled", fillcolor="Green",label=" '+U+self.GetUnitKV(U,"Word")+' "]'+"\n"
                if self.IsUnit(U,"Type=Phrase"):
                    Script+=self.UnitInfo(U)+'[style="filled", fillcolor="lightblue",label=" '+U+self.GetUnitKV(U,"Word")+' "]'+"\n"
                if self.IsUnit(U,"Type=Chunk"):
                    Script+=self.UnitInfo(U)+'[style="filled", fillcolor="Gold",label=" '+U+self.GetUnitKV(U,"Word")+' "]'+"\n"
                ColInfo.append(self.UnitInfo(U))
            Script+="->".join(ColInfo)+' [dir=none,color="white"]'+"\n"
            Script+='}'+"\n"
            ID+=1
        if not IsShowGrid:
            Script=Heade+"\n"
        if IsShowRel:
            for Col in Grid:
                for U in Col:
                    HeadUs=self.GetUnitKV(U,"USub")
                    for H in HeadUs:
                        R=self.GetUnitKV(H,U)
                        Rel=" ".join(R)
                        if not IsShowGrid:
                            Script+=self.GetWord(U)+"->"+self.GetWord(H)+'[ label=" '+Rel+' "]'+"\n"
                        else:
                            Script+=self.UnitInfo(U)+"->"+self.UnitInfo(H)+'[ label=" '+Rel+' "]'+"\n"
        Script+='}'+"\n"
        Out=open("./tmp.dot","w",encoding="utf-8")
        print(Script,file=Out)
        Out.close()
        Cmd=self.DotExe+" -Tpng "+" ./tmp.dot -o "+Img
        os.system(Cmd)
        os.remove("./tmp.dot")


    def Show(self,Json="",**Others):
        Param=[]
        self.GetShowInfo(Others,Param)
        if not Param[0] == "":
            Json=Param[0]
        IsShowGrid=Param[1]
        IsShowRelation=Param[2]
        Output=Param[3]
        Unit=Param[4]

        if Json == "":
            if Unit == "":
                self.ShowGrid(Output,IsShowRelation,IsShowGrid)
            else:
                self.ShowUnit(Unit,Output)
        else:
            self.ShowStructure(Json,Output)

    def GetShowInfo(self,Others,Param):
        Json=""
        if Others.get("Json"):
            Json=Others["Json"]
        IsShowGrid=True
        if "Grid" in Others:
            IsShowGrid=Others["Grid"]
        if "IsShowGrid" in Others:
            IsShowGrid=Others["IsShowGrid"]
        IsShowRelation=False
        if "IsShowRelation" in Others:
            IsShowRelation=Others["IsShowRelation"]
        if "Relation" in Others:
            IsShowRelation=Others["Relation"]
        Output="./gpf.png"
        if Others.get("Output"):
            Output=Others["Output"]

        Unit=""
        if Others.get("Unit"):
            Unit=Others["Unit"]
        Param.append(Json)
        Param.append(IsShowGrid)
        Param.append(IsShowRelation)
        Param.append(Output)
        Param.append(Unit)
    def GPFPersons(self):
        print("2023最佳进步奖：朱红同学")
        print("2023最佳进步奖：宋玉良同学")
        print("2023最佳贡献奖：王雨同学")
        print("2023最佳贡献奖：刘廷超同学")

    def GetJSUnitInfo(self,JS):
        Att=""
        if isinstance(JS,dict):
            for Word,Val in JS.items():
                Att+=Word
                if isinstance(Val,dict):
                    for K,V in Val.items():
                        if isinstance(V,list):
                            Att+=K+"（"+"｜".join(V)+"）"
                        if isinstance(V,int):
                            Att+=K+"（"+str(V)+"）"
                        if isinstance(V,str):
                            Att+=K+"（"+V+"）"
                elif isinstance(Val,str):
                    Att+=Word+"（"+str(Val)+"）"
        if isinstance(JS,str):
           ret=re.search('([^/]+)/([^/]+)',JS)
           if ret:
               Att=ret.group(1)+"（"+ret.group(2)+"）"
           else:
               Att=JS
        if isinstance(JS,int):
            Att=str(JS)

        return Att
            
    def DrawGraph(self,Json,Tag,Root=""):
        DoctInfo=""
        if isinstance(Json,str):
            if Root !=  "":
                DoctInfo+=Root+"->"+Json+'\n'
        if isinstance(Json,list):
            for Item in Json:
                if isinstance(Item,list) and len(Item) == 3 and isinstance(Item[0],str):
                    DoctInfo+=Item[0]+"->"+Item[1]+' [label=" '+Item[2]+' " ]\n'
                if isinstance(Item,list) and len(Item) == 3 and isinstance(Item[0],dict):
                    DoctInfo+=self.GetJSUnitInfo(Item[0])+"->"+self.GetJSUnitInfo(Item[1])+' [label=" '+self.GetJSUnitInfo(Item[2])+' " ]\n'

        if isinstance(Json,dict):
            for K,V in Json.items():
                if isinstance(V,list) and len(V) >0 and  isinstance(V[0],list):
                    for Tail in V:
                        if isinstance(Tail,list) and len(Tail) == 2 and  isinstance(Tail[0],dict):
                            DoctInfo+=K+"->"+self.GetJSUnitInfo(Tail[0])+' [label=" '+self.GetJSUnitInfo(Tail[1])+' " ]\n'
                        if isinstance(Tail,list) and len(Tail) == 2 and  isinstance(Tail[0],str):
                            DoctInfo+=K+"->"+Tail[0]+' [label=" '+Tail[1]+' " ]\n'
                if isinstance(V,list) and len(V) ==2 and  isinstance(V[0],str):
                        DoctInfo+=K+"->"+V[0]+' [label=" '+V[1]+' " ]\n'
                if isinstance(V,str) :
                        if not Tag.get(K):
                            Tag[K]=K
                        else:
                            Tag[K]=Tag[K]+"　"
                        DoctInfo+=Root+"->"+Tag[K]+'\n'
                        DoctInfo+=Tag[K]+"->"+V+'\n'
                if isinstance(V,dict):
                    for Rel,Tail in V.items():
                        if Root !=  "":
                            DoctInfo+=Root+"->"+K+' [label=" '+Rel+' " ]\n'
                        if isinstance(Tail ,str):
                            DoctInfo+=K+"->"+Tail+' [label=" '+Rel+' " ]\n'
                        if isinstance(Tail ,list):
                            for T in Tail:
                                DoctInfo+=K+"->"+T+' [label=" '+Rel+' " ]\n'
                        if isinstance(Tail ,dict):
                            for k,v in Tail.items():
                                if not Tag.get(k):
                                    Tag[k]=k
                                else:
                                    Tag[k]=Tag[k]+"　"
                                DoctInfo+=K+"->"+Tag[k]+' [label=" '+Rel+' " ]\n'
                                DoctInfo+=self.DrawGraph(v,Tag,Tag[k])
        return DoctInfo


    def DrawSeq(self,Json):
        DoctInfo=""
        if isinstance(Json,list):
            for i in range(len(Json)):
                NextInfo="->"
                if i == len(Json)-1:
                    NextInfo="\n"
                if isinstance(Json[i],str) or isinstance(Json[i],int):
                    DoctInfo+=str(self.GetJSUnitInfo(Json[i]))+NextInfo
                elif isinstance(Json[i],dict) :
                    DoctInfo+=self.GetJSUnitInfo(Json[i])+NextInfo
        return DoctInfo


    def DrawTree(self,Json,Tag,Root=""):
        DoctInfo=""
        if isinstance(Json,list):
            for i in range(len(Json)):
                if isinstance(Json[i],str) or isinstance(Json[i],int):
                    if Root == "":
                        if i <len(Json)-1:
                            DoctInfo+=str(Json[i])+"->"
                        else:    
                            DoctInfo+=str(Json[i])+"\n"
                    else:
                        DoctInfo+=Root+"->"+str(Json[i])+"\n"
                else:
                    DoctInfo+=self.DrawTree(Json[i],Tag,Root)
        elif isinstance(Json,dict):
            for K,V in Json.items():
                if not Tag.get(K):
                    Tag[K]=K
                else:
                    Tag[K]=Tag[K]+"　"
                if not Root == "":
                    DoctInfo+=Root+"->"+Tag[K]+"\n"
                
                if isinstance(V,str) or isinstance(V,int):
                    DoctInfo+=Tag[K]+"->"+str(V)+"\n"
                else:
                    DoctInfo+=self.DrawTree(V,Tag,Tag[K])
        return DoctInfo

    def ShowTree(self,Json):
        Head='''
        digraph g {
                node [fontname="fangsong"]
                rankdir=TD  
                '''
        Tail='}'
        Tag={}
        Script=""
        Script+=Head
        Script+=self.DrawTree(json.loads(Json),Tag)
        Script+=Tail
        return Script

    def ShowSeq(self,Json):
        Head='''
        digraph g {
                node [fontname="fangsong"]
                rankdir=LR  
                '''
        Tail='}'

        Script=""
        Script+=Head
        Script+=self.DrawSeq(json.loads(Json))
        Script+=Tail
        return Script


    def ShowCloud(self,Json,Output):
        wd=WordCloud(background_color="white",font_path="c:/windows/fonts/simyou.ttf")
        wd.generate_from_frequencies(json.loads(Json))
        wd.to_file(Output)


    def ShowGraph(self,Json):
        Head='''
        digraph g {
                node [fontname="fangsong"]
                edge [fontname="fangsong"]
                rankdir=TD  
                '''
        Tail='}'
        Script=""
        Tag={}
        Script+=Head
        Script+=self.DrawGraph(json.loads(Json),Tag)
        Script+=Tail
        return Script

    def AddSeq(self,Json):
        Struct=json.loads(Json)
        Txt=self.GetText()
        if isinstance(Struct,list):
            for Item in Struct:
                Word=""
                Att={}
                if isinstance(Item,str):
                    Word=Item
                    if Item.find("/") != -1:
                        (Word,POS)=Item.split("/")
                        if not POS =="":
                            Att["POS"]=POS
                elif isinstance(Item,dict):
                    if Item.get("Unit"):
                        Word=Item["Unit"]
                    else:
                        for Word,Att in Item.items():
                            break
                    if Item.get("Att"):
                        Att=Item["Att"]
                Pos=Txt.find(Word)        
                if Pos != -1:
                    Unit=self.AddUnit(Word,Pos+len(Word)-1)
                    for K,V in Att.items():
                        Val=""
                        if isinstance(V,str):
                            Val=V
                        elif isinstance(V,int):
                            Val=str(V)
                        elif isinstance(V,list):
                            Val=" ".join(V)
                        self.AddUnitKV(Unit,K,Val)
                    

    def AddTree(self,Json):
        Json=re.sub('[" : ,]',"",Json)
        Json=re.sub(r'\[',r"(",Json)
        Json=re.sub(r'\]',r")",Json)
        Json=re.sub(r'{',r"(",Json)
        Json=re.sub(r'}',r")",Json)
        Json='{"Type":"Tree","Units":["'+Json+'"]}'
        self.AddGridJS(Json)

    def Add2Grid(self,Txt,Head,Tail,Rel):
        Unit1=""
        Unit2="" 
        Pos=Txt.find(Head)        
        if Pos != -1: 
            Unit1=self.AddUnit(Head,Pos+len(Head)-1)
        Pos=Txt.find(Tail)        
        if Pos != -1:
            Unit2=self.AddUnit(Tail,Pos+len(Tail)-1)
        if Unit2 !="" and  Unit1 !="": 
            self.AddRelation(Unit1,Unit2,Rel)
            self.AddGridKV("URoot",Unit1)

    def AddGraph(self,Json):
        Struct=json.loads(Json)
        Txt=self.GetText()
        if isinstance(Struct,list):
            for Item in Struct:
                if isinstance(Item,list) and len(Item) == 3 and isinstance(Item[0],str) and   isinstance(Item[1],str) and   isinstance(Item[2],str) :
                    self.Add2Grid(Txt,Item[0],Item[1],Item[2])
        if isinstance(Struct,dict):
            for Head,Val in Struct.items():
                if isinstance(Val ,list) and len(Val ) >0 and  isinstance(Val [0],list):
                    for Tail in Val :
                        if isinstance(Tail,list) and len(Tail) == 2 and  isinstance(Tail[0],str):
                            self.Add2Grid(Txt,Head,Val[0],Val[1])            
                if isinstance(Val ,dict):
                    for R,Tail in Val.items():
                        if isinstance(Tail ,str):
                            self.Add2Grid(Txt,Head,Tail,R)           
                        if isinstance(Tail ,list):
                            for T in Tail:
                                self.Add2Grid(Txt,Head,T,R)       
    def InitGPF(self,Path):
        IdxedFile2Time={}
        ToIdxFile2Time={}
        TableFiles=[]
        FSAFiles=[]
        BCCFiles=[]
        Ret=self.GetIdxInfo(Path,IdxedFile2Time)
        self.dataPath=Path
        if len(IdxedFile2Time) >0 or Ret:
            return True
        self.GetFileInfo(Path,ToIdxFile2Time)
        if len(ToIdxFile2Time) == 0:
            return True
        PathIdx=Path+"Idx"
        self.dataPath=PathIdx
        self.GetIdxInfo(PathIdx,IdxedFile2Time)
        self.GetGPFFile(Path,IdxedFile2Time,TableFiles,FSAFiles,BCCFiles)
        if self.IsSame(ToIdxFile2Time,IdxedFile2Time):
            return True
        self.library_gpf.GPF_LatticeInit.argtypes = [c_void_p, c_char_p]
        self.library_gpf.GPF_LatticeInit.restype  = c_int

        self.library_gpf.GPF_DataInit(0,PathIdx.encode('gbk', errors='strict'));
        for File in TableFiles:
            print("Indexing Table",File)
            self.IndexTable(File)
            self.Write2IdxLog(PathIdx,File)
        for File in FSAFiles:
            print("Indexing FSA",File)
            self.IndexFSA(File)
            self.Write2IdxLog(PathIdx,File)
        if len(BCCFiles)>0:
            print("Indexing BCC")
            self.IndexBCC(BCCFiles)
            for File in BCCFiles:
                self.Write2IdxLog(PathIdx,File)
        return True
        
    def IsIdxedPath(self,Path):
        for root, dirs, files in os.walk(Path):
            for File in files:
                if File.find("IdxUnit.dat") != -1 or File.find("table.idx") != -1 or  File.find("fsa.idx") != -1:
                    return True
        return False
                
    def GetIdxInfo(self,Path,IdxedFile2Time):
        IdxLog = os.path.join(Path, self.g_IdxLog)
        if not  os.path.isfile(IdxLog):
            if self.IsIdxedPath(Path):
                return True
            return False
        In=open(IdxLog,"rt")
        for Line in In:
            Line=Line.strip()
            if Line =="":
                break
            Item=re.split("\t",Line)
            if len(Item)>1 and not IdxedFile2Time.get(Item[0]):
                IdxedFile2Time[Item[0]]={}
            for i in range(1,len(Item)):
                IdxedFile2Time[Item[0]][Item[i]]=1
        In.close()
        return True
    
    def GetFileInfo(self,Path,ToIdxFile2Time):
        for root, dirs, files in os.walk(Path):
            for File in files:
                full_path = os.path.join(root, File)
                TimeId=os.path.getmtime(full_path)
                if not ToIdxFile2Time.get(File):
                    ToIdxFile2Time[File]={}
                ToIdxFile2Time[File][str(TimeId)]=1
        return True
    
    def IsSame(self,ToIdxFile2Time,IdxedFile2Time):
        for File,IDs in ToIdxFile2Time.items():
            if not IdxedFile2Time.get(File):
                return False
            for Id in IDs:
                if not IdxedFile2Time[File].get(Id):
                    return False
        return True

    def GetGPFFile(self,Path,IdxedFile2Time,TableFiles,FSAFiles,BCCFiles):
        BCCFilesTmp=[]
        for root, dirs, files in os.walk(Path):
            for File in files:
                full_path = os.path.join(root, File)
                if IdxedFile2Time.get(File):
                    TimeId=os.path.getmtime(full_path)
                    if IdxedFile2Time[File].get(str(TimeId)) :
                        continue
                if self.IsFileFormat(full_path) == "Table":
                    TableFiles.append(full_path)
                elif self.IsFileFormat(full_path) == "FSA":
                    FSAFiles.append(full_path)
                else:
                    BCCFiles.append(full_path)

    def IsFileFormat(self,File):
        Ret="BCC"
        try:
            In=open(File,"rt")
            No=0
            for Line in In:
                Line=Line.strip()
                No+=1
                if No > 100:
                    break
                ret=re.search('^FSA ',Line)
                if ret:
                    Ret="FSA"
                    break
                ret=re.search('^Table ',Line)
                if ret:
                    Ret="Table"
                    break

            In.close()
        except:
            return Ret
        return Ret

    def Write2IdxLog(self,Path,File):
        IdxedFile2Time={}
        self.GetIdxInfo(Path,IdxedFile2Time)
        TimeId=os.path.getmtime(File)
        File=os.path.basename(File)
        if not IdxedFile2Time.get(File):
            IdxedFile2Time[File]={}
        IdxedFile2Time[File][str(TimeId)]=1

        IdxLog = os.path.join(Path, self.g_IdxLog)
        Out=open(IdxLog,"wt")
        for File,TimeIDs in IdxedFile2Time.items():
            print(File+"\t"+"\t".join(TimeIDs.keys()),file=Out)
        Out.close()

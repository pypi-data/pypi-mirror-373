function CreateTree(Query,IsR2L)
    local root = {lchild =nil,rchild = nil,parent=nil,Query = Query,Relation = "",ScriptAS="",Handle=""}
    CreateNode(root,IsR2L)
    return root
end 

function CreateNode(node,IsR2L)
	local Other,AS,Relation=SegAS(node.Query,IsR2L)
	if Other == "" then
		if AS == "" then
			if IsR2L == 1 then
				--任意+P[不含[]的复杂情况]
				Re="^(.+[^a-zA-Z-_])(%(?[a-zA-Z-_]+%[[^%[%]]+%]%)?)$"
				B,E,LEFT,r=string.find(node.Query,Re)
				if B == nil then
					--P[.*]+P[含[]的复杂情况]
					Re="^([^%]]+%])([%(%~%)%.]*[a-zA-Z-_]+%[.+%][%(%~%)%.]*)$"
					B,E,LEFT,r=string.find(node.Query,Re)
				end
				if B == nil then
					--非P[.*]+P[含[]的复杂情况]
					Re="^([^%]%[]+[^a-zA-Z-_%]%[])([a-zA-Z-_]+%[.+%][%(%~%)%.]*)$"
					B,E,LEFT,r=string.find(node.Query,Re)
				end
				if B ~= nil then
					B,E,Rel=string.find(LEFT,"(.)$")
					RELATION="Link"
					if Rel == "*" or Rel == "^" then
						RELATION=Rel
					end
					node.Query=r
					CreateNode(node,1)
				end
			end
		else
			node.ScriptAS,node.Handle=GetScriptAS(node.Query)
		end
		return
	end
	if IsR2L == 0 then 
		local lnode= {parent = node,lchild =nil,rchild =nil,Query = AS,Relation = "",ScriptAS="",Handle=""} 
		local rnode = {parent = node,lchild =nil,rchild =nil,Query = Other,Relation = "",ScriptAS="",Handle=""}
		lnode.ScriptAS,lnode.Handle=GetScriptAS(lnode.Query)
		node.lchild = lnode
		node.rchild = rnode
		node.Relation = Relation
		CreateNode(rnode,IsR2L)
	
	else
		local lnode= {parent = node,lchild =nil,rchild =nil,Query = Other,Relation = "",ScriptAS="",Handle=""} 
		local rnode = {parent = node,lchild =nil,rchild =nil,Query = AS,Relation = "",ScriptAS="",Handle=""}
		rnode.ScriptAS,rnode.Handle=GetScriptAS(rnode.Query)
		node.lchild = lnode
		node.rchild = rnode
		node.Relation = Relation
		CreateNode(lnode,IsR2L)
	end
end 

function GetScriptAS(Query)
	local ScriptAS=""
	local Handle=""
	if Query == nil or Query == "" then
		goto RET
	end

	Query,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner=GetASInfo(Query)
	--P HZs
	Re="^([a-zA-Z-_]+)([^%s\1-\127]+)$"
	B,E,POS,HZs=string.find(Query,Re)
	if B ~= nil then
		B,E,HZ=string.find(HZs,"^([%z\1-\127\194-\244][\128-\191]*)")
		HZ,HZs=Chin2Eng(HZ,HZs)
		ScriptAS=string.format('Handle%d=GetAS("|%s_%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,HZ,HZs,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		goto RET
	end

	--HZs P
	Re="^([^%s\1-\127]+)([a-zA-Z-_]+)$"
	B,E,HZs,POS=string.find(Query,Re)
	if B ~= nil then
		B,E,HZ=string.find(HZs,"([%z\1-\127\194-\244][\128-\191]*)$")
		HZ,HZs=Chin2Eng(HZ,HZs)
		ScriptAS=string.format('Handle%d=GetAS("%s_%s|","%s","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,HZ,POS,HZs,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		goto RET
	end

	--HZs
	Re="^([^%s\1-\127]+)$"
	B,E,HZs=string.find(Query,Re)
	if B ~= nil then
		-- B,E,HZ=string.find(HZs,"([%z\1-\127\194-\244][\128-\191]*)$")
		B,E,HZ=string.find(HZs,"^([%z\1-\127\194-\244][\128-\191]*)")
		HZ,HZs=Chin2Eng(HZ,HZs)
		ScriptAS=string.format('Handle%d=GetAS("<%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,HZ,HZs,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		goto RET
	end

	--P
	Re="^([a-zA-Z-_]+)$"
	B,E,POS=string.find(Query,Re)
	if B ~= nil then
		if lFix == '.' then
			ScriptAS=string.format('Handle%d=GetAS("%s|","%s","","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		elseif rFix == '.' then
			ScriptAS=string.format('Handle%d=GetAS("|%s","%s","%s","","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,rFix,lFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		else
			ScriptAS=string.format('Handle%d=GetAS("|%s","","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		end
		goto RET
	end
	
	--q[*HZs]
	Re="^([a-zA-Z_-]+)%[%*?([^%s\1-\127]+)%]$"	
	B,E,POS,HZs=string.find(Query,Re)
	if B ~= nil then
		B,E,HZ=string.find(HZs,"([%z\1-\127\194-\244][\128-\191]*)$")
		HZ,HZs=Chin2Eng(HZ,HZs)
		ScriptAS=string.format('Handle%d=GetAS("$%s_%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,HZ,HZs,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		goto RET
	end
	
	--q[*]
	Re="^([a-zA-Z_-]+)%[%*?%]$"	
	B,E,POS=string.find(Query,Re)
	if B ~= nil then
		ScriptAS=string.format('Handle%d=GetAS("$%s","","%s","%s","%s","%s","%s","%s","%s","%s")\n',HandleNo,POS,lFix,rFix,lFixinn,rFixinn,lBracket,rBracket,lBracketInner,rBracketInner)
		goto RET
	end

	--@
	Re="^@$"	
	B,E,POS=string.find(Query,Re)
	if B ~= nil then
		ScriptAS=""
		goto RET
	end

	
::RET::
	if ScriptAS == "" then
		Handle=string.format('Handle%d',HANDLENO)
	else
		Handle=string.format('Handle%d',HandleNo)
	end
	HandleNo=HandleNo+1
	return ScriptAS,Handle
end

function IsOK(Q3)
	B1,E1=string.find(Q3,"%[")
	B2,E2=string.find(Q3,"%]")
	local Ret=1
	if B1 ~=nil and B2 ~=nil then
		if B1 > B2 then
			Ret=0
		end
	end
	return Ret
end

function GetChunkInfo(InChunk)
	local Other=""
	local Relation=""
	if string.find(InChunk,"^%*.+%*$") then
		Relation="InChunk"
	elseif string.find(InChunk,".+%*$") then
		Relation="SameLeft"
	elseif string.find(InChunk,"^%*.+$") then	
		Relation="SameRight"
	else
		Relation="SameBoundary"
	end	
	Other=string.gsub(InChunk,"^[%*%s]+","")
	Other=string.gsub(Other,"[%*%s]+$","")
	return Other,Relation
end


function SegAS(Query,IsR2L)
	local Relation="Link"
	local Other=""
	local AS=""
	if Query == nil or  Query == "" then
		goto RET
	end
	for i=1,#REAS do
		B,E=string.find(Query,REAS[i])
		if B ~= nil then
			AS=Query
			goto RET
		end
	end	
	if IsR2L == 1 then
		--P[~[^HZ]HZs]
		Re="^([a-zA-Z-_%(%)]+)%[([%~%.%(%)]*)([\1-\127]*)([^\1-\127]+)%]([%(%)]?)$"
		B,E,Q1,Q2,Q3,Q4,Q5=string.find(Query,Re)
		if B ~= nil then
			B,E=string.find(Q3,"%](.*)%[")
			if B == nil then
				AS=Q1.."["..Q2.."*"..Q4.."]"..Q5
				Other=Q2..Q3..Q4
				Relation="SameBoundary"
				goto RET
			end
		end

		--P[~[^~]~]
		Re="^([a-zA-Z-_%(%)]+)%[([%~%.%(%)]*)(.*)([%~%.%(%)]*)%]([%(%)]?)$"
		B,E,Q1,Q2,Q3,Q4,Q5=string.find(Query,Re)
		if B ~= nil then
			if IsOK(Q3) == 1 then
				Relation="SameBoundary"
				AS=Q1.."["..Q2.."*"..Q4.."]"..Q5
				Other=Q2..Q3..Q4
				Other,Relation=GetChunkInfo(Other)
				goto RET
			end
		end

		
		--P HZs P
		Re="^([%~%.%(%)]*[a-zA-Z-_%(%)]+)%s*([^%s\1-\127]+)%s*([a-zA-Z-_%(%)]+[%~%.%(%)]*)$"
		B,E,Q1,Q2,Q3=string.find(Query,Re)
		if B ~= nil then
			Other=Q1..Q2
			AS=Q2..Q3
			Relation="ShareQuery"
			goto RET
		end

		--HZs P HZs
		Re="^([%~%.%(%)]*[^%s\1-\127]+)%s*([a-zA-Z-_%(%)]+)%s*([^%s\1-\127]+[%~%.%(%)]*)$"
		B,E,Q1,Q2,Q3=string.find(Query,Re)
		if B ~= nil then
			Other=Q1..Q2
			AS=Q2..Q3
			Relation="ShareTag"
			goto RET
		end
		
		for i=1,#RER2L do
			B,E=string.find(Query,RER2L[i])
			if B ~= nil then
				Other=string.sub(Query,1,B-1)
				AS=string.sub(Query,B,E)
				B,E,Sep=string.find(Other,"([%*%^])$")
				if B ~= nil then
					Other=string.sub(Other,1,B-1)
					Relation=Sep
				end
				goto RET
			end
		end	
	else
		for i=1,#REL2R do
			B,E=string.find(Query,REL2R[i])
			if B ~= nil then
				Other=string.sub(Query,E+1)
				AS=string.sub(Query,B,E)
				B,E,Sep=string.find(Other,"^([%*%^])")
				if B ~= nil then
					Other=string.sub(Other,1)
					Relation=Sep
				end
				goto RET
			end
		end	
	end

::RET::	
	Other=string.gsub(Other,"[%s%*%^]+$","")
	Other=string.gsub(Other,"^[%s%*%^]+","")
	return Other,AS,Relation
	
end


function CreateScriptR(Root)
    if Root.lchild then
        CreateScriptR(Root.lchild)  
    end

    if Root.lchild and Root.rchild then
		Root.ScriptAS=string.format('Handle%d=JoinAS(%s,%s,"%s")\n',HandleNo,Root.lchild.Handle,Root.rchild.Handle,Root.Relation)
		Root.Handle=string.format('Handle%d',HandleNo)
		HandleNo=HandleNo+1
		Script=Script..Root.rchild.ScriptAS
		Script=Script..Root.ScriptAS
	else
		Script=Script..Root.ScriptAS
    end
end

function CreateScriptL(Root)
    if Root.rchild then
        CreateScriptL(Root.rchild)  
    end

    if Root.lchild and Root.rchild then
		Root.ScriptAS=string.format('Handle%d=JoinAS(%s,%s,"%s")\n',HandleNo,Root.lchild.Handle,Root.rchild.Handle,Root.Relation)
		Root.Handle=string.format('Handle%d',HandleNo)
		HandleNo=HandleNo+1
		Script=Script..Root.lchild.ScriptAS
		Script=Script..Root.ScriptAS
	else
		Script=Script..Root.ScriptAS
    end
end


function GetPosInfo(BrackInfo,IsL2R)
	local Bracket=""
	local RE=BrackInfo
	if BrackInfo == nil then
		goto ERROR
	end
	Table={}
	if BrackInfo == nil or BrackInfo == "" then
		Bracket=""
	end
	if IsL2R == 0 then
		RE=string.reverse(BrackInfo)
	end

	Stop=0
	e=0
	while(Stop==0) do
		B,E=string.find(RE,"[%(%)]",e)
		if B == nil then
			Stop=1
		else
			l=string.sub(RE,1,B-1)
			Str =string.gsub(l,"[%(%)]"," ")
			table.insert(Table,GetPos(Str))
			e=E+1
		end
	end
	if #Table > 0 then
		if IsL2R == 1 then
			Bracket=table.concat(Table,",")
		else
			for i=1,#Table do
				Bracket=Bracket..Table[#Table-i+1]
				if i ~= #Table then
					Bracket=Bracket..","
				end
			end
		end
	end
::ERROR::
	return Bracket
end

function GetPos(Str)
	local Fix=string.gsub(Str,"~","~ ")
	Fix=string.gsub(Fix,"%.","%. ")
	Fix=string.gsub(Fix,"^%s","")
	Fix=string.gsub(Fix,"%s$","")
	Fix=string.gsub(Fix,"%s+"," ")
	local Pos=0
	for Space in string.gmatch(Fix,"%S") do
		Pos=Pos+1
	end
	return Pos
end

function GetBracketInfo(Query)
	local lBracket=""
	local rBracket=""
	local lBracketInner=""
	local rBracketInner=""
	Re="^([%~%.%(%)]*)[a-zA-Z_-]+%[([%~%.%(%)]*)%*?([%~%.%(%)]*)[^%s\1-\127]*%]([%~%.%(%)]*)$"
	local B,E,lFix,lFixInner,rFixInner,rFix=string.find(Query,Re)
	local lQuery,rQuery
	if B== nil then
		B,E,lQuery,rQuery=string.find(Query,"^([\1-\127]*)[^\1-\127]+([\1-\127]*)$")
		if B == nil then
			B,E,lQuery,rQuery=string.find(Query,"^([%~%.%(%)]*)[a-zA-Z%-%_]+([%~%.%(%)]*)$")
		end
	else
		lQuery=lFix
		rQuery=rFix
	end
	lBracket=GetPosInfo(lQuery,1)
	rBracket=GetPosInfo(rQuery,0)

	rBracketInner=GetPosInfo(rFixInner,1)
	lBracketInner=GetPosInfo(lFixInner,0)
	return lBracket,rBracket,lBracketInner,rBracketInner
end

function GetASInfo(Query)
	local QueryEx=""
	local lFix=""
	local rFix=""
	local lFixinn=""
	local rFixinn=""
	local lBracket=""
	local rBracket=""
	local lBracketInner=""
	local rBracketInner=""
	QueryEx=string.gsub(Query,"[%.%(%)~]","")
	Re="^([%~%.%(%)]*)[^%~%.%(%)]+([%~%.%(%)]*)$"
	B,E,lFix,rFix=string.find(Query,Re)
	if B == nil then
		Re="^[a-zA-Z_-]+%[([%~%.%(%)]*)%*?([%~%.%(%)]*)[^%s\1-\127]*%]$"
		B,E,lFixInner,rFixInner=string.find(Query,Re)
	end

	if lFix ~= nil then
		lFix=string.gsub(lFix,"[%(%)]","")
	else
		lFix=""
	end

	if rFix ~= nil then
		rFix=string.gsub(rFix,"[%(%)]","")
	else
		rFix=""
	end

	if lFixInner ~= nil then
		lFixInner=string.gsub(lFixInner,"[%(%)]","")
	else
		lFixInner=""
	end

	if rFixInner ~= nil then
		rFixInner=string.gsub(rFixInner,"[%(%)]","")
	else
		rFixInner=""
	end

	lBracket,rBracket,lBracketInner,rBracketInner=GetBracketInfo(Query)
	return QueryEx,lFix,rFix,lFixInner,rFixInner,lBracket,rBracket,lBracketInner,rBracketInner
end


function Replace(Inp)
	local Query=Inp
	Query=string.gsub(Query,"%s+"," ")
	Query=string.gsub(Query,"%s*[%*]+%s*","*")
	Query=string.gsub(Query,"%s*[%(]+%s*","(")
	Query=string.gsub(Query,"%s*[%)]+%s*",")")
	Query=string.gsub(Query,"%s+[%^]+%s+","^")
	Query=string.gsub(Query,"^[%s%*%^]+","")
	Query= string.gsub(Query,"[%s%*%^]+$","")
	Query=string.gsub(Query,"%s+%[%s+","[")
	Query=string.gsub(Query,"%s+%]%s+","]")
	Stop=0
	e=0
	while(Stop==0) do
		B,E=string.find(Query,"%s+",e)
		if B == nil then
			Stop=1
		else
			l=string.sub(Query,1,B-1)
			r=string.sub(Query,E+1)
			if string.find(l,"[a-zA-Z0-9]$") ~=nil and string.find(r,"^[a-zA-Z0-9]") ~=nil then
				Query=l.." "..r
			else
				Query=l.."#"..r
			end
			
			e=E+1
		end
	end
	Query=string.gsub(Query,"#","")
	return Query
end

	 
function Init(QueryExpress)
	B,E,Speedup=string.find(QueryExpress,"(Speedup%(.+%))")
	if B == nil then
		Speedup="Speedup(1)"
	end

	B,E,Query,Condition,Operation=string.find(QueryExpress,"(.+)%{(.*)%}([^%(%)]+%([^%(%)]+%))")	
	if B == nil then
		Operation="Context(10,0,100)"
		B,E,Query,Condition=string.find(QueryExpress,"(.+)%{(.*)%}")
		if B == nil then
			Condition=""
			Query=QueryExpress
		end	
	end
	Query=Replace(Query)

	local ASRE={}
	table.insert(ASRE,"[%~%.%(%)]*[a-zA-Z-_]+[%(%)]?[^%s\1-\127]+[%~%.%(%)]*")--P HZs
	table.insert(ASRE,"[%~%.%(%)]*[^%s\1-\127]+[a-zA-Z-_%(%)]+[%~%.%(%)]*")--HZs P
	table.insert(ASRE,"[%~%.%(%)]*[^%s\1-\127]+[%~%.%(%)]*")--HZs
	table.insert(ASRE,"[%~%.%(%)]*[a-zA-Z_-]+%[[%~%.%(%)]*%*?[%~%.%(%)]*[^%s\1-\127]*%][%~%.%(%)]*")--P[*HZ]
	table.insert(ASRE,"[%~%.%(%)]*[a-zA-Z-_]+[%~%.%(%)]*")--P
	table.insert(ASRE,"@")--@

	RER2L={}
	REL2R={}
	REAS={}
	for i=1,#ASRE do
		table.insert(RER2L,ASRE[i].."$")
		table.insert(REL2R,"^"..ASRE[i])
		table.insert(REAS,"^"..ASRE[i].."$")
	end
	return Query,Condition,Operation,Speedup
end

function GetOperation(Operation)
	Output=string.format('Ret=Output(Handle%d)\n',HandleNo)
	B,E,Op,Obj=string.find(Operation,"([^%(%)]+)%((.*)%)")
	if B == nil then
		Op=Operation
		Obj=""
	end
	if Op == "Context" then
		B,E,pPageSize,pWinSize,pPageNo=string.find(Obj,"([^%,]+)%,([^%,]+)%,(.*)")
		if B == nil then
			pPageNo="0"
			B,E,pPageSize,pWinSize=string.find(Obj,"([^%,]+)%,(.*)")
			if B == nil then
				pWinSize="20"
				B,E,pPageSize=string.find(Obj,"([^%,]+)")
				if B == nil then
					pPageSize="1000"
				end
			end
		end
		Operation=string.format('Handle%d=Context(Handle%d,%s,%s,%s)\n',HandleNo,HandleNo-1,pWinSize,pPageNo,pPageSize)
		Operation=Operation..Output
	elseif Op == "Freq" then
		B,E,pMaxNum,pObj,pContextNum=string.find(Obj,"([^%,]+)%,([^%,]+)%,(.*)")
		if B == nil then
			pContextNum="0"
			B,E,pMaxNum,pObj=string.find(Obj,"([^%,]+)%,(.*)")
			if B == nil then
				pObj="$Q"
				B,E,pMaxNum=string.find(Obj,"([^%,]+)")
				if B == nil then
					pMaxNum="1000"
				end
			end
		end
		Operation=string.format('Handle%d=Freq(Handle%d,"%s",%s)\n',HandleNo,HandleNo-1,pObj,pContextNum)
		Output=string.format('Ret=Output(Handle%d,%s)\n',HandleNo,pMaxNum)
		Operation=Operation..Output
	elseif Op == "Count" then
		Operation=string.format('Handle%d=Count(Handle%d,"%s")\n',HandleNo,HandleNo-1,Obj)
		Operation=Operation..Output
	elseif Op == "AddTag" or Op == "AddKV" then
		B,E,pTag,pVal=string.find(Obj,"([^%,]+)%,(.*)")
		if B == nil then
			B,E,pTag,pVal=string.find(Obj,"([^=]+)=%[(.*)%]")
			if B == nil then
				B,E,pTag,pVal=string.find(Obj,"([^=]+)=(.*)")
				if B == nil then
					pTag=""
					pVal=""
				end
			end
		end
		pVal=string.gsub(pVal,' ',';')
		pVal=string.gsub(pVal,',',';')
		Operation=string.format('AddTag("%s","%s")\nRet=GetTags(1)\n',pTag,pVal)
	elseif Op == "SpeedUp"then
		Operation=string.format('SpeedUp(%s)\n',Obj)
	elseif Op == "GetKV" or Op == "GetKVs"  then
		if Obj == "" then
			Operation=string.format('Ret=GetTags(1)\n')
		else
			Operation=string.format('Ret=GetTagVal("%s",1)\n',Obj)
		end
	elseif Op == "ClearTag" or  Op == "ClearKV" then
		if Obj == "" then
			Operation=string.format('Ret=ClearTag(%s)\n',Obj)
		else
			Operation=string.format('Ret=ClearTag("%s")\n',Obj)
		end
	elseif Op == "GetTags" or  Op == "GetKeys" then
		Operation=string.format('Ret=GetTags(1)\n')
	elseif Op == "GetTagVal" or Op == "GetValues" then
		Operation=string.format('Ret=GetTagVal("%s",1)\n',Obj)
	elseif Op == "AddLimit" then
		Operation=string.format('AddLimit(%s)\n',Obj)
	elseif Op == "ClearLimit" then
		Operation=string.format('ClearLimit()\n')
	elseif Op == "SetMax" then
		Operation=string.format('Ret=SetMax(%s)\n',Obj)
	elseif Op == "Lua" then
		if Obj == "" then
			Obj ="$Q"
		end
		B,E,pObj,pMaxNum,pContextNum=string.find(Obj,"([^%,]+)%,([^%,]+)%,(.*)")
		if B == nil then
			pContextNum="0"
			B,E,pObj,pMaxNum=string.find(Obj,"([^%,]+)%,(.*)")
			if B == nil then
				pMaxNum="1000"
				pObj=Obj
			end
		end
		Operation=string.format('Handle%d=Freq(Handle%d,"%s",%s)\n',HandleNo,HandleNo-1,pObj,pContextNum)
		Output=string.format('Ret=Output(Handle%d,%s)\n',HandleNo,pMaxNum)
		Operation=Operation..Output
	else	
		Output=string.format('\nRet=Output(Handle%d,%s)\n',HandleNo-1,1)
		Operation=Operation..Output
	end
	HandleNo=HandleNo+1
	return Operation
end

function IsFunc(Query)
	Cmd={"AddTag","AddKV","GetTags","GetKV","GetValue","GetTagVal","ClearKV","ClearTag","SetMax","SpeedUp","AddLimit","ClearLimit"}
	for K,V in ipairs(Cmd) do
		B,E=string.find(Query,V)
		if B ~= nil then
			return 1
		end		
	end
	return 0	
end

function Parser(Query,launguage)
	print(Query)
	Query=GB2UTF8(Query)
	
	HandleNo=0
	Script=""
	Operation="Context"
	Condition=""
	LEFT=""
	RELATION=""
	HANDLENO=0
	E2HZMap={}
	global_i=0

	local Query,Condition,Operation,Speedup=Init(Query)

	if Condition ~= "" then
		Condition="OriOn()\nCondition(\""..Condition.."\")\n"
	else
		Condition="OriOn()\n"
	end
	
	if IsFunc(Query) == 1 then
		Script=GetOperation(Query)
		Script=Script.."return Ret\n"
	else
		if launguage == 1 then
			Query=Eng2Chin(Query)
		end
		local rTree =CreateTree(Query,1)
		CreateScriptR(rTree) 
		HANDLENO=HandleNo-1
		if LEFT ~= nil and LEFT ~= ""  then
			local lTree=CreateTree(LEFT.."@",0)
			CreateScriptL(lTree)
		end
		Operation=GetOperation(Operation)
		Script=Script..Operation
		Script=Speedup.."\nOriOn()\n"..Condition..Script.."return Ret\n"
		
	end
	return UTF82GB(Script)
end

function split(str, delimiter)
    local result = {}
    local from = 1
    local delim_from, delim_to = string.find(str, delimiter, from)
    while delim_from do
        table.insert(result, string.sub(str, from, delim_from-1))
        from = delim_to + 1
        delim_from, delim_to = string.find(str, delimiter, from)
    end
    table.insert(result, string.sub(str, from))
    return result
end

function ReplaceE2C(Inp)
	local Query=Inp
	Query=string.gsub(Query,"%*"," * ")
	Query=string.gsub(Query,"%("," ( ")
	Query=string.gsub(Query,"%)"," ) ")
	Query=string.gsub(Query,"%^"," ^ ")
	Query=string.gsub(Query,"%["," [ ")
	Query=string.gsub(Query,"%]"," ] ")
	Query=string.gsub(Query,"%~"," ~ ")
	Query=string.gsub(Query,"%s+"," ")
	Query=string.gsub(Query,"%s+$","")
	Query=string.gsub(Query,"^%s+","")
	return Query 
end

function E2HZ(Items)
	Ret=Items
	B,E=string.find(Items,"[%[%]%*%^%(%)%~]")
	if B == nil then
		B,E=string.find(Items,"^[A-Z][A-Z]")
		if B == nil then
			Re="^[^%s\1*-\127]+$"
			B,E=string.find(Items,Re)
			if B == nil then
				 Ret=HZ2EngMap(Items)
			end
		end
	end
	return Ret
end


function Eng2Chin(Query)
	QueryE2C=Query
	Re="[^%s\1-\127]+"
	B,E=string.find(Query,Re)
    local result = {}
	if B == nil then
		Query=ReplaceE2C(Query)
		Items=split(Query, " ")
		for i=1,#Items do
			HZ=E2HZ(Items[i])
			table.insert(result, HZ)
		end
		QueryE2C=table.concat(result,"")
	end
	return QueryE2C
end

function HZ2EngMap(Word)
	H1=string.char(0xb2,0xa1+global_i)
	global_i=global_i+1
	H1=GB2UTF8(H1)
	E2HZMap[H1]=Word
	return H1
end


function Chin2Eng(HZ,HZs)
	RetHZ=HZ
	RetHZs=HZs
	if E2HZMap[HZ] == nil then
		return RetHZ,RetHZs
	end
	
	local EngWords={}
	if E2HZMap[HZ] ~= nil then
		RetHZ=E2HZMap[HZ]
	end
	
	B,E,HZ,Other=string.find(HZs,"^([%z\1-\127\194-\244][\128-\191]*)(.*)")
	while B~= nil do
		if E2HZMap[HZ] ~= nil then
			table.insert(EngWords,E2HZMap[HZ])
		else
			table.insert(EngWords,HZ)
		end
		B,E,HZ,Other=string.find(Other,"^([%z\1-\127\194-\244][\128-\191]*)(.*)")
	end
	if #RetHZs >0 then
		RetHZs=table.concat(EngWords," ")
	end
	return RetHZ,RetHZs
end

function Test()
	local Search="~JJ急啊(~){$1=[A,B]}"
	LuaScript=Parser(Search)
	print(LuaScript)
end

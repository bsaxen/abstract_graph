#========================================================================
# File:   translator.py 
# Author: Benny Saxen
# Date:   2025-07-29
#========================================================================

import json
from itertools import product

#==========================================
def readJasonFile(sourceFile):
#==========================================

    basicTriple = []

    memberIdToNameDict = {}
    memberIdToDescDict = {}
    familyIdToNameDict = {}
    memberToFamilyDict = {}
    familyIdToDescDict = {}
    familyIdToPaDict   = {}

    familyNameList = []
    familyDescDict = {}

    familyMemberDict = {}
    memberIdToDescDict = {}

    memberNameToAgidDict = {}

    paList = []

    famSizeDict = {}

    familyPADict = {}

    jsonSet = sourceFile.replace('.json','')
    dataSet = 'human-'+jsonSet+'.txt'
 
    fh = open(dataSet,'w')
    fh_ag = open('ag-'+jsonSet+'.txt','w')

    with open(sourceFile) as fd:
        data = json.load(fd)

        # Read Families
        nFamilies = 0
        nMembers = 0
        nCombinations = 0
        agid = 0
        for fam in data['families']:
            agid += 1
            nFamilies+=1
            fam_id  = fam['id']
            name  = fam['name']
            name = name.replace(' ','')
            familyNameList.append(name)
            desc  = fam['description']
            familyDescDict[name] = desc
            #familyMemberDict[name] = []

            familyIdToNameDict[fam_id] = name
            familyIdToDescDict[fam_id] = desc
            members = fam['members']
            fh.write('F#'+str(agid)+'#'+name+'#'+desc+'\n')
            #fh_families.write(name+','+desc+','+pa+'\n')

            fh.write('M#')
            k = 0
            memList = []
            family_agid = agid
            for mem in members:
                agid += 1
                fh.write('M#'+str(agid))
                k += 1
                nMembers += 1
                member_id = mem['id']
                member_name = mem['name']
                memList.append(member_name)
                member_name = member_name.replace(' ','')
                member_desc = mem['description']
                fammen = name+'-'+member_name
                fh.write('M#'+str(agid)+'#'+fammen+'#'+member_desc+'\n')
                memberIdToDescDict[member_id] = member_desc
                memberIdToNameDict[member_id] = member_name
                memberToFamilyDict[member_id] = name
                fh_ag.write(str(family_agid) + ' ' +str(agid) + '\n')

                memberNameToAgidDict[fammen] = agid


        # Read Rules and Combinations
        nRules = 0
        for rule in data['rules']:
            nRules+=1
            rule_id  = rule['id']
            families  = rule['familyIds'] # ON-OFF

            #print("==== Families in Rule ==== ")
            nFam = 0
            fh.write("================= R:")
            tempList = []
            for ffam in families:
                nname = familyIdToNameDict[ffam]
                tempList.append(nname)
            tempList.sort()
            jj = ' '.join(tempList)

            fh.write(jj+'\n')
            workDict = {}
            for fam in families:
                nFam += 1
                name = familyIdToNameDict[fam]
                workDict[name] = []

            combinations  = rule['combinations']

            #print("Combinations")
            #ncomb = 0

            #print(combinations)
            for comb in combinations:
                    #ncomb += 1
                    for fam in workDict:
                        workDict[fam].clear()
                    membersInCombination = comb['memberIds']
                    for mem in membersInCombination:
                        name = memberIdToNameDict[mem]
                        familyName = memberToFamilyDict[mem]
                        fammen = familyName+'-'+name
                        workDict[familyName].append(fammen)

                    res = list(product(*workDict.values()))
                    #print(workDict)
                    #sres = ''.join(res)
                    for combo in res:
                        nCombinations += 1
                        resDict = dict(zip(workDict.keys(), combo))
                        #sorted_items = sorted(resDict.items()) # sorted by key
                        sorted_items = sorted(resDict.items(), key=lambda x: x[1]) # sorted by value
                        agid += 1
                        fh.write('C#'+str(agid)+'#')

                        temps = 'C-'
                        for key,value in sorted_items:
                            temps += value+','

                        m = len(sorted_items)
                        #print(sorted_items)
                        k = 0
                        for key,value in sorted_items:
                            #print(f"{key}: {value}")
                            k += 1
                            member_agid = memberNameToAgidDict[value]
                            if k < m:
                                fh.write(value+',')
                            else:
                                fh.write(value+'\n')
                                
                            fh_ag.write(str(member_agid) + ' ' +str(agid) + '\n')
                                


    
    print("Families:  "+ str(nFamilies))
    print("Members:   "+ str(nMembers))
    print("Blockings: "+ str(nCombinations))
    
    fh.close()

    fh_ag.close()


    return
#========================================================================
def main():
#========================================================================   
    go = 1
    while(go == 1):
        prompter = 'TRANSLATOR >'
        command = input(prompter) 

        sp  = command.split(" ")
        n = len(sp)
        op = sp[0]

        if op == 'ex':
            exit()

        if op == 'he':
            help() 

        if op == 're':           
            sourceFile = 'data_250729.json'
            readJasonFile(sourceFile)

#========================================================================
#========================================================================
if __name__ == "__main__":
    main()
#========================================================================
#========================================================================
  

#========================================================================
# End Of File
#========================================================================
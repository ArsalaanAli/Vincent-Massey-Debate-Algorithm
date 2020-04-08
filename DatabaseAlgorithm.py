from random import *
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#Google Sheet Database Connection
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Debate_Data.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Vincent Massey Debate Database').sheet1
records = client.open('Vincent Massey Debate Database').get_worksheet(1)
#test = sheet.get_all_records()
#test2 = records.get_all_records()
if records.cell(2, 6).value.lower() != "yes":
    print("proceed not initiated on document")
    x = input("quit?")
    if x == 'y':
        quit()
#=================================================================================================#

#Team Class
class team:
    def __init__(this, ID, mem1, mem2, grade, dp, prev1, prev2):
        this.ID = ID
        this.mem1 = mem1
        this.mem2 = mem2
        this.grade = grade
        this.dp = dp
        this.prev = [0, 0]
        this.prev[0] = prev1
        this.prev[1] = prev2
    def printStats(this):
        print(this.ID, this.mem1, this.mem2, this.grade, this.dp, this.prevs)
    def teamName(this):
        return this.mem1
    def getPrev(this):
        return this.prev
print('sadasdasdasd')
#=================================================================================================#
#File I/O With Google Drive Database
teamId = sheet.col_values(1)
member1 = sheet.col_values(2)
member2 = sheet.col_values(3)
grade = sheet.col_values(4)
dp = sheet.col_values(5)
previous1 = sheet.col_values(6)
previous2 = sheet.col_values(7)
##print(teamId)
##print(member1)
##print(member2)
##print(grade)
##print(dp)
availableTeams = []
teams = []

#Available Teams Builder
for i in range(1, len(teamId)):
    temp = team(int(teamId[i]), member1[i], member2[i], int(grade[i]), int(dp[i]), previous1[i], previous2[i])
    availableTeams.append(temp)

##for t in availableTeams:
##   print(t.mem1)
#=================================================================================================#

#SET PREVS AND DP WHEN INPUTTING W/L


#=======================#
#Match Making Algorithm
#=======================#
done = []
leftOver = []
#                                                                    GETTING TEAM INPUT
def teamInput():
    global teams
    print("Available Teams")
    for t in availableTeams:
        print(t.mem1)
    print("use: 'add all' to add all teams")
    print("use: 'done' to finish selection")
    while True:
        inp = input("Team Name: ")
        if inp.lower() == "add all":
            teams = availableTeams
            break
        if inp.lower() == "done":
            break
        matchedTeam = findTeam(inp.lower())
        if matchedTeam == 0:
            continue
        elif matchedTeam in teams:
            print("Team has already been selected, cannot be added twice")
        else:
            print("Team has been added")
            teams.append(matchedTeam)

def findTeam(pt):
    for t in availableTeams:
        if pt == t.mem1.lower():
            return t
        elif pt == t.mem2.lower():
            return t
    else:
        print("Unable to find this team", pt)
        return 0
        
team1 = []
team2 = []
#                                                                       SORTING TEAMS FROM HIGHEST TO LOWEST DP
def teamSort():
    global teams
    teams.sort(key=lambda x: x.dp, reverse=True)
##for t in teams:
##    print(t.dp)
#                                                                       MAKING MATCHED TEAMS
#checks compatibility of teams
def notCompatible(t1, t2):
    if t2 in t1.getPrev():
        return True
    if t1 in t2.getPrev():
        return True
    return False

#MatchMaking algorithm
def makeMatch(valid, done, left):
    if len(left)<=1:
        return [True, done, left]
    for i in range(len(left)-1):
        if notCompatible(left[-1], left[-2-i]):
            continue
        newDone = done[:]
        newDone.append((left[-1], left[-2-i]))
        newLeft = left[:]
        del newLeft[-2-i]
        del newLeft[-1]
        x = makeMatch(True, newDone, newLeft)
        if x[0] == False:
            continue
        return x
    return [False, [], []]

##for t in done:
##    x, y = t
##    print(x.teamName(), "vs", y.teamName())

def prepTeams(done):
    global team1
    global team2
    for t in done:
        x, y = t
        side = randint(0, 1)
        if side:
            team1.append(x)
            team2.append(y)
        else:
            team1.append(y)
            team2.append(x)

def checkContinue():
    print("here are the matches")
    for i in range(len(team1)):
        print(team1[i].mem1, "vs", team2[i].mem1)
    continu = int(input(("would you like to continue with theses matches?\n1. continue\n2. exit")))
    if continu == 2:
        quit()
#                                                                       RECORD FILLING WITH MATCHED TEAMS
#finds newest section to start filling/getting records from, Done
marker = records.col_values(1)
def findIndex():
    print("finding index")
    for i in range(len(marker)-1, 0, -1):
        if marker[i] == 'start':
            return i+1
    return -1

    
#takes all matches made, and inputs them into records, Done
def fillRecords():
    index = findIndex()
    if index == -1:
        print("ERROR, INDEX NOT ABLE TO FIND START")
        quit()
    print("filling records")
    for i in range(len(team1)):
#        print(i, 'yes')
        records.update_cell(index+i, 2, team1[i].teamName())
        records.update_cell(index+i, 3, team2[i].teamName())
    records.update_cell(index+i+1, 1, "start")
    records.update_cell(index, 1, "old start")
    print("finished filling records")
    

#=======================#
#Debate Points Algorithm
#=======================#

#produces a list of lists, containing the winner on the first index, and a loser on the second index
def results():
    print("getting results")
    if records.cell(2, 6).value.lower() != "yes":
        print("proceed not initiated on document")
        quit()
    cell = records.find("start")
    startR = (cell.row)-1
    mark = records.col_values(1)
    govs = records.col_values(2)
    opps = records.col_values(3)
    wins = records.col_values(5)
    pendingMatches = []
    while True:
        startR-=1
        gov = govs[startR]
        opp = opps[startR]
        winner = int(wins[startR])
        gov = findTeam(gov.lower())
        opp = findTeam(opp.lower())
        print(gov.mem1, "v.s.", opp.mem1)
        if winner == 1:
            pendingMatches.append([gov, opp])
        elif winner == 2:
            pendingMatches.append([opp, gov])
        if mark[startR] == "old start":
            break
    return pendingMatches

def setPrev(tg, ts):
    tr = member1.index(tg.mem1)+1
    sheet.update_cell(tr, 7, tg.prev[0])
    sheet.update_cell(tr, 6, ts.mem1)

def getPrevs(teamg):
    for m in teamg:
        o, t = m
        setPrev(o, t)
        setPrev(t, o)

def dpCalc(tm, op, res):
    if tm.mem1 in member1:
        tr = member1.index(tm.mem1)
        tdp = int(dp[tr])
    else:
        print("error: Team", tm.mem1," not found")

 #   tr = tcell.row
  #  tdp = int(sheet.cell(tr, 5).value)
    if res == "won":
        tdp+=10
        if tm.dp < op.dp:
            tdp += 3
        else:
            tdp -= 4
    elif res == "lost":
        tdp+=3
    #other factors for increasing score go here
    return [tdp, tr]
def updateDp(matchResults):
    print("updating dp")
    for m in matchResults:
        a, b = m
        adp, ar = dpCalc(a, b, "won")
        bdp, br = dpCalc(b, a, "lost")
        dp[ar] = adp
        dp[br] = bdp
        #sheet.update_cell(ar, 5, adp)
        #sheet.update_cell(br, 5, adp)
    endRange = "E"+str(len(availableTeams)+1)
    newdps = sheet.range("E1:" + endRange)
    inc = 0
    for oldcell in newdps:
        oldcell.value = dp[inc]
        inc+=1
    sheet.update_cells(newdps)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def matchMakingAlgorithm():
    teamInput()
    if len(teams) == 0:
        print("no teams were selected \nending program")
        return
    teamSort()
    matches = makeMatch(True, [], teams)
    done = matches[1]
    leftOver = matches[2]#STILL HAVE TO DEAL WITH LEFT OVERS================================================================================
    prepTeams(done)
    checkContinue()
    fillRecords()

def recordKeep():
    matchResults = results()
    contin = input("would you like to continue?(y/n): ")
    if contin.lower() == 'n':
        quit()
    getPrevs(matchResults)
    updateDp(matchResults)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

###################
#END OF ALGORITHMS#
###################
print("which algorithm do you want to run?\n1. Match Making\n2. Record Keeping")
runAlg = int(input())
if runAlg == 1:
    matchMakingAlgorithm()
    print("Which action would you like to preform next\n1. Exit\n2. Record Keeping")
    nextRunAlg = int(input())
    if nextRunAlg == 2:
        recordKeep()
if runAlg == 2:
    recordKeep()
print("Exiting Program")

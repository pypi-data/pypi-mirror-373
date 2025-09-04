'''
Created on Jul 10, 2025

@author: ahypki
'''
import os
from sys import path
import sys
import importlib.metadata


from gima.utils.args import getArgString, isArgPresent
from gima.git.Settings import Settings
from gima.utils.Logger import Logger
from gima.db.Database import Database
# from gima.git.GitRepo import GitRepo
from gima.git.GitRepo import GitRepo
import requests
import os
from rich.console import Console
from rich.markdown import Markdown
from rich import print

database = Database()

def version():
    try:
        __version__ = importlib.metadata.version("gima")
        return str(__version__)
    except Exception as e:
        return ""

def prompt(gitRepo, readCommand = False):
    path = gitRepo.getPath()
    status = None
    if gitRepo.isClean():
        status = Logger.GREEN + 'clean' + Logger.GREEN_END
    else:
        status = Logger.WARNING + gitRepo.statusShort() + Logger.WARNING_END 
    
    prompt = Settings.PREFIX_LINE\
            + Logger.blue('gim > ') \
            + ('[' + (status).rjust(18, " ") + '] ' if status is not None else '') \
            + Logger.blue(str(path)) \
            + ' > '
    if readCommand:
        print(prompt, end = '', flush = True)
        return sys.stdin.readline().strip()
    else:
        Logger.logInfo(prompt, printLogLevel = False)

def printUsage():
    this_dir, this_filename = os.path.split(__file__)
    myfile = os.path.join(this_dir, 'usage.md') 
    file = open(myfile)
    s = file.read()
    
    s = s.replace('VERSION', 'version `' + version() + '`')

    console = Console()
    renderable_markup = Markdown(s)
#    Logger.logInfo(s, printLogLevel = False, printNewLine = False)
#    print(renderable_markup)
    console.print(renderable_markup)
#    console.print("Where there is a [bold cyan]Will[/bold cyan] there [u]is[/u] a [i]way[/i].")
    
def commitOneRepo(repo):
    while True:
        Logger.logInfo(Settings.SEPARATOR_NEXT_REPO, printLogLevel= False)
        gitRepo = GitRepo(repo)
        if gitRepo.isGitRepo():
            items, size = gitRepo.status()
            if (len(items) > 0):
                cmd = prompt(gitRepo, True)
                
                if cmd.startswith('cp '):
                    msg = cmd[2:].strip()
                    gitRepo.commit(msg)
                    gitRepo.push()
                elif cmd.startswith('c '):
                    msg = cmd[2:].strip()
                    gitRepo.commit(msg)
                elif cmd.startswith('a '):
                    if size > Settings.MAX_COMMIT_BYTES:
                        Logger.logWarn('Already added {} MB in this commit, skipping'.format(str(size / 1_000_000)))
                    else:
                        pattern = cmd[1:].strip()
                        gitRepo.add(pattern)
                elif cmd.startswith('i '):
                    pattern = cmd[1:].strip()
                    gitRepo.ignore(pattern)
                elif cmd.startswith('push'):
                    gitRepo.push()
                elif cmd.startswith('pull'):
                    gitRepo.pull()
                elif cmd.startswith('l'):
                    pass
                elif cmd.startswith('n'):
                    break
                elif cmd.startswith('q'):
                    # break checking other repos
                    return True
                else:
                    Logger.logError('Unknown command: {}'.format(cmd))
            else:
                prompt(gitRepo)
                break
        else:
            # not a git repo
            Logger.logError("Not a git repo in {}".format(repo))
            break
        
def commit():
    if isArgPresent("path"):
        commitOneRepo(getArgString("path", None))
    else:
        for repo in database.iterateRepos(getArgString('group', None)):
            if (os.path.exists(repo)):
                if commitOneRepo(repo):
                    break

def scan():
    currentDir = os.getcwd()
    if getArgString('path', None) is not None:
        currentDir = getArgString('path', None)
        
    foldersSkip = []
    foldersCountAll = 0
    foldersCountIgnored = 0
    foldersCountGitRepos = 0
    
    Logger.logInfo('Scanning {}...'.format(currentDir))
        
    for subdir, dirs, files in os.walk(currentDir):
        subdir = str(subdir)
        
        # statistics
        foldersCountAll += 1
        if (foldersCountAll == 100
            or foldersCountAll == 1000 
            or foldersCountAll % 10000 == 0):
            Logger.logInfo("{} folders scanned, {} ignored, {} already tracking".format(foldersCountAll, foldersCountIgnored, foldersCountGitRepos))
        
        # check if folder was checked already
        skip = False
        for ign in foldersSkip:
            if subdir.startswith(ign):
                # logDebug('Already checked ' + subdir)
                skip = True
                break
        if skip:
            continue
                    
        # check if the folder is ignored in the database
        if database.isIgnored(subdir):
            gitRepo = GitRepo(subdir)
            if gitRepo.isGitRepo():
                foldersSkip.append(subdir)
                foldersCountIgnored += 1
            # logDebug('Ignored in database ' + subdir)
            continue
            
        gitRepo = GitRepo(subdir)
        if gitRepo.isGitRepo():
            subdir = str(gitRepo.getPath())
            if subdir not in foldersSkip and not database.isRepoPresent(subdir):
            #     logInfo("Git repo in {} is ignored".format(subdir))
            # else:
                Logger.logInfo("{} > [A]dd/[I]gnore/ignore [R]ecursivelly/[S]kip for now".format(Logger.blue(subdir)))
                cmd = sys.stdin.readline().strip()
                if cmd.lower() == "a":
                    database.addRepo(subdir)
                elif cmd.lower() == "i":
                    database.ignore(subdir)
                elif cmd.lower() == "r":
                    database.ignoreAll(subdir)
                elif cmd.lower() == "s":
                    pass
            else:
                foldersCountGitRepos += 1

            foldersSkip.append(str(subdir))
    Logger.logInfo("{} folders scanned, {} ignored, {} already tracking".format(foldersCountAll, foldersCountIgnored, foldersCountGitRepos))
    
def clone():
    host = getArgString('url', None)
    token = getArgString('token', None)

    # Page through repository search endpoint until we stop getting data
    page = 0
    repositories = []
    r = requests.get("{}/api/v1/repos/search?limit=50&page={}&token={}".format(host, page, token))
    while len(r.json()["data"]):
        repositories.extend(r.json()["data"])
        page = page + 1
        r = requests.get("{}/api/v1/repos/search?limit=50&page={}&token={}".format(host, page, token))

    # Loop through each repository returned, cloning it over SSH
    for repository in repositories:
        Logger.logInfo(repository["full_name"], printLogLevel=False)
        # Logger.logInfo(repository["ssh_url"] + ", repos/" + repository["full_name"])
        # Repo.clone_from()

def group():
    if isArgPresent("path"):
        groupOneRepo(getArgString("path", None))
    else:
        Logger.logWarn('Iterating over all repos. Add groups with +group and remove groups with -group', printLogLevel=False)
        for repo in database.iterateRepos(getArgString('group', None)):
            if groupOneRepo(repo):
                break

def groupOneRepo(repoPath):
    repo = database.getRepo(repoPath)
    prompt = Settings.PREFIX_LINE\
            + Logger.blue('gim > ') \
            + Logger.blue(str(repoPath)) \
            + (' > current groups: ' + Logger.GREEN + ', '.join(repo['groups']) + Logger.GREEN_END) \
            + ' > '
    
    print(prompt, end = '', flush = True)
    newGroups = sys.stdin.readline().strip()
    for g in newGroups.split():
        g = g.strip()
        if len(g) > 0:
            if g.startswith('+'):
                database.addGroup(repoPath, g[1:])
            elif g.startswith('-'):
                database.removeGroup(repoPath, g[1:])
            elif g == 'q':
                return True
    
    repo = database.getRepo(repoPath)
    prompt = Settings.PREFIX_LINE\
            + Logger.blue('gim > ') \
            + Logger.blue(str(repoPath)) \
            + (' > current groups: ' + Logger.GREEN + ', '.join(repo['groups']) + Logger.GREEN_END)
    print(prompt, flush = True)
    return False
       
def main():
    if isArgPresent('verbose'):
        Logger.DEBUG = True
    
    if (isArgPresent('summary')):
        database.printSummary()
    elif (isArgPresent('ignore')):
        database.ignore(getArgString('ignore', None))
    elif (isArgPresent('ignore-all')):
        database.ignoreAll(getArgString('ignore-all', None))
    elif (isArgPresent('commit') or isArgPresent('c')):
        commit()
    elif (isArgPresent('scan') or isArgPresent('s')):
        scan()
    elif (isArgPresent('clone')):
        clone()
    elif (isArgPresent('group') or isArgPresent('g')):
        group()
    elif (isArgPresent('help') or isArgPresent('h')):
        group()
    else:
        printUsage()
        
    Logger.logInfo('Finished!')
    
if __name__ == '__main__':
    main()
'''
Created on Jul 10, 2025

@author: ahypki
'''
import json
import os
from pathlib._local import PosixPath

from gima.utils.Logger import Logger


class Database:
    __database_path = PosixPath('~/.gima.json').expanduser()
    
    __initiated = False
    __data = None
    
    def __init__(self):
        if (self.__initiated):
            return
        
        self.__initiated = True
        Logger.logDebug('Reading gim database {}'.format(self.__database_path))
        
        self.__data = {}
        if os.path.isfile(self.__database_path):
            with open(self.__database_path, 'r') as file:
                file_content = file.read()
                if len(file_content.strip()) > 0:
                    with open(self.__database_path, 'r') as file:
                        self.__data = json.load(file)
            
    def getRepo(self, path):
        for gitRepo in self.__data['gitRepos']:
            if gitRepo['path'] == path:
                return gitRepo
        return None
    
    def addGroup(self, path, group):
        repo = self.getRepo(path)
        repo['groups'].append(group)
        self.save()
        
    def removeGroup(self, path, group):
        repo = self.getRepo(path)
        if group in repo['groups']:
            repo['groups'].remove(group)
            self.save()
            
    def iterateRepos(self, group):        
        repos = [];
        if 'gitRepos' in self.__data:
            for gitRepo in self.__data['gitRepos']:
                if group is not None:
                    # checking if the git repo in in the given group
                    if group in gitRepo['groups']:
                        repos.append(gitRepo['path'])
                else:
                    repos.append(gitRepo['path'])
        return repos
    
    def printSummary(self):       
        Logger.logDebug('gim summary:')
        
        # repositories
        for gitRepo in self.__data['gitRepos']:
            groups = ''
            for g in gitRepo['groups']:
                groups += (', ' if len(groups) > 0 else '') + str(g)
            Logger.logDebug("\t\tRepository: " + gitRepo['path'] + " (" + groups + ")")
            
        # ignored paths
        for ign in self.__data['ignorePaths']:
            Logger.logDebug("\t\tIgnored: " + ign)
        for ign in self.__data['ignoreSubPaths']:
            Logger.logDebug("\t\tIgnored: " + ign)
            
    def isRepoPresent(self, testPath):
        if 'gitRepos' in self.__data:
            for gitRepo in self.__data['gitRepos']:
                if gitRepo['path'] == testPath:
                    return True
        return False
    
    def isIgnored(self, testPath):
        if 'ignorePaths' in self.__data:
            for ign in self.__data['ignorePaths']:
                if ign == testPath:
                    return True
        if 'ignoreSubPaths' in self.__data:
            for ign in self.__data['ignoreSubPaths']:
                if ign == testPath or testPath.startswith(ign):
                    return True
        return False

    def save(self):
        with open(self.__database_path, 'w', encoding='utf-8') as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)
        Logger.logDebug('Saved gim database {}'.format(self.__database_path))
        
    def addRepo(self, repo):
        if 'gitRepos' not in self.__data:
            self.__data['gitRepos'] = []
        if repo not in self.__data['gitRepos']:
            repoJson = {}
            repoJson['path'] = repo
            repoJson['groups'] = []
            repoJson['groups'].append('1')
            self.__data['gitRepos'].append(repoJson)
            Logger.logInfo("{} added to database".format(Logger.blue(repo)))
            self.save()
    
    def ignore(self, ignoreDir):
        if ignoreDir not in self.__data['ignorePaths']:
            self.__data['ignorePaths'].append(ignoreDir)
            Logger.logInfo("{} added to ignored folders".format(ignoreDir))
            self.save()
            
    def ignoreAll(self, ignoreDir):
        if ignoreDir not in self.__data['ignoreSubPaths']:
            self.__data['ignoreSubPaths'].append(ignoreDir)
            Logger.logInfo("{} added to ignored folders (and all its subfolders)".format(ignoreDir))
            self.save()
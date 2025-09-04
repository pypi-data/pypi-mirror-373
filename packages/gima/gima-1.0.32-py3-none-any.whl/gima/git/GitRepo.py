'''
Created on 15-06-2013

@author: ahypki
'''
from fileinput import filename
import fnmatch
import os
from pathlib._local import Path, PurePosixPath

import pygit2
from pygit2.enums import FileStatus
from pygit2.repository import Repository

from gima.git.Settings import Settings
from gima.utils.regex import matches, isNumber
from gima.utils.Logger import Logger
from gima.utils.io import linux_cmd

import re


class GitRepo:
    __path = None
    
    def __init__(self, path):
        self.__path = path
        
    def add(self, pattern):
        if matches(pattern.strip(), '[0-9\\-\\s]+'):
            self.addByIndices(pattern)
        else:
            self.addByWildcards(pattern)
    
    def ignore(self, pattern):
        if matches(pattern.strip(), '[0-9\\-\\s]+'):
            self.ignoreByIndices(pattern)
        else:
            self.ignoreByWildcards(pattern)
            
    def addByIndices(self, pattern):
        if (isNumber(pattern)):
            toAdd = int(pattern)
            i = 1
            items, size = self.status()
            for filename, code in items:
                if (i == toAdd):
                    self.addFile(filename)
                    break
                i += 1
        elif '-' in pattern:
            fromTo = pattern.split('-')
            fromIdx = int(fromTo[0])
            toIdx = int(fromTo[1])
            addedBytes = 0
            i = 1
            items, size = self.status()
            for filename, code in items:
                if (i >= fromIdx and i <= toIdx):
                    if self.addFile(filename):
                        addedBytes += os.path.getsize(self.__path + '/' + filename)
                i += 1
                if addedBytes > Settings.MAX_COMMIT_BYTES:
                    Logger.logWarn("Already added {} MB, breaking adding more".format(str(addedBytes / 1_000_000)))
                    break
                
    def ignoreByIndices(self, pattern):
        if (isNumber(pattern)):
            toAdd = int(pattern)
            i = 1
            items, size = self.status()
            for filename, code in items:
                if (i == toAdd):
                    self.ignoreFile(filename)
                    break
                i += 1
        elif '-' in pattern:
            fromTo = pattern.split('-')
            fromIdx = int(fromTo[0])
            toIdx = int(fromTo[1])
            i = 1
            items, size = self.status()
            for filename, code in items:
                if (i >= fromIdx and i <= toIdx):
                    self.ignoreFile(filename)
                i += 1
    
    def addByWildcards(self, pattern):
        items, size = self.status()
        addedBytes = 0
        for filename, code in items:
            if (code == FileStatus.INDEX_NEW 
                or code == FileStatus.WT_NEW
                or code == FileStatus.WT_DELETED
                or code == FileStatus.WT_MODIFIED):
                if fnmatch.fnmatch(filename, pattern):
                    if self.addFile(filename):
                        addedBytes += os.path.getsize(self.__path + '/' + filename)
                    if addedBytes > Settings.MAX_COMMIT_BYTES:
                        Logger.logWarn("Already added {} MB, breaking adding more".format(str(addedBytes / 1_000_000)))
                        break
    
    def ignoreByWildcards(self, pattern):
        items, size = self.status()
        for filename, code in items:
            if (code == FileStatus.INDEX_NEW 
                or code == FileStatus.WT_NEW
                or code == FileStatus.WT_DELETED
                or code == FileStatus.WT_MODIFIED):
                if fnmatch.fnmatch(filename, pattern):
                    self.ignoreFile(filename)
        
    def toString(self, code):
        if code == FileStatus.WT_MODIFIED:
            return "MODIFIED"
        elif code == FileStatus.WT_NEW:
            return "??"
        elif code == FileStatus.INDEX_NEW:
            return "NEW"
        elif code == FileStatus.WT_DELETED:
            return "DELETED"
        elif code == FileStatus.INDEX_DELETED:
            return "DELETED"
        elif code == FileStatus.WT_RENAMED:
            return "RENAMED"
        else:
            return str(code)
    
    def addFile(self, filename):
        if os.path.exists(self.__path + '/' + filename):
            repo = Repository(self.__path)
            cwd = os.getcwd()
            if len(cwd) > len(repo.path.replace('.git/', '')):
                cwd = cwd.replace(repo.path.replace('.git/', ''), '')
            else:
                cwd = ''
            repo.index.add((cwd + '/' if len(cwd) > 0 else '') + filename)
            repo.index.write()
            return True
        return False
        
    def ignoreFile(self, filename):
        with open(self.__path + '/.gitignore', 'a') as content_file:
            content_file.write('\n')
            content_file.write(filename)
    
    def commit(self, msg):
        repo = Repository(self.__path)
        
        cwd = os.getcwd()
        if len(cwd) > len(repo.path.replace('.git/', '')):
            cwd = cwd.replace(repo.path.replace('.git/', ''), '')
        else:
            cwd = ''
        
        # adding all modified files
        # repo.index.add_all() - SUPER slow!
        items, size = self.status()
        for filename, code in items:
            if (code == FileStatus.INDEX_NEW 
                # or code == FileStatus.WT_NEW
                or code == FileStatus.WT_DELETED
                or code == FileStatus.WT_MODIFIED):
                    if os.path.exists(self.__path + '/' + filename):
                        repo.index.add((cwd + '/' if len(cwd) > 0 else '') + filename)
                    else:
                        repo.index.remove((cwd + '/' if len(cwd) > 0 else '') + filename)
        
        repo.index.write()
        tree = repo.index.write_tree()
        author = pygit2.Signature(repo.config.__getitem__('user.name'), 
                                  repo.config.__getitem__('user.email'))
        committer = pygit2.Signature(repo.config.__getitem__('user.name'), 
                                     repo.config.__getitem__('user.email'))
        if repo.is_empty:
            repo.create_commit(
            "HEAD",
            author,
            committer,
            msg,
            tree,
            [],
        )
        else:
            ref = repo.head.name
            parents = [ repo.head.target ]
            repo.create_commit(
                ref,
                author,
                committer,
                msg,
                tree,
                parents,
            )
        
    def isGitRepo(self):
        try:
            repo = Repository(self.__path)
            # items = repo.status().items()
            return True
        except Exception as e:
            return False
        
    def status(self, printToScreen = True):
        
        # INFO: it simply does not work if the working tree is large, it takes hours and crashes eventually
        # repo = Repository(self.__path)
        # items = repo.status().items()
        # i = 1
        # size = 0
        # for filename, code in items:
        #     if printToScreen:
        #         print(Settings.PREFIX_LINE + ('[' + str(i) + ']').rjust(5, " ")
        #               + ' ' 
        #               + self.toString(code).rjust(10, " ")
        #               + ' ' 
        #               + filename
        #               + ' [' + str(i) + ']')
        #         i += 1
        #     if (code == FileStatus.INDEX_NEW 
        #         # or code == FileStatus.WT_NEW
        #         # or code == FileStatus.WT_DELETED
        #         or code == FileStatus.WT_MODIFIED):
        #         try:
        #             size += os.path.getsize(self.__path + '/' + filename)
        #         except Exception as e:
        #             pass
        
        # ... I have to use CLI instead
        items = []
        i = 1
        size = 0
        for line in linux_cmd('git status -sb -uall', self.__path, False):
            if not line.startswith('##'):
                code = FileStatus.INDEX_NEW
                codeStr = line[:2].strip()
                if (codeStr == '??'):
                    code = FileStatus.WT_NEW
                elif codeStr == 'A':
                    code = FileStatus.INDEX_NEW
                elif codeStr == 'M' or codeStr == 'AM':
                    code = FileStatus.WT_MODIFIED
                elif codeStr == 'D':
                    code = FileStatus.WT_DELETED
                elif codeStr == 'R' or codeStr == 'RM':
                    code = FileStatus.WT_RENAMED
                else:
                    Logger.logWarn('Unimplemented file status ' + codeStr)
                filename = line[3:]
                if filename.startswith('"'):
                    filename = filename[1:-1]
                items.append([filename, code])
                if printToScreen:
                    print(Settings.PREFIX_LINE + ('[' + str(i) + ']').rjust(5, " ")
                          + ' ' 
                          + self.toString(code).rjust(10, " ")
                          + ' ' 
                          + filename
                          + ' [' + str(i) + ']')
                    i += 1
                if (code == FileStatus.INDEX_NEW 
                    # or code == FileStatus.WT_NEW
                    # or code == FileStatus.WT_DELETED
                    or code == FileStatus.WT_MODIFIED):
                    try:
                        size += os.path.getsize(self.__path + '/' + filename)
                    except Exception as e:
                        pass
        return items, size
    
    def push(self):
        try:
            # logger.info("Pushing changes to git")
            repo = Repository(self.__path)
            remote = "origin"
            branch = "refs/heads/" + repo.head.shorthand
            sshcred = pygit2.Keypair('git',
                                       Path('~/.ssh/id_rsa.pub').expanduser(),
                                       Path('~/.ssh/id_rsa').expanduser(),
                                       '')
            repo.crendentals = sshcred
            # credentials = pygit2.UserPass(userName, password)
            callbacks = pygit2.RemoteCallbacks(credentials=sshcred)
            repo.remotes[remote].push(['+' + branch], callbacks=callbacks)
            
            Logger.logInfo('gim > ' + Logger.GREEN + str(self.__path) + Logger.GREEN_END + ' > '
                + ' [' + Logger.GREEN + 'Push OK' + Logger.GREEN_END + ']')
        except Exception as e:
            try:
                linux_cmd('git push', self.__path, False)
            except Exception as e:
                Logger.logError(e)
            
    def isClean(self):
        # repo = Repository(self.__path)
        # items = repo.status().items() # NOTE this is useless for large repos
        # if len(items) == 0:
        #     return True
        # else:
        #     return False
        
        for line in linux_cmd('git status -sb -uall', self.__path, False):
            if not line.startswith('##'):
                return False
        return True
    
    def statusShort(self):
        if self.isClean():
            return "clean"
        else:
            try:
                repo = Repository(self.__path)
                upstream_head = repo.revparse_single('origin/HEAD')
                local_head    = repo.revparse_single('HEAD')
            
                diff = repo.ahead_behind(local_head.id, upstream_head.id)
                if diff[0] > 0:
                    return "ahead " + str(diff[0])
                elif diff[1] > 0:
                    return "behind " + str(diff[1])
                else:
                    status = "modified"
                    items, size = self.status(printToScreen = False)
                    sizeMB = size / 1_000_000
                    return status + ", " + ("{:.1f}".format(sizeMB)) + " MB"
            except Exception as e:
                return "modified"
            
    def getPath(self):
        repo = Repository(self.__path)
        return PurePosixPath(repo.path).parent
    
    def pull(self):
        try:
            linux_cmd('git pull', self.__path, False)
        except Exception as e:
            Logger.logError(e)
    
    
    

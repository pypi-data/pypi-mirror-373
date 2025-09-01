'''
2019 Bjoern Annighoefer
'''
import os,shutil
from datetime import datetime

class Backupper():
    def __init__(self,backupSourceDirs=[],backupDestinationDir='./backup',maxBackups=10):
        self.backupSourceDirs = backupSourceDirs
        self.backupDestinationDir = backupDestinationDir
        self.maxBackups = maxBackups
        
        
    def CreateBackup(self):
        #create a new directory within the backup path
        #create the backup dir if it does not exist
        if(not os.path.isdir(self.backupDestinationDir)):
            os.makedirs(self.backupDestinationDir)
        #build log folder name from current date
        now = datetime.now() # current date and time
        backupBasename = now.strftime("%Y-%m-%d_%H_%M_%S")
        n = 0
        #check if there is already a backup for that second
        while(os.path.isdir(os.path.join(self.backupDestinationDir,"%s_%05d"%(backupBasename,n)))):
            n+=1
        self.currentBackupDir = os.path.join(self.backupDestinationDir,"%s_%05d"%(backupBasename,n))
        
        #remove old backups, if limit is exceeded
        existingBackupDirs = []
        for name in os.listdir(self.backupDestinationDir): 
            existingBackupDir = os.path.join (self.backupDestinationDir, name)   
            if os.path.isdir(existingBackupDir):
                existingBackupDirs.append(existingBackupDir)
                
        nExistingBackupDirs = len(existingBackupDirs)
        nEntriesToDelete = max([nExistingBackupDirs-self.maxBackups+1,0]) #+1 for the newly created one
        if 0 < nEntriesToDelete:
            existingBackupDirs = sorted(existingBackupDirs)
            for i in range(nEntriesToDelete):
                shutil.rmtree(existingBackupDirs[i])
            nExistingBackupDirs -= nEntriesToDelete
        
        #on for the current log
        os.makedirs(self.currentBackupDir)
        nExistingBackupDirs += 1;
        
        for backupSourceDir in self.backupSourceDirs:
            if(os.path.isdir(backupSourceDir)):
                backupDestDir = os.path.basename(backupSourceDir)
                backupDestPath = os.path.join(self.currentBackupDir,backupDestDir)
                shutil.copytree(backupSourceDir,backupDestPath)
            else:
                print("warning: Should backup %s, but path was not found."%(backupSourceDir))
        
        print('Backup ready! (path: %s)'%(self.currentBackupDir))
import asyncio
import os
import posixpath  
import re
from bs4 import BeautifulSoup
from typing import Literal
import utils  

class PapaCambridgeDownloader():
    class Level():
        def __init__(self, LINK: str, TITLE: str):
            self.link = LINK
            self.title = TITLE
            self.FoundSubjects = []

    class Subject():
        def __init__(self, LINK: str, TITLE: str, _LEVEL: "PapaCambridgeDownloader.Level", SubjectCode: str):
            self.link = LINK
            self.title = TITLE
            self.level = _LEVEL
            self.SubjectCode = SubjectCode
            self.FoundSessions = []

    class Session():
        def __init__(self, LINK: str, TITLE: str, _SUBJECT: "PapaCambridgeDownloader.Subject", Year: str, Month: str):
            self.link = LINK
            self.title = TITLE
            self.subject = _SUBJECT
            self.Year = Year
            self.Month = Month
            self.FoundPapers = []

    class Paper():
        def __init__(self, LINK: str, TITLE: str, _SESSION: "PapaCambridgeDownloader.Session", PaperNum, Type: str):
            self.link = LINK
            self.title = TITLE
            self.session = _SESSION
            self.PaperNum = PaperNum
            self.Type = Type
        
    def __init__(self):
        self.BaseURL = "https://pastpapers.papacambridge.com/"
        self.FoundLevels = []

    async def main(self): 
        pass

    async def GetLevelsData(self, Force=False) -> list[Level]:
        """Fetches the main assessment levels (IGCSE, A-level, etc.). Saves to .FoundLevels"""
        if self.FoundLevels and not Force:
            print("Already have Levels list")
            return self.FoundLevels
        self.LevelDataSource = await utils.GetWebPageSource(self.BaseURL)
        self.LevelDataSoup = BeautifulSoup(self.LevelDataSource, "html.parser")

        self.FoundLevels = []
        for link in self.LevelDataSoup.find_all("a"):
            href = link.get('href')
            if href and str(href).startswith("papers/caie/"):
                expression = r'.*/([^/]+)/?$'
                match = re.search(expression, str(href).rstrip('/'))
                if match:
                    NAME = match.group(1)
                    URL = posixpath.join(self.BaseURL, href)
                    if NAME:
                        _LevelData = self.Level(URL, NAME)
                        self.FoundLevels.append(_LevelData)
        return self.FoundLevels
    
    async def GetSubjectsList(self, _Level: Level, Force=False) -> list[Subject]:
        """Fetches the subject list for the selected level. Saves to the _Level obj"""
        if _Level.FoundSubjects and not Force:
            print("Already have Subjects list")
            return _Level.FoundSubjects
        
        _Level.FoundSubjects = []

        self.SubjectDataSource = await utils.GetWebPageSource(_Level.link)
        self.SubjectDataSoup = BeautifulSoup(self.SubjectDataSource, "html.parser")

        for link in self.SubjectDataSoup.find_all("a"):
            href = link.get('href')
            if href and str(href).startswith("papers/caie/"):
                # Case insensitive match to prevent string casing mismatches
                extractor = r'(?:.*?)-(.*?)-(\d{4})'
                match = re.search(extractor, str(href), re.IGNORECASE)
                if not match:
                    continue
                Name = match.group(1)
                Code = match.group(2)
                URL = posixpath.join(self.BaseURL, href)
                _SubjectData = self.Subject(URL, Name, _Level, Code)
                _Level.FoundSubjects.append(_SubjectData)
        return _Level.FoundSubjects

    async def GetSessionsList(self, _Subject: Subject, Force=False) -> list[Session]:
        """Fetches the session list (Years/Months) for the selected subject. Saves to the _Subject obj"""
        if _Subject.FoundSessions and not Force:
            print("Already have Sessions list")
            return _Subject.FoundSessions
        
        _Subject.FoundSessions = []

        self.SessionDataSource = await utils.GetWebPageSource(_Subject.link)
        self.SessionDataSoup = BeautifulSoup(self.SessionDataSource, "html.parser")

        for link in self.SessionDataSoup.find_all("a"):
            href = link.get('href')
            if href and str(href).startswith("papers/caie/"):
                extractor = r'(?:.*?)-(.*?)-(\d{4})-(\d{4})-(.*$)'
                match = re.search(extractor, str(href), re.IGNORECASE)
                if not match:
                    continue
                Name = match.group(1)
                Year = match.group(3)
                Months = match.group(4)

                URL = posixpath.join(self.BaseURL, href)
                _SessionData = self.Session(URL, Name, _Subject, Year, Months)
                _Subject.FoundSessions.append(_SessionData)
        return _Subject.FoundSessions

    async def GetPapersList(self, _Session: Session, Force=False) -> list[Paper]:
        """Fetches the actual paper PDF download links for a specific session. Saves to the _Session obj"""
        if _Session.FoundPapers and not Force:
            print("Already have Papers list")
            return _Session.FoundPapers
        
        _Session.FoundPapers = []

        self.PaperDataSource = await utils.GetWebPageSource(_Session.link)
        self.PaperDataSoup = BeautifulSoup(self.PaperDataSource, "html.parser")

        for link in self.PaperDataSoup.find_all("a"):
            href = link.get('href')
            if href and str(href).startswith("papers/caie/"):
                extractor = r'(?:.*?)-(.*?)-(\d{4})-(\d{4})-(.*$)' 
                match = re.search(extractor, str(href), re.IGNORECASE)
                if not match:
                    continue
                Type = match.group(3)
                Number = match.group(4)
                URL = posixpath.join(self.BaseURL, href)
                Filename = posixpath.basename(URL)

                _PaperData = self.Paper(URL, Filename, _Session, Number, Type)
                _Session.FoundPapers.append(_PaperData)
        return _Session.FoundPapers

async def MainTester(): # simple tester function.
    import random
    import pickle
    PC = PapaCambridgeDownloader()
    try:
        while True:
            levels = await PC.GetLevelsData()
            for level in levels:
                print(f"Found Level: {level.title}: {level.link}")

            subjects = []
            while not subjects:
                selected_level = random.choice(levels)
                print(f"\nSelected {selected_level.title} at random...")
                subjects = await PC.GetSubjectsList(selected_level, True)
                
            for subject in subjects:
                print(f"    Found Subject: {subject.title} ({subject.SubjectCode})")

            Sessions = []
            while not Sessions:
                selected_subject = random.choice(subjects)
                print(f"\nSelected {selected_subject.title} at random...")
                Sessions = await PC.GetSessionsList(selected_subject, True)
                
            for session in Sessions:
                print(f"    Found Session: {session.title} ({session.Year} - {session.Month})")
                

            Papers = []
            while not Papers:
                selected_session = random.choice(Sessions)
                print(f"\nSelected {selected_session.title} at random...")
                Papers = await PC.GetPapersList(selected_session, True)
                
            for paper in Papers:
                print(f"    Found Paper: {paper.title} {paper.PaperNum} {paper.Type}") 
    except BaseException:
        print("User Exit")
if __name__ == "__main__":
    asyncio.run(MainTester())

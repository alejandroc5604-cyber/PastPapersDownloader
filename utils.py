import os
import re
import asyncio
from typing import Literal
from itertools import batched
from bs4 import BeautifulSoup
from rich.panel import Panel
import keyboard
from playwright.async_api import async_playwright

class PickFromList:
    def __init__(self, OptionsList, UpdateTo):
        self.OptionsList = OptionsList
        self.selected_index = 0
        self.ChunkSize = min(16, len(self.OptionsList)) if OptionsList else 1
        self.Chunked_list = list(batched(OptionsList, self.ChunkSize)) if OptionsList else []
        self.UpdateTo = UpdateTo

    def generate_menu_renderable(self, title=None) -> Panel:
        if not self.OptionsList:
            return Panel("No entries available.", title="Selection Menu")
        
        lines = []
        batch_num = self.selected_index // self.ChunkSize
        relative_index = self.selected_index % self.ChunkSize
        
        if batch_num > len(self.Chunked_list) - 1:
            batch_num = len(self.Chunked_list) - 1
            
        for idx, item in enumerate(self.Chunked_list[batch_num]):
            if idx == relative_index:
                lines.append(f"[blue] > [bold blue]{item}[/bold blue] [/blue]")
            else:
                lines.append(f"  {item}")
                
        menu_content = "\n".join(lines)
        if not title:
            title = "Select Option [Use Arrow Keys & Enter]"
        return Panel(menu_content, title=title)

    async def Pick(self):
        if not self.OptionsList:
            return ("EMPTY", -1, None)

        keys_to_check = ["up", "down", "enter"]
        
        while True:
            self.UpdateTo.update(self.generate_menu_renderable())
            
            event = await asyncio.to_thread(keyboard.read_event)
            if event.event_type == keyboard.KEY_DOWN and event.name in keys_to_check:
                
                if event.name == "up":
                    if self.selected_index > 0:
                        self.selected_index -= 1
                        
                elif event.name == "down":
                    if self.selected_index < len(self.OptionsList) - 1:
                        self.selected_index += 1
                        
                elif event.name == "enter": 
                    if keyboard.is_pressed("ctrl"):
                        return ("CTRL-ENTER", self.selected_index, self.OptionsList[self.selected_index])
                    return ("ENTER", self.selected_index, self.OptionsList[self.selected_index])

            await asyncio.sleep(0.05)


def Sorter(SubjectCode, Year, Month: str, Course: Literal["IGCSE", "ALevel", "OLevel"], SortingString="", basepath=None):
    """Builds a path based on the paper data and safely sets up folders."""
    if Course not in ["IGCSE", "ALevel", "OLevel"]:
        raise ValueError('Invalid Subject Course; Must be of ["IGCSE", "ALevel", "OLevel"]')

    # Fixed: Prevent function from dropping out early when using default empty string
    if not SortingString:
        SortingString = "$COURSE$/$CODE$/$YEAR$/$MONTH$"
    
    for code, replacement in [
        ("$COURSE$", str(Course)),
        ("$CODE$", str(SubjectCode)),
        ("$YEAR$", str(Year)),
        ("$MONTH$", str(Month))
    ]:
        if code in SortingString:
            SortingString = SortingString.replace(code, replacement)
            
    if basepath:
        path = basepath
    else:
        path = os.getcwd()
        
    path = os.path.join(path, SortingString)
    
    os.makedirs(path, exist_ok=True)
    return path


async def GetWebPage(URL, XPATH=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_load_state()
        if XPATH:
            XPATH_waiter = page.locator(f"xpath={XPATH}")
            await XPATH_waiter.wait_for(state="visible")

        pagecontent = await page.content()
        await page.close()
        return pagecontent


async def GetSubjectListIGCSE():
    """Return a list of all the subjects and the set URLS for IGCSE level."""
    extracted_subjects = []
    mainpageurl = "https://pastpapers.papacambridge.com/papers/caie/igcse"
    MainPage = await GetWebPage(mainpageurl, "/html/body/div[14]/div/form/div/div/div[2]/div[1]/div[3]/div[2]/h1")
    soup = BeautifulSoup(MainPage, "html.parser")
    for link in soup.find_all("a"):
        href = link.get('href')
        if href:
            if not str(href).startswith("papers/caie/"):
                continue
            m = re.search(r'igcse-(.*?)-(\d{4})', href)
            if not m:
                continue
            name = m.group(1).replace("-", " ").title()
            code = m.group(2)
            url = mainpageurl.replace("papers/caie/igcse", "") + str(href).replace(" ", "")
            extracted_subjects.append((name, code, url))
            
    return extracted_subjects


async def GetYearExamsFromSubjectURL(subjectURL):
    """Checks the page for the year past papers."""
    PageSource = await GetWebPage(subjectURL)
    soup = BeautifulSoup(PageSource, "html.parser")
    found_years = []
    mainpageurl = "https://pastpapers.papacambridge.com/papers/caie/igcse"
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            if not str(href).startswith("papers/caie/"):
                continue
            m = re.search(r"igcse-(.*?)-(\d{4})-(\d{4})-(.*$)", href)
            if not m:
                continue
            name = m.group(1)
            code = m.group(2)
            year = m.group(3)
            months = m.group(4)
            link = mainpageurl.replace("papers/caie/igcse", "") + str(href).replace(" ", "")

            found_years.append((name, code, year, months, link))
    return found_years


async def GetYearExamsFromYearMonthURL(yearmonthURL):
    """Gets the papers from selected year."""
    downloadURLbasepath = "https://pastpapers.papacambridge.com"
    PageSource = await GetWebPage(yearmonthURL) 
    soup = BeautifulSoup(PageSource, "html.parser")
    found_papers = []
    
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            if not str(href).startswith("download_file.php?"):
                continue

            extractor = r"\b(\d{4})_([a-z]\d+)_([a-z]{2})(?:_(\d+))?\b"
            match = re.search(extractor, href.strip())
            
            if not match:
                continue
                
            code = match.group(1)
            month = match.group(2)      
            doctype = match.group(3)   
            paper_num = match.group(4) if match.group(4) else ""
            download_link = downloadURLbasepath + "/" + href
            filename = href.split("/")[-1]
            
            found_papers.append((code, month, doctype, paper_num, download_link, filename))
            
    return found_papers
